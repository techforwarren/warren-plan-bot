import praw
import pdb
import re
import os
import json
import fuzzywuzzy
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

# change dev to prod to shift to production bot
reddit = praw.Reddit('dev')

# JSON filename of policy plans
plans_file = "plans.json"

POSTS_REPLIED_TO_PATH = os.getenv("POSTS_REPLIED_TO_PATH", "posts_replied_to.txt")


def build_response_text(plan_record, submission_id=None, comment_id=None):
    """
    Create response text with plan summary
    """

    reply_string = "She has a plan for " + plan_record["topic"] + "!\n\n" + plan_record["summary"] + "\n\n"
    # Add link to learn more about the plan
    reply_string = reply_string + "Learn more about her plan for [" + plan_record["display_title"] + "](" + plan_record[
        "url"] + ")\n\n"

    # Add horizontal line above footer
    reply_string = reply_string + "\n***\n"
    # Add error reporting info
    reply_string = reply_string + f"Wrong topic or another problem?  [Send a report to my creator](https://www.reddit.com/message/compose?to=WarrenPlanBotDev&subject=reference&nbsp;{'comment' if comment_id else 'post'}&nbsp;id[" + submission_id + " | " + comment_id + "]).  \n"
    # Add disclaimer
    reply_string = reply_string + "This bot was independently created by volunteers for Sen. Warren's 2020 campaign.  \n"
    # Add volunteer link
    reply_string = reply_string + "If you'd like to join us, visit the campaign's [Volunteer Sign-Up Page](https://my.elizabethwarren.com/page/s/web-volunteer).  \n"

    return reply_string


def run_plan_bot(*args, **kwargs):
    with open(plans_file) as json_file:
        plans_dict = json.load(json_file)

    # Check if replied posts exists, if not create an empty list
    if not os.path.isfile(POSTS_REPLIED_TO_PATH):
        posts_replied_to = []

    # If replied posts file exists, load the list of posts replied to from it
    else:
        # Read the file into a list and remove any empty values
        with open(POSTS_REPLIED_TO_PATH, "r") as f:
            posts_replied_to = f.read()
            posts_replied_to = posts_replied_to.split("\n")
            posts_replied_to = list(filter(None, posts_replied_to))

    # Get the subreddit
    subreddit = reddit.subreddit("WPBSandbox")

    # Set const for number of posts to return
    post_limit = 10

    # Get the number of new posts up to the limit
    for submission in subreddit.new(limit=post_limit):

        # If we haven't replied to this post before

        if submission.id not in posts_replied_to:

            # Do a case insensitive search
            if re.search("!warrenplanbot|/u/WarrenPlanBot", submission.selftext, re.IGNORECASE):

                # Initialize match_confidence and match_id before fuzzy searching
                match_confidence = 0
                match_id = 0
                match_response = ""
                # Search topic keywords and response body for best match
                for item in plans_dict["plans"]:
                    item_match_confidence = fuzz.WRatio(submission.selftext, item["topic"])

                    if item_match_confidence > match_confidence:
                        # Set new match ID
                        match_confidence = item_match_confidence
                        match_id = item["id"]
                        print("new topic match: ", item["topic"])

                # Select entry from plans_dict using best match ID
                plan_record = next(plan for plan in plans_dict["plans"] if plan["id"] == match_id)

                reply_string = build_response_text(plan_record, submission.id)

                # Reply to the post with plan info, uncomment next line to activate post replies
                submission.reply(reply_string)
                print("Bot replying to: ", submission.id)

                # Append post id to prevent future replies to the same submission
                posts_replied_to.append(submission.id)

            # After checking submission.selftext, check comments
            # Get comments for submission and search for trigger in comment body
            submission.comments.replace_more(limit=None)
            for comment in submission.comments.list():
                # If we haven't replied to the comment before
                if comment.id not in posts_replied_to:

                    # Search for trigger phrases in the comment
                    if re.search("!warrenplanbot|/u/WarrenPlanBot", comment.body, re.IGNORECASE):

                        # Search for matching topic keywords in comment body
                        # Initialize match_confidence, match_id, match_response before fuzzy searching
                        match_confidence = 0
                        match_id = 0
                        match_response = ""
                        # Search topic keywords and response body for best match
                        for item in plans_dict["plans"]:
                            item_match_confidence = fuzz.WRatio(comment.body, item["topic"])

                            if item_match_confidence > match_confidence:
                                # Set new match ID
                                match_confidence = item_match_confidence
                                match_id = item["id"]

                        # Select entry from plans_dict using best match ID
                        plan_record = next(plan for plan in plans_dict["plans"] if plan["id"] == match_id)

                        # Create response text with plan summary
                        reply_string = build_response_text(plan_record, submission.id, comment.id)

                        # Reply to the post with plan info, uncomment next line to activate post replies
                        comment.reply(reply_string)
                        print("Bot replying to: ", comment.id)
                        posts_replied_to.append(comment.id)

    # Write the updated list back to the file
    with open(POSTS_REPLIED_TO_PATH, "w") as f:
        for post_id in posts_replied_to:
            # record post IDs so it doesn't reply multiple times
            f.write(post_id + "\n")
            print("updated replies list includes: ", post_id + "\n")


if __name__ == "__main__":
    run_plan_bot()
