#!/usr/bin/env python3

import json
from os import path

from matching import Strategy

DIRNAME = path.dirname(path.realpath(__file__))


class Post:
    """
    Post class that has the same attributes as Submission and Comment as used in matching,
    plus some methods used only for scoring
    """

    def __init__(self, post):
        self.post = post
        self.text = post["text"]
        self.source = post["source"]
        self.match = post["match"]
        self.alternate_matches = post.get("alternate_matches", [])


with open(path.join(DIRNAME, "labeled_posts.json")) as posts_file:
    labeled_posts = [Post(post) for post in json.load(posts_file)]


with open(path.join(DIRNAME, "../src/plans.json")) as plans_file:
    plans = json.load(plans_file)

# Weights for how good/bad the possible outcomes are to be considered
CORRECT_MATCH = 1
ALTERNATE_MATCH = 0.5
NO_MATCH = 0
WRONG_MATCH = -1


def score_match(post, match_info):
    if post.match == match_info["match"]:
        return CORRECT_MATCH
    if match_info["match"] in post.alternate_matches:
        return ALTERNATE_MATCH
    if match_info["match"] is None:
        return NO_MATCH
    return WRONG_MATCH


def score_strategy(strategy):
    strategy_name = strategy.__name__
    print(f"")
    print(f"--SCORING STRATEGY: {strategy_name}--")
    print(f"")
    match_scoring = []
    for post in labeled_posts:
        match_info = strategy(plans, post)
        match = {
            "post_text": post.text,
            "post_source": post.source,
            "score": score_match(post, match_info),
            "match": match_info["match"],
        }
        match_scoring.append(match)

    wrong_matches = [m for m in match_scoring if m["score"] == WRONG_MATCH]
    no_matches = [m for m in match_scoring if m["score"] == NO_MATCH]
    bulk_score = sum(m["score"] for m in match_scoring)
    total_score = bulk_score / len(labeled_posts) * 100

    print(f"{strategy_name}: NO MATCHES FOR:{'' if no_matches else ' None!'}\n")
    for m in no_matches:
        print(f"{strategy_name}: {m}")
    print(f"")

    print(f"{strategy_name}: WRONG MATCHES FOR{'' if wrong_matches else ' None!'}:\n")
    for m in wrong_matches:
        print(f"{strategy_name}: {m}")
    print(f"")

    print(f"{strategy_name}: TOTAL SCORE: {total_score}")


def score_strategies():
    strategies = [
        getattr(Strategy, func_name)
        for func_name in dir(Strategy)
        if callable(getattr(Strategy, func_name))
        if not func_name.startswith("_")
    ]
    for strategy in strategies:
        score_strategy(strategy)


if __name__ == "__main__":
    score_strategies()
