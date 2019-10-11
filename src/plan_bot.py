import re

from google.cloud import firestore
from praw.exceptions import APIException

from matching import RuleStrategy, Strategy
from reddit_util import standardize


def footer(post):
    return (
        f"\n\n"
        # Horizontal line above footer
        "\n***\n"
        # Disclaimer
        f"This bot was created independently by volunteers. [Join us!](https://my.elizabethwarren.com/page/s/web-volunteer) "
    )


def _plan_links(plans):
    return "\n".join(
        ["[" + plan["display_title"] + "](" + plan["url"] + ")  " for plan in plans]
    )


def build_response_text_plan_cluster(plan_record, post):
    """
    Create response text with plan summary when plan is actually a plan cluster
    """

    return (
        f"Senator Warren has quite a number of plans for that!"
        f"\n\n"
        # Links to learn more about the plan cluster
        f"Learn more about her plans for {plan_record['display_title']}:"
        f"\n\n"
        f"{ _plan_links(plan_record['plans'])}"
        f"{footer(post)}"
    )


def build_response_text_pure_plan(plan_record, post):
    """
    Create response text with plan summary
    """

    return (
        f"Senator Warren has a plan for that!"
        f"\n\n"
        f"{plan_record['summary']}"
        f"\n\n"
        # Link to learn more about the plan
        f"Learn more about her plan: [{plan_record['display_title']}]({plan_record['url']})"
        f"{footer(post)}"
    )


def build_response_text(plan_record, post):
    if plan_record.get("is_cluster"):
        return build_response_text_plan_cluster(plan_record, post)
    return build_response_text_pure_plan(plan_record, post)


def build_no_match_response_text(potential_plan_matches, post):
    if potential_plan_matches:
        return (
            f"I'm not sure I have an exact match for you! "
            f"Here are the plans that seem most relevant:"
            f"\n\n"
            f"{ _plan_links(match['plan'] for match in potential_plan_matches[:8])}"
            f"\n\n"
            f"Or I can show you my full list of her plans if you reply with"
            f"\n\n"
            f"```"
            f"!WarrenPlanBot show me the plans"
            f"```"
            f"\n\n"
            f"{footer(post)}"
        )
    else:
        return (
            f"I'm not sure exactly which plan you're looking for, "
            f"and I'm not feeling confident enough in any of my guesses to tell you about them! ':("
            f"\n\n"
            f"I can show you my full list of her plans if you reply with"
            f"\n\n"
            f"```"
            f"!WarrenPlanBot show me the plans"
            f"```"
            f"\n\n"
            f"Or please kindly rephrase? ':D"
            f"{footer(post)}"
        )


def build_all_plans_response_text(plans, post):
    pure_plans = list(filter(lambda p: not p.get("is_cluster"), plans))

    response = (
        f"Here's the full list of plans Sen. Warren has released that I know about:"
        f"\n\n"
        f"|[{pure_plans[0]['display_title']}]({pure_plans[0]['url']})|[{pure_plans[1]['display_title']}]({pure_plans[1]['url']})|[{pure_plans[2]['display_title']}]({pure_plans[2]['url']})|"
        f"\n"
        f"|:-:|:-:|:-:|"
        f"\n"
    )
    for i, plan in enumerate(pure_plans[3:], start=3):
        response += f"|[{plan['display_title']}]({plan['url']})"
        if (i + 1) % 3 == 0:
            response += "|\n"

    response += f"\n\n" f"{footer(post)}"

    return response


def build_help_response_text(plans, post):
    return """I’m the WarrenPlanBot. If Elizabeth Warren has a plan, I can help you find it!

You can call me like this:  
`!WarrenPlanBot [plan_topic]`  
and I’ll reply with the plan she has for that.

For example, if you wanted to learn about Elizabeth’s plan for immigration reform, you could write  
`!WarrenPlanBot immigration reform`

You can even be a little more conversational if you’d like, and say  
`!WarrenPlanBot what is her plan for ending private prisons?`

I’ll do my best to find the correct plan, but sometimes I have to guess, which means I might make mistakes (I’m just a bot!). I’ll get better, though, as I learn more about the topics that matter to you most 😄

To see my full list of Elizabeth’s plans, you can use the command: `!WarrenPlanBot show me the plans`  
To display this help: `!WarrenPlanBot help`
For advanced usage: `!WarrenPlanBot advanced help`

I hope to see you around!

***

This bot was created independently by volunteers. [Join us!](https://my.elizabethwarren.com/page/s/web-volunteer)
Have another question or run into any problems?  [Send a report](https://www.reddit.com/message/compose?to=WarrenPlanBotDev&subject=BotReport&message=Issue with help response).  
"""

def build_advanced_response_text(plans, post):
    return """I’m the WarrenPlanBot. If Elizabeth Warren has a plan, I can help you find it!

If you start your message with `-p` or `--parent` like this:
`!WarrenPlanBot --parent [plan_topic]`,
I'll reply directly to the parent message.

To see my full list of Elizabeth’s plans, you can use the command: `!WarrenPlanBot show me the plans`
To display basic help: `!WarrenPlanBot help`
To display this advanced usage: `!WarrenPlanBot advanced help`

***

This bot was created independently by volunteers. [Join us!](https://my.elizabethwarren.com/page/s/web-volunteer)
Have another question or run into any problems?  [Send a report](https://www.reddit.com/message/compose?to=WarrenPlanBotDev&subject=BotReport&message=Issue with help response).
"""


def reply(post, reply_string: str, parent=False, send=False, simulate=False):
    """
    :param post: post to reply on
    :param reply_string: string to reply with
    :param send: whether to send an actual reply to reddit
    :param simulate: whether to simulate sending an actual reply to reddit
    :return: did_reply – whether an actual or simulated reply was made
    """

    if parent and hasattr(post, 'parent'):
        post = standardize(post.parent())

    if simulate:
        print(f"[simulated] Bot replying to {post.type}: {post.id}")
        return True
    if send:
        print(f"Bot replying to {post.type}: {post.id}")
        post.reply(reply_string)
        return True

    print(f"Bot would have replied to {post.type}: {post.id}")


def process_post(
    post,
    plans,
    posts_db,
    post_ids_processed=None,
    send=False,
    simulate=False,
    skip_tracking=False,
    matching_strategy=Strategy.lsa_gensim_v2,
):
    if post_ids_processed is None:
        post_ids_processed = {}

    print(f"Processing post {post.type}: {post.id}")

    # Make sure we don't reply to a post we've already processed
    if post.id in post_ids_processed:
        return

    # Never try to reply if a post is locked
    if post.locked:
        skip_reason = "post_locked"
    # Never reply to a deleted post
    elif not post.author:
        skip_reason = "no_author"
    # Make sure we're not replying to ourself
    elif "warrenplanbot" in post.author.name.lower():
        skip_reason = "own_post"
    # Ensure it's a post where someone summoned us
    elif not re.search("!warrenplanbot", post.text, re.IGNORECASE):
        skip_reason = "trigger_not_found"
    else:
        skip_reason = None

    if skip_reason:
        post_record = create_db_record(
            post, processed=True, skipped=True, skip_reason=skip_reason
        )
        if not skip_tracking:
            posts_db.document(post.id).set(post_record)
        return

    post_text, options = process_flags(get_trigger_line(post.text))

    match_info = (
        RuleStrategy.request_help(plans, post_text, post=post)
        or RuleStrategy.request_plan_list(plans, post_text, post=post)
        or RuleStrategy.match_display_title(plans, post_text, post=post)
        or matching_strategy(plans, post_text, post=post)
    )

    match = match_info.get("match")
    operation = match_info.get("operation")
    plan_confidence = match_info.get("confidence")
    plan = match_info.get("plan", {})
    potential_matches = match_info.get("potential_matches")
    plan_id = plan.get("id")

    # Create partial db entry from known values, placeholder defaults for mutable values
    # Mark post as processed _before_ we reply to prevent double-posting
    post_record = create_db_record(
        post, match, plan_confidence, plan_id, processed=True
    )

    if not skip_tracking:
        posts_db.document(post.id).set(post_record)

    operations_map = {
        'all_the_plans': {
            'response': build_all_plans_response_text
        },
        'help': {
            'response': build_help_response_text
        },
        'advanced_help': {
            'response': build_advanced_response_text
        }
    }

    post_record_update = {}

    # If plan is matched with confidence, build and send reply
    if match:
        print("plan match: ", plan_id, post.id, plan_confidence)

        reply_string = build_response_text(plan, post)
        post_record_update["reply_type"] = (
            "plan_cluster" if plan.get("is_cluster") else "plan"
        )
    elif operation and operation in operations_map:
        print(operation, "requested: ", post.id)

        response_fn = operations_map[operation]['response']
        reply_string = response_fn(plans, post)
        post_record_update["reply_type"] = "operation"
        post_record_update["operation"] = operation
    else:
        print("topic mismatch: ", plan_id, post.id, plan_confidence)

        reply_string = build_no_match_response_text(potential_matches, post)
        post_record_update["reply_type"] = "no_match"

    try:
        did_reply = reply(post, reply_string, send=send, simulate=simulate, parent=options["parent"])
    except APIException as e:
        if e.error_type == "DELETED_COMMENT":
            did_reply = False
            post_record_update["skipped"] = True
            post_record_update["skip_reason"] = "deleted_comment"
        else:
            raise

    post_record_update["replied"] = did_reply
    if did_reply:
        # Replace default None values in post_record_update record
        post_record_update["reply_timestamp"] = firestore.SERVER_TIMESTAMP

    if not skip_tracking:
        posts_db.document(post.id).update(post_record_update)


def create_db_record(
    post,
    match=None,
    plan_confidence=None,
    plan_id=None,
    reply_timestamp=None,
    reply_made=False,
    processed=False,
    skipped=False,
    skip_reason=None,
) -> dict:
    # Reddit 3-digit code prefix removed for each id, leaving only the ID itself
    post_parent_id = post.parent_id[3:] if post.type == "comment" else None
    post_subreddit_id = post.subreddit.name[3:]
    post_top_level_parent_id = post.link_id[3:] if post.type == "comment" else None
    post_title = post.title if post.type == "submission" else None
    # Return db_entry for Firestore
    entry = {
        "processed": processed,
        "processed_timestamp": firestore.SERVER_TIMESTAMP,
        "replied": reply_made,
        "skipped": skipped,
        "skip_reason": skip_reason,
        "type": post.type,
        "post_id": post.id,
        "post_author": "/u/" + post.author.name,
        "post_text": post.text,
        "post_parent_id": post_parent_id,  # ID or None if no parent_id
        "post_url": "https://www.reddit.com" + post.permalink,
        "post_subreddit_id": post_subreddit_id,
        "post_subreddit_display_name": post.subreddit.display_name,
        "post_title": post_title,  # Post Title or None if no title
        "post_top_level_parent_id": post_top_level_parent_id,
        "post_locked": post.locked,
        # TODO flesh out / clarify this some
        "plan_match": match,
        "top_plan_confidence": plan_confidence,
        "top_plan": plan_id,
        "reply_timestamp": reply_timestamp,
    }

    return entry


def get_trigger_line(text, trigger_word="!warrenplanbot"):
    """
    Get the last line that !WarrenPlanBot occurs on,
    only returning the part of that line which occurs _after_ !WarrenPlamBot
    """
    matches = re.findall(fr"{trigger_word}\W+(.*)$", text, re.IGNORECASE | re.MULTILINE)

    return matches[-1] if matches else ""


def process_flags(text):
    """
    Identifies flags in the text. Removes the flags from the text and
    returns the tuple (remaining_text, options).
    """
    options = {
        "parent": False
    }

    match = re.match(r"^(?:-p|--parent)\s+(.*)$", text, re.IGNORECASE | re.MULTILINE)
    if match:
        options["parent"] = True
        text = match.group(1)

    return (text, options)
