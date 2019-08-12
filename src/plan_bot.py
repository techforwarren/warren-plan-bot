import re

from fuzzywuzzy import fuzz
from google.cloud import firestore


def build_response_text(plan_record, post):
    """
    Create response text with plan summary
    """
    submission = post if post.type == "submission" else post.submission
    comment = post if post.type == "comment" else None

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
        f"subject=reference&nbsp;Submission[{submission.id}]&nbsp{'Comment[' + comment.id + ']' if comment else ''}).  "
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
    plans_dict,
    posts_db,
    post_ids_replied_to=None,
    send=False,
    simulate=False,
    skip_tracking=False,
):
    if post_ids_replied_to is None:
        post_ids_replied_to = []

    if post.id not in post_ids_replied_to:
        # Do a case insensitive search
        if re.search("!warrenplanbot|/u/WarrenPlanBot", post.text, re.IGNORECASE):
            # Initialize minimum match_confidence to 50% and match_id before fuzzy searching
            match_confidence = 50
            match_id = 0
            match_topic=""

            # Search topic keywords and response body for best match
            for plan in plans_dict["plans"]:
                plan_match_confidence = fuzz.token_sort_ratio(post.text, plan["topic"])

                if plan_match_confidence > match_confidence:
                    # Set new match ID
                    match_confidence = plan_match_confidence
                    match_id = plan["id"]
                    match_topic = plan["topic"]
                    print("new topic match: ", plan["topic"])

            # If new topic matched with confidence > 50% select and build reply from new match_id
            if match_id != 0:
                # Select entry from plans_dict using best match ID
                plan_record = next(
                    plan for plan in plans_dict["plans"] if plan["id"] == match_id
                )

                reply_string = build_response_text(plan_record, post)

                did_reply = reply(post, reply_string, send=send, simulate=simulate)

                if did_reply and not skip_tracking:
                    posts_db.document(post.id).set(
                        {
                            # TODO add more info about the match here
                            "replied": True,
                            "type": post.type,
                            "topic_confidence": match_confidence,
                            "topic_selected": match_topic,
                            "reply_timestamp": firestore.SERVER_TIMESTAMP,
                        }
                    )
            else:
                posts_db.document(post.id).set(
                    {
                        # TODO add more info about the match here
                        "replied": False,
                        "type": post.type,
                        "topic_confidence": match_confidence,
                        "post_text": post.text
                    }
                )
