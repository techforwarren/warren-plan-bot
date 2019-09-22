#!/usr/bin/env python3

import json
from os import path

import click

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
    pure_plans = json.load(plans_file)

with open(path.join(DIRNAME, "../src/plan_clusters.json")) as plans_file:
    plan_clusters = json.load(plans_file)

plans = pure_plans + plan_clusters

# Weights for how good/bad the possible outcomes are to be considered
CORRECT_MATCH = 1
ALTERNATE_MATCH = 0.5
NO_MATCH = 0
WRONG_MATCH = -2


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
    match_scoring = []
    for post in labeled_posts:
        match_info = strategy(plans, post)
        match = {
            "post_text": post.text,
            "post_source": post.source,
            "score": score_match(post, match_info),
            "match": match_info["match"],
            "match_confidence": match_info["confidence"],
        }
        match_scoring.append(match)

    correct_matches = [m for m in match_scoring if m["score"] == CORRECT_MATCH]
    alternate_matches = [m for m in match_scoring if m["score"] == ALTERNATE_MATCH]
    wrong_matches = [m for m in match_scoring if m["score"] == WRONG_MATCH]
    no_matches = [m for m in match_scoring if m["score"] == NO_MATCH]
    bulk_score = sum(m["score"] for m in match_scoring)
    total_score = bulk_score / len(labeled_posts) * 100

    return {
        "name": strategy_name,
        "total_score": total_score,
        "no_matches": no_matches,
        "wrong_matches": wrong_matches,
        "alternate_matches": alternate_matches,
        "correct_matches": correct_matches,
    }


@click.command()
@click.option(
    "-v",
    "--verbose",
    default=False,
    is_flag=True,
    help="scoring details of all strategies, rather than only the top one",
)
def score_strategies(verbose=False):
    strategies = [
        getattr(Strategy, func_name)
        for func_name in dir(Strategy)
        if callable(getattr(Strategy, func_name))
        if not func_name.startswith("_")
    ]

    scored_strategies = [score_strategy(strategy) for strategy in strategies]

    scored_strategies.sort(key=lambda x: -x["total_score"])

    if verbose:
        for strategy in scored_strategies:
            _print_strategy_scoring_details(strategy, verbose=verbose)
    else:
        _print_strategy_scoring_details(scored_strategies[0], verbose=verbose)

    print("")
    print("")
    print("--Top Strategies--")
    print("")

    for strategy in scored_strategies[:10]:
        print(f"{strategy['name']}: TOTAL SCORE: {round(strategy['total_score'],1)}")


def _print_strategy_scoring_details(strategy, verbose=False):
    print(f"")
    print(f"")
    print(f"--SCORING STRATEGY: {strategy['name']}--")
    print(f"")
    print(
        f"{strategy['name']}: NO MATCHES FOR:{'' if strategy['no_matches'] else ' None!'}\n"
    )
    for m in strategy["no_matches"]:
        print(f"{strategy['name']}: {m}")
    print(f"")

    print(
        f"{strategy['name']}: WRONG MATCHES FOR{'' if strategy['wrong_matches'] else ' None!'}:\n"
    )
    for m in strategy["wrong_matches"]:
        print(f"{strategy['name']}: {m}")
    print(f"")

    print(
        f"{strategy['name']}: ALTERNATE MATCHES FOR{'' if strategy['alternate_matches'] else ' None!'}:\n"
    )
    for m in strategy["alternate_matches"]:
        print(f"{strategy['name']}: {m}")
    print(f"")

    if verbose:
        print(
            f"{strategy['name']}: CORRECT MATCHES FOR{'' if strategy['correct_matches'] else ' None!'}:\n"
        )
        for m in strategy["correct_matches"]:
            print(f"{strategy['name']}: {m}")
        print(f"")

    print(f"{strategy['name']}: TOTAL SCORE: {strategy['total_score']}")


if __name__ == "__main__":
    score_strategies()
