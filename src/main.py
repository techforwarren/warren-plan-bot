#!/usr/bin/env python3

import json
import logging
import os
import re
import time

import click
import praw
import praw.models
from google.cloud import firestore

import pushshift
import reddit_util
from plan_bot import process_post

logger = logging.getLogger(__name__)

# JSON filename of policy plans
PLANS_FILE = "plans.json"
PLANS_CLUSTERS_FILE = "plan_clusters.json"
VERBATIMS_FILE = "verbatims.json"
TIME_IN_LOOP = float(
    os.getenv("TIME_IN_LOOP", 40)
)  # seconds to spend in loop when calling from event handler. this should be less than the time between running iterations of the cloud function

click_kwargs = {"show_envvar": True, "show_default": True}

POST_IDS_PROCESSED = set()


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
    envvar="SKIP_TRACKING",
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
@click.option(
    "--log-level",
    envvar="LOG_LEVEL",
    type=click.Choice(["0", "1", "2", "3"]),
    default="1",
    help="log level (quiet, info, debug, debug imports)",
    **click_kwargs,
)
def run_plan_bot(
    send_replies=False,
    skip_tracking=False,
    simulate_replies=False,
    limit=10,
    praw_site="dev",
    project="wpb-dev",
    log_level="1",
):
    """
    Run a single pass of Warren Plan Bot

    \b
    - Check list of posts replied to (If tracking is on)
    - Search for any new comments and submissions not on that list
    - Reply to any unreplied matching comments (If replies are on)
    - Update replied_to list (If replies and tracking is on)
    """
    if log_level == "0":
        level_name = logging.WARNING
    elif log_level == "1":
        level_name = logging.INFO
    else:
        level_name = logging.DEBUG

    logging.basicConfig(
        level=level_name, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )
    if log_level == "2":
        # silence debug-logging from external imports so we can have a
        # "quiet" debug log when we want it.   Additional imports
        # may mean needing to update this.
        for logger_name in ("prawcore", "urllib3", "smart_open"):
            logging.getLogger(logger_name).setLevel(logging.INFO)

    logger.info("Running a single pass of plan bot")
    pass_start_time = time.time()

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
        pure_plans = json.load(json_file)

    with open(PLANS_CLUSTERS_FILE) as json_file:
        plan_clusters = json.load(json_file)

    for plan in plan_clusters:
        plan["is_cluster"] = True
        plan["plans"] = [
            next(filter(lambda p: p["id"] == plan_id, pure_plans))
            for plan_id in plan["plan_ids"]
        ]

    plans = pure_plans + plan_clusters

    with open(VERBATIMS_FILE) as json_file:
        verbatims = json.load(json_file)

    if skip_tracking:
        posts_db = None
        comments_progress_ref = None
    else:
        db = firestore.Client(project=project)

        posts_db = db.collection("posts")

        # get post ids from database only if we don't already have them
        if not POST_IDS_PROCESSED:
            # Load the list of posts processed to or start with empty list if none
            posts_processed = posts_db.where("processed", "==", True).stream()

            POST_IDS_PROCESSED.update({post.id for post in posts_processed})

        # Track progress of comments
        comments_progress_ref = db.collection("progress").document("comments")

    process_the_post = lambda post: process_post(
        post,
        plans,
        verbatims,
        posts_db,
        POST_IDS_PROCESSED,
        send=send_replies,
        simulate=simulate_replies,
        skip_tracking=skip_tracking,
    )

    subreddit_name = "ElizabethWarren" if praw_site == "prod" else "WPBSandbox"

    # Get the subreddit
    subreddit = reddit.subreddit(subreddit_name)

    # Get the number of new submissions up to the limit
    # Note: If this gets slow, we could switch this to pushshift
    for submission in subreddit.search(
        "warrenplanbot", sort="new", time_filter="all", limit=limit
    ):
        # turn this into our more standardized class
        submission = reddit_util.Submission(submission)
        process_the_post(submission)

    for pushshift_comment in pushshift.search_comments(
        "warrenplanbot", subreddit_name, limit=limit
    ):

        comment = reddit_util.Comment(
            praw.models.Comment(reddit, _data=pushshift_comment)
        )

        process_the_post(comment)

    # Get new comments since we last ran.
    #
    # subreddit.comments() returns the newest comments first so we
    # need to reverse it so that the comments we're iterating over are getting newer.
    # With no specified params, it returns newest 100 comments in the
    # subreddit.
    comments_params = get_comments_params(comments_progress_ref)
    for comment in reversed(list(subreddit.comments(params=comments_params))):
        comment = reddit_util.Comment(comment)
        if re.search("warrenplanbot", comment.text, re.IGNORECASE):
            process_the_post(comment)

        # update the cursor after processing the comment
        if not skip_tracking:
            comments_progress_ref.set({"newest": comment.fullname}, merge=True)

    logger.info(
        f"Single pass of plan bot took: {round(time.time() - pass_start_time, 2)}s"
    )


def get_comments_params(comments_progress_ref):
    if comments_progress_ref:
        comments_progress = comments_progress_ref.get()
        if comments_progress.exists:
            newest_comment_id = comments_progress.get("newest")
            if newest_comment_id:
                # Gets newer comments that our newest comment
                return {"before": newest_comment_id}

    # Empty params causes subreddit.comments() to return the newest
    # comments in the subreddit.
    return {}


def run_plan_bot_event_handler(event, context):
    start_time = time.time()
    logger.info("Starting plan bot loop")
    while time.time() - start_time < TIME_IN_LOOP:
        # Click exits with return code 0 when everything worked. Skip that behavior
        try:
            run_plan_bot(
                prog_name="run_that_plan_bot"
            )  # need to set prog_name to avoid weird click behavior in cloud fn
        except SystemExit as e:
            if e.code != 0:
                raise
        # add a sleep so things don't go crazy if we make things very fast at some point
        # for example, pushshift has a rate limit that we don't want to hit https://api.pushshift.io/meta
        time.sleep(1)


if __name__ == "__main__":
    run_plan_bot()
