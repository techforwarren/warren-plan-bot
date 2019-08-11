#!/usr/bin/env python3

import json
import os

import click
import praw
import praw.models
from google.cloud import firestore

import reddit_util
from plan_bot import process_post

# JSON filename of policy plans
PLANS_FILE = "plans.json"

click_kwargs = {"show_envvar": True, "show_default": True}


@click.command()
@click.option(
    "--send-replies/--skip-send",
    envvar="SEND_REPLIES",
    default=False,
    is_flag=True,
    help="whether to send replies",
    **click_kwargs,
)
@click.option(
    "--skip-tracking",
    default=False,
    is_flag=True,
    help="whether to check whether replies have already been posted",
    **click_kwargs,
)
@click.option(
    "--simulate-replies",
    default=False,
    is_flag=True,
    help="pretend to make replies, including updating state",
    **click_kwargs,
)
@click.option(
    "--limit",
    envvar="LIMIT",
    type=int,
    default=10,
    help="number of posts to return",
    **click_kwargs,
)
@click.option(
    "--praw-site",
    envvar="PRAW_SITE",
    type=click.Choice(["dev", "prod"]),
    default="dev",
    help="section of praw file to use for reddit module configuration",
    **click_kwargs,
)
@click.option(
    "--project",
    envvar="GCP_PROJECT",
    default="wpb-dev",
    type=str,
    help="gcp project where firestore db lives",
    **click_kwargs,
)
def run_plan_bot(
    send_replies=False,
    skip_tracking=False,
    simulate_replies=False,
    limit=10,
    praw_site="dev",
    project="wpb-dev",
):
    """
    Run a single pass of Warren Plan Bot

    \b
    - Check list of posts replied to (If tracking is on)
    - Search for any new comments and submissions not on that list
    - Reply to any unreplied matching comments (If replies are on)
    - Update replied_to list (If replies and tracking is on)
    """

    if simulate_replies and send_replies:
        raise ValueError(
            "--simulate-replies and --send-replies options are incompatible. at most one may be set"
        )

    # Change working directory so that praw.ini works, and so all files can be in this same folder. FIXME
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    # change dev to prod to shift to production bot
    reddit = praw.Reddit(praw_site)

    # Ensure that we don't accidentally write to Reddit
    reddit.read_only = not send_replies

    with open(PLANS_FILE) as json_file:
        plans_dict = json.load(json_file)

    if skip_tracking:
        posts_db = None
        post_ids_replied_to = []
    else:
        db = firestore.Client(project=project)

        posts_db = db.collection("posts")

        # Load the list of posts replied to or start with empty list if none
        posts_replied_to = posts_db.where("replied", "==", True).stream()

        post_ids_replied_to = [post.id for post in posts_replied_to]

        print("post ids previously replied to", post_ids_replied_to)

    # Get the subreddit
    subreddit = reddit.subreddit("WPBSandbox")

    # Get the number of new posts up to the limit
    for submission in subreddit.new(limit=limit):
        # turn this into our more standardized class
        submission = reddit_util.Submission(submission)
        process_post(
            submission,
            plans_dict,
            posts_db,
            post_ids_replied_to,
            send=send_replies,
            simulate=simulate_replies,
            skip_tracking=skip_tracking,
        )

        # Get comments for submission and search for trigger in comment body
        submission.comments.replace_more(limit=None)
        for comment in submission.comments.list():
            # turn this into our more standardized class
            comment = reddit_util.Comment(comment)
            process_post(
                comment,
                plans_dict,
                posts_db,
                post_ids_replied_to,
                send=send_replies,
                simulate=simulate_replies,
                skip_tracking=skip_tracking,
            )


def run_plan_bot_event_handler(event, context):
    # Click exits with return code 0 when everything worked. Skip that behavior
    try:
        run_plan_bot(
            prog_name="run_that_plan_bot"
        )  # need to set prog_name to avoid weird click behavior in cloud fn
    except SystemExit as e:
        if e.code != 0:
            raise


if __name__ == "__main__":
    run_plan_bot()
