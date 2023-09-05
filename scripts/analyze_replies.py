#!/usr/bin/env python3

from collections import Counter
from os import path

import click
from google.cloud import firestore

DIRNAME = path.dirname(path.realpath(__file__))

OUTPUT_FILE = path.abspath(path.join(DIRNAME, "../data/raw/reply_analysis"))


@click.command()
@click.option(
    "--project",
    envvar="GCP_PROJECT",
    default="wpb-dev",
    type=str,
    help="gcp project where firestore db lives",
)
def analyze_replies(project="wpb-dev"):
    db = firestore.Client(project=project)

    posts_db = db.collection("posts")

    posts_processed = posts_db.where("processed", "==", True).stream()

    matched_plan_counter = Counter()
    top_plan_counter = Counter()

    for post in posts_processed:
        post = post.to_dict()
        if not post.get("skip_reason"):
            matched_plan_counter[post.get("plan_match") or post.get("operation")] += 1
            top_plan_counter[post.get("top_plan") or post.get("operation")] += 1

    print("Matched plans / operations")
    print(matched_plan_counter)
    print("Top plans (when no match) / operations")
    print(top_plan_counter)


if __name__ == "__main__":
    analyze_replies()
