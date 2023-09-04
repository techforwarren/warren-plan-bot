from os import path
import json
DIRNAME = path.dirname(path.realpath(__file__))


PLANS_FILE = path.abspath(path.join(DIRNAME, "plans.json"))
PLANS_CLUSTERS_FILE = path.abspath(path.join(DIRNAME, "plan_clusters.json"))
PLAN_TEXT_DIR = path.abspath(
    path.join(DIRNAME, "plan_text")
)
def load_plans() -> list[dict]:
    """
    Load all plans from json files

    :return: {
        "id": plan_id
        "topic": hand-picked human-readable topic for matching
        "summary": summary, from the Warren Campaign site
        "display_title": title, from the Warren Campaign site
        "url": url, from the Warren Campaign site
        "full_text": [for pure plans, not plan clusters] full text, scraped from the Warren Campaign site and processed to remove html elements, irrelevant campaign features etc...
        "plans": [for pure clusters, not pure plans] full text, scraped from the Warren Campaign site and processed using beautifulsoup
    },
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