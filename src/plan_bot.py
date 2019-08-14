import re

from google.cloud import firestore

from matching import Strategy


def build_response_text(plan_record, post):
    """
    Create response text with plan summary
    """

    return (
        f"Senator Warren has a plan for that!"
        f"\n\n"
        f"{plan_record['summary']}"
        f"\n\n"
        # Link to learn more about the plan
        f"Learn more about her plan for [{plan_record['display_title']}]({plan_record['url']})"
        f"\n\n"
        # Horizontal line above footer
        "\n***\n"
        # Error reporting info
        f"Wrong topic or another problem?  [Send a report to my creator]"
        f"(https://www.reddit.com/message/compose?to=WarrenPlanBotDev&"
        f"subject=BotReport&"
        f"message=Issue with bot response to: {post.permalink}).  "
        f"\n"
        # Disclaimer
        f"This bot was independently created by volunteers for Sen. Warren's 2020 campaign.  "
        f"\n"
        # Add volunteer link
        f"If you'd like to join us, visit the campaign's "
        f"[Volunteer Sign-Up Page](https://my.elizabethwarren.com/page/s/web-volunteer)."
    )


def reply(post, reply_string: str, send=False, simulate=False):
    """
    :param post: post to reply on
    :param reply_string: string to reply with
    :param send: whether to send an actual reply to reddit
    :param simulate: whether to simulate sending an actual reply to reddit
    :return: did_reply – whether an actual or simulated reply was made
    """

    if simulate:
        print(f"[simulated] Bot replying to {post.type}: ", post.id)
        return True
    if send:
        post.reply(reply_string)
        return True

    print(f"Bot would have replied to {post.type}: ", post.id)


def process_post(
    post,
    plans,
    posts_db,
    post_ids_replied_to=None,
    send=False,
    simulate=False,
    skip_tracking=False,
    matching_strategy=Strategy.token_sort_ratio,
):
    if post_ids_replied_to is None:
        post_ids_replied_to = []

    if post.id not in post_ids_replied_to:
        # Do a case insensitive search
        if re.search("!warrenplanbot|/u/WarrenPlanBot", post.text, re.IGNORECASE):
            match_info = matching_strategy(plans, post)

            match = match_info["match"]
            plan_confidence = match_info["confidence"]
            plan = match_info["plan"]
            plan_id = plan["id"]
            post_parent_id = False # Could be "" unless constructing URLs with it later
            post_title = False # Could be "" unless constructing URLs with it later
            post_top_level_parent_id = False

            if(self.type == "comment"):
                # Reddit 3-digit code prefix removed for each id, leaving only the ID itself
                post_parent_id = post.parent_id([3:])
                post_top_level_parent_id = post.link_id([3:])
            
            if(self.type = "submission"):
                post_title = post.title
            
            # If plan is matched with confidence, build and send reply if post not locked
            if match and not post.locked:
                print("plan match: ", plan_id, post.id, plan_confidence)

                reply_string = build_response_text(plan, post)

                did_reply = reply(post, reply_string, send=send, simulate=simulate)

                if did_reply and not skip_tracking:
                    
                    posts_db.document(post.id).set(
                        {
                            # TODO add more info about the match here
                            "replied": True,
                            "type": post.type,
                            "post_author": "/u/" + post.author,
                            "post_text": post.text,
                            "post_parent_id": post_parent_id,   # ID or False if no parent_id
                            "post_url": "https://www.reddit.com" + post.permalink,
                            "post_subreddit": post.subreddit,
                            "post_title": post_title,           # Post Title or False if no title
                            "post_top_level_parent_id": post_top_level_parent_id,

                            # TODO flesh out / clarify this some
                            "plan_match": match,
                            "top_plan_confidence": plan_confidence,
                            "top_plan": plan_id,
                            "reply_timestamp": firestore.SERVER_TIMESTAMP,
                        }
                    )
            elif not skip_tracking:
                print("topic mismatch: ", plan_id, post.id, plan_confidence)
                posts_db.document(post.id).set(
                    {
                        # TODO add more info about the match here
                        "replied": False,
                        "type": post.type,
                        "post_author": "/u/" + post.author,
                        "post_text": post.text,
                        "post_parent_id": post_parent_id,   # ID or False if no parent_id
                        "post_url": "https://www.reddit.com" + post.permalink,
                        "post_subreddit": post.subreddit,
                        "post_title": post_title,           # Post Title or False if no title
                        "post_locked": post.locked

                        # TODO flesh out / clarify this some
                        "plan_match": match,
                        "top_plan_confidence": plan_confidence,
                        "top_plan": plan_id,
                    }
                )
