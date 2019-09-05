#!/usr/bin/env python3

import json
import os
from os import path

import click
import praw

import reddit_util

DIRNAME = path.dirname(path.realpath(__file__))

OUTPUT_FILE = path.abspath(path.join(DIRNAME, "../data/raw/trigger_posts"))


@click.command()
@click.option(
    "--praw-site",
    type=click.Choice(["dev", "prod"]),
    default="dev",
    help="section of praw file to use for reddit module configuration",
)
@click.option("--limit", type=int, default=100, help="number of posts to return")
@click.option("--bot-name", type=str, default="warrenplanbot", help="bot username")
def download_bot_post_parents(praw_site="dev", limit=100, bot_name="warrenplanbot"):
    # Change working directory so that praw.ini works, and so all files can be in this same folder. FIXME
    os.chdir(path.join(DIRNAME, "../src"))
    reddit = praw.Reddit(praw_site)
    comments = reddit.redditor(bot_name).comments.new(limit=limit)
    parents = (reddit_util.standardize(c.parent()) for c in comments)
    labeled_posts_skeleton = (
        {"text": c.text, "source": f"/r/{c.subreddit.display_name}", "match": None}
        for c in parents
    )

    with open(OUTPUT_FILE, "w") as output_file:
        print(f"downloading up to {limit} posts")
        json.dump(
            list(labeled_posts_skeleton), output_file, indent=2, separators=(",", ": ")
        )


if __name__ == "__main__":
    download_bot_post_parents()
