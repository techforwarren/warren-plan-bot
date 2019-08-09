import praw
import pdb
import re
import os
import json
import click
import urllib.parse
import sys
import tempfile
from google.cloud import storage

from fuzzywuzzy import fuzz
from fuzzywuzzy import process

# JSON filename of policy plans
PLANS_FILE = "plans.json"


def build_response_text(plan_record, submission_id="None", comment_id="None"):
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


def parse_gs_uri(uri):
    '''
    :param uri:
    :return: (bucket, blob)
    '''
    parsed = urllib.parse.urlparse(uri)

    return parsed.netloc, parsed.path.strip("/")


def read_file(uri):
    if uri.startswith("gs://"):
        bucket_name, blob_name = parse_gs_uri(uri)

        storage_client = storage.Client()
        bucket = storage_client.get_bucket(bucket_name)

        return bucket.blob(blob_name).download_as_string().decode("utf-8")

    if not os.path.isfile(uri):
        return

    with open(uri, "r") as f:
        return f.read()


def write_file(uri, contents):
    if uri.startswith("gs://"):
        bucket_name, blob_name = parse_gs_uri(uri)

        storage_client = storage.Client()
        bucket = storage_client.get_bucket(bucket_name)

        return bucket.blob(blob_name).upload_from_string(contents)

    with open(uri, "w") as f:
        return f.write(contents)


@click.command()
@click.option('--replied-to-path', envvar='REPLIED_TO_PATH', type=click.Path(),
              default="gs://wpb-storage-dev/posts_replied_to.txt", help='path to file where replies are tracked')
@click.option('--send-replies/--skip-send', envvar='SEND_REPLIES', default=False, is_flag=True,
              help='whether to send replies')
@click.option('--skip-tracking', default=False, is_flag=True,
              help='whether to check whether replies have already been posted')
@click.option('--limit', envvar='LIMIT', default=10, type=int, help='number of posts to return')
def run_plan_bot(replied_to_path="gs://wpb-storage-dev/posts_replied_to.txt", send_replies=False, skip_tracking=False,
                 limit=10):
    # Change working directory so that praw.ini works, and so all files can be in this same folder. FIXME
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    # change dev to prod to shift to production bot
    reddit = praw.Reddit('dev')

    with open(PLANS_FILE) as json_file:
        plans_dict = json.load(json_file)

    posts_replied_to_contents = read_file(replied_to_path) or "" if not skip_tracking else ""

    # Load the list of posts replied to or start with empty list if none
    posts_replied_to = list(filter(None, posts_replied_to_contents.split("\n")))

    # Get the subreddit
    subreddit = reddit.subreddit("WPBSandbox")

    # Get the number of new posts up to the limit
    for submission in subreddit.new(limit=limit):

        # If we haven't replied to this post before
        if submission.id not in posts_replied_to:

            # Do a case insensitive search
            if re.search("!warrenplanbot|/u/WarrenPlanBot", submission.selftext, re.IGNORECASE):

                # Initialize match_confidence and match_id before fuzzy searching
                match_confidence = 0
                match_id = 0

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
                if send_replies:
                    submission.reply(reply_string)
                    print("Bot replying to submission: ", submission.id)
                    # Append post id to prevent future replies to the same submission
                    posts_replied_to.append(submission.id)
                else:
                    print("Bot would have replied to submission: ", submission.id)

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
                        if send_replies:
                            comment.reply(reply_string)
                            print("Bot replying to comment: ", comment.id)
                            posts_replied_to.append(comment.id)
                        else:
                            print("Bot would have replied to comment: ", comment.id)

    # Write the updated tracking list back to the file
    post_replied_to_output = "\n".join(posts_replied_to)

    if send_replies and not skip_tracking:
        write_file(replied_to_path, post_replied_to_output)
        print("updated posts_replied_to list:", "\n", post_replied_to_output)
    else:
        print("would have updated posts_replied_to list to:", "\n", post_replied_to_output)


def run_plan_bot_event_handler(event, context):
    # Click exits with return code 0 when everything worked. Skip that behavior
    try:
        run_plan_bot(prog_name='run_that_plan_bot')  # need to set prog_name to avoid weird click behavior in cloud fn
    except SystemExit as e:
        if e.code != 0:
            raise


if __name__ == "__main__":
    run_plan_bot()
