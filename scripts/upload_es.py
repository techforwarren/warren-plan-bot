#!/usr/bin/env python3

import glob
import json
import logging
from os import path

import click
from elasticsearch import Elasticsearch

logging.basicConfig(format="%(levelname)s : %(message)s", level=logging.INFO)

logger = logging.getLogger(__name__)

DIRNAME = path.dirname(path.realpath(__file__))

PLAN_INDEX = "plan"

# JSON filename of policy plans
PLAN_TEXT_DIR = path.abspath(path.join(DIRNAME, "../data/interim/plan_text"))
PLANS_FROM_REPO_PATH = path.abspath(path.join(DIRNAME, "../src/plans.json"))
PLAN_CLUSTERS_PATH = path.abspath(path.join(DIRNAME, "../src/plan_clusters.json"))

plan_file_paths = [f for f in glob.glob(path.join(PLAN_TEXT_DIR, "*"))]

mapping = {
    "properties": {
        "text": {
            "type": "text",
            "fields": {"english": {"type": "text", "analyzer": "english"}},
        },
        "display_title": {
            "type": "text",
            "fields": {"english": {"type": "text", "analyzer": "english"}},
        },
    }
}


@click.command()
@click.option("--host", envvar="ES_HOST")
@click.option("--port", envvar="ES_POST", type=int)
@click.option("--user", envvar="ES_USER")
@click.option("--password", envvar="ES_PASSWORD")
def upload(host, port, user, password):

    es = Elasticsearch(
        [
            {
                "host": host,
                "port": port,
                "use_ssl": True,
                "http_auth": f"{user}:{password}",
            }
        ]
    )
    print(
        {"host": host, "port": port, "use_ssl": True, "http_auth": f"{user}:{password}"}
    )

    # es.indices.delete(index=PLAN_INDEX, ignore=400)
    es.indices.create(index=PLAN_INDEX, ignore=400)

    es.indices.put_mapping(mapping, index=PLAN_INDEX)

    with open(PLANS_FROM_REPO_PATH) as json_file:
        plans_from_repo = json.load(json_file)

    with open(PLAN_CLUSTERS_PATH) as json_file:
        plan_clusters = json.load(json_file)

    for plan in plan_clusters:
        plan["is_cluster"] = True
        print(plan)
        plan["plans"] = [
            next(filter(lambda p: p["id"] == plan_id, plans_from_repo))
            for plan_id in plan["plan_ids"]
        ]

    parsed_plans = [
        json.load(open(plan_file_path)) for plan_file_path in plan_file_paths
    ]
    parsed_plans.sort(key=lambda p: p["id"])

    plans_from_repo = json.load(open(PLANS_FROM_REPO_PATH))
    plans_from_repo.sort(key=lambda p: p["id"])

    plan_clusters.sort(key=lambda p: p["id"])

    for parsed_plan, plan_from_repo in zip(parsed_plans, plans_from_repo):
        if parsed_plan["id"] != plan_from_repo["id"]:
            raise ValueError(f"Plans don't match {parsed_plan} {plan_from_repo}")
        plan_from_repo.update(parsed_plan)

    plans = plans_from_repo + plan_clusters

    # print(plans)

    for plan in plans:
        es.index(index=PLAN_INDEX, body=plan, id=plan["id"])


if __name__ == "__main__":
    upload()
