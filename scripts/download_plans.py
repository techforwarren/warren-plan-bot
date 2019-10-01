#!/usr/bin/env python3

import json
import logging
import os
from os import path

import click
import requests

logging.basicConfig(format="%(levelname)s : %(message)s", level=logging.INFO)

logger = logging.getLogger(__name__)

DIRNAME = path.dirname(path.realpath(__file__))

PLANS_FILE = path.join(DIRNAME, "../src/plans.json")

OUTPUT_DIR = path.abspath(path.join(DIRNAME, "../data/raw/plan_html"))

def create_output_dir():
    """
    Make empty output directory
    """
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

def clear_output_dir():
    for file_path in os.listdir(OUTPUT_DIR):
        os.remove(path.join(OUTPUT_DIR, file_path))


@click.command()
@click.option(
    "--force-redownload",
    default=False,
    is_flag=True,
    help="force all plans to re-download",
)
def download_plans(force_redownload=False):
    """
    Download all plans as html

    """
    with open(PLANS_FILE) as json_file:
        plans = json.load(json_file)

    if force_redownload:
        clear_output_dir()

    # Iterate through plans_dict, download html
    for plan in plans:
        filename = path.join(OUTPUT_DIR, f"{plan['id']}.json")

        if os.path.exists(filename):
            logger.info(f"Plan already downloaded. Skipping {plan['id']}")
            continue

        # if we already have the "full text" of a plan in plans.json for some reason or another
        if plan.get("full_text"):
            logger.info(
                f"Full text available for {plan['id']}. Saving and skipping download"
            )

            with open(filename, "w") as plan_text_file:
                json.dump(
                    {
                        "full_text": plan["full_text"],
                        "url": plan["url"],
                        "id": plan["id"],
                    },
                    plan_text_file,
                )
            continue

        logger.info(f"Downloading {plan['url']}")

        resp = requests.get(
            plan["url"],
            headers={
                # add user agent to avoid some 403s
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
            },
        )

        if resp.status_code != 200:
            logger.warning(
                f"Plan {plan['id']} not downloaded. Status code: {resp.status_code}. Url: {plan['url']}"
            )
            continue

        html = resp.text

        logger.info(f"Writing plan html to {filename}")
        with open(filename, "w") as plan_text_file:
            json.dump(
                {"html": html, "url": plan["url"], "id": plan["id"]}, plan_text_file
            )


if __name__ == "__main__":
    create_output_dir()
    download_plans()
