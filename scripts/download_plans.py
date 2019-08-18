#!/usr/bin/env python3

import json
import os
from os import path

import requests

DIRNAME = path.dirname(path.realpath(__file__))

PLANS_FILE = path.join(DIRNAME, "../src/plans.json")

OUTPUT_DIR = path.abspath(path.join(DIRNAME, "../data/raw/plan_html"))

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)


def download_plans():
    """
    Download all plans as html

    """
    with open(PLANS_FILE) as json_file:
        plans = json.load(json_file)

    # Iterate through plans_dict, download html
    for plan in plans:
        print(f"Downloading {plan['url']}")

        resp = requests.get(plan["url"])

        # FIXME black_maternal_mortality not downloaded.
        #  Status code: 403. Url: https://www.essence.com/feature/sen-elizabeth-warren-black-women-mortality-essence/
        if resp.status_code != 200:
            print(
                f"Plan {plan['id']} not downloaded. Status code: {resp.status_code}. Url: {plan['url']}"
            )
            continue

        page = resp.text

        filename = path.join(OUTPUT_DIR, plan["id"])

        print(f"Writing plan html to {filename}")
        with open(filename, "w") as plan_text_file:
            plan_text_file.write(page)


if __name__ == "__main__":
    download_plans()
