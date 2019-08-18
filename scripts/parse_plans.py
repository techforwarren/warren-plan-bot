#!/usr/bin/env python3

import glob
import logging
import os
from os import path

from bs4 import BeautifulSoup, Comment

DIRNAME = path.dirname(path.realpath(__file__))

OUTPUT_DIR = path.abspath(path.join(DIRNAME, "../data/interim/plan_text"))

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

PLAN_HTML_DIR = path.abspath(path.join(DIRNAME, "../data/raw/plan_html"))

plan_file_paths = [f for f in glob.glob(path.join(PLAN_HTML_DIR, "*"))]

logging.basicConfig(format="%(levelname)s : %(message)s", level=logging.INFO)

logger = logging.getLogger(__name__)


def unwrap_and_smooth(soup, tag):
    # remove tag
    for t in soup.findAll(tag):
        t.unwrap()
    # smooth together the text that was in those tags with neighboring text
    soup.smooth()


def decompose_and_smooth(soup, tag):
    # remove tag
    for t in soup.findAll(tag):
        t.decompose()
    # smooth together the text that was in those tags with neighboring text
    soup.smooth()


def remove_html_comments(soup):
    comments = soup.findAll(text=lambda text: isinstance(text, Comment))
    for comment in comments:
        comment.extract()

    soup.smooth()


def parse_plan():
    """
    Extract text from plan html, preserving whitespace as appropriate

    Optimized for Medium posts
    """

    # Iterate through plans
    for plan_file_path in plan_file_paths:
        logger.info(f"Parsing {plan_file_path}")

        plan_id = path.basename(plan_file_path)

        with open(plan_file_path) as plan_file:
            page = plan_file.read()

        page_soup = BeautifulSoup(page, "lxml")

        article = page_soup.find("article")

        if article is None:
            # TODO parse ultra_millionaire_tax https://elizabethwarren.com/ultra-millionaire-tax/
            logger.warning(f"Failure to parse {plan_id}. Missing <article> tag")
            continue

        for tag in ["a", "b", "i", "u", "em", "strong"]:
            unwrap_and_smooth(article, tag)

        for tag in ["noscript", "img", "button"]:
            decompose_and_smooth(article, tag)

        remove_html_comments(article)

        text = article.get_text(separator="\n")

        filename = path.join(OUTPUT_DIR, plan_id)

        logger.info(f"Writing plan text to {filename}")
        with open(filename, "w") as plan_text_file:
            plan_text_file.write(text)


if __name__ == "__main__":
    parse_plan()
