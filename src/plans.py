import json
from os import path
from typing import Literal, NotRequired, TypedDict, Union

DIRNAME = path.dirname(path.realpath(__file__))
PLANS_FILE = path.abspath(path.join(DIRNAME, "plans.json"))
PLANS_CLUSTERS_FILE = path.abspath(path.join(DIRNAME, "plan_clusters.json"))
PLAN_TEXT_DIR = path.abspath(path.join(DIRNAME, "plan_text"))


# Plan types #
# future work: migrate from dictionaries to classes
class BasePlan(TypedDict):
    """Base class for all Plans"""

    id: str  # plan id
    topic: str  # hand-picked human-readable topic for matching
    display_title: str  # title, from the Warren Campaign site


class PurePlan(BasePlan):
    """
    A single plan that can be matched
    """

    summary: str  # summary, from the Warren Campaign site
    full_text: str  # full text, scraped from the Warren Campaign site and processed to remove html elements, irrelevant campaign features etc...
    is_cluster: Literal[False]  # pure plans are not clusters
    url: str  # url, from the Warren Campaign site


class PlanCluster(BasePlan):
    """
    A cluster of plans that can be matched
    """

    plans: list[PurePlan]  # plans that make up the cluster
    is_cluster: Literal[True]  # pure plans are clusters
    url: NotRequired[str]  # url, from the Warren Campaign site, if available


Plan = Union[
    PurePlan, PlanCluster
]  # many functions will take either a pure plan or a plan cluster, as either can be matched


def load_plans() -> list[Plan]:
    """
        Load all plans from json files
    }
    """
    with open(PLANS_FILE) as json_file:
        pure_plans = json.load(json_file)

    for plan in pure_plans:
        plan["is_cluster"] = False
        plan["full_text"] = json.load(
            open(path.join(PLAN_TEXT_DIR, plan["id"] + ".json"))
        )["text"]

    with open(PLANS_CLUSTERS_FILE) as json_file:
        plan_clusters = json.load(json_file)

    for plan in plan_clusters:
        plan["is_cluster"] = True
        plan["plans"] = [
            next(filter(lambda p: p["id"] == plan_id, pure_plans))
            for plan_id in plan["plan_ids"]
        ]

    return pure_plans + plan_clusters
