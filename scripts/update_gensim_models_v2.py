#!/usr/bin/env python3


import glob
import json
import logging
import os
from os import path

from gensim import corpora, models, similarities

from matching import GENSIM_V2_MODELS_PATH, Preprocess

logging.basicConfig(format="%(levelname)s : %(message)s", level=logging.INFO)

logger = logging.getLogger(__name__)

DIRNAME = path.dirname(path.realpath(__file__))

OUTPUT_DIR = GENSIM_V2_MODELS_PATH

logging.getLogger("gensim").setLevel(logging.INFO)

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)


PLAN_TEXT_DIR = path.abspath(path.join(DIRNAME, "../data/interim/plan_text"))
PLANS_FROM_REPO_PATH = path.abspath(path.join(DIRNAME, "../src/plans.json"))
PLAN_CLUSTERS_PATH = path.abspath(path.join(DIRNAME, "../src/plan_clusters.json"))

plan_file_paths = [f for f in glob.glob(path.join(PLAN_TEXT_DIR, "*"))]


def update_gensim_models():
    """
    Prepare TFIDF and LSA models for later similarity comparisons
    """

    parsed_plans = [
        json.load(open(plan_file_path)) for plan_file_path in plan_file_paths
    ]
    parsed_plans.sort(key=lambda p: p["id"])

    plans_from_repo = json.load(open(PLANS_FROM_REPO_PATH))
    plans_from_repo.sort(key=lambda p: p["id"])

    plan_clusters = json.load(open(PLAN_CLUSTERS_PATH))
    plan_clusters.sort(key=lambda p: p["id"])

    for parsed_plan, plan_from_repo in zip(parsed_plans, plans_from_repo):
        if parsed_plan["id"] != plan_from_repo["id"]:
            raise ValueError(f"Plans don't match {parsed_plan} {plan_from_repo}")

    documents_for_training = [
        p["text"]
        + "\n"
        + p2.get("additional_training_text", "")
        + "\n"
        + p2.get("display_title", "")
        for p, p2 in zip(parsed_plans, plans_from_repo)
    ] + [
        c["topic"]
        + "\n"
        + c.get("additional_training_text", "")
        + "\n"
        + c.get("display_title", "")
        for c in plan_clusters
    ]

    documents_for_matching = (
        documents_for_training
        + [p["topic"] for p in plan_clusters]
        + [p["display_title"] for p in plan_clusters]
        + [p["topic"] for p in plans_from_repo]
        + [p["display_title"] for p in plans_from_repo]
    )

    plan_ids_for_matching = (
        [p["id"] for p in plans_from_repo]
        + [p["id"] for p in plan_clusters]
        + [p["id"] for p in plan_clusters]
        + [p["id"] for p in plan_clusters]
        + [p["id"] for p in plans_from_repo]
        + [p["id"] for p in plans_from_repo]
    )

    # Run preprocessing
    preprocessed_documents_for_training = [
        Preprocess.preprocess_gensim_v1(doc) for doc in documents_for_training
    ]
    preprocessed_documents_for_matching = [
        Preprocess.preprocess_gensim_v1(doc) for doc in documents_for_matching
    ]

    dictionary = corpora.Dictionary(preprocessed_documents_for_training)

    dictionary.save(path.join(OUTPUT_DIR, "plans.dict"))

    training_corpus = [
        dictionary.doc2bow(text) for text in preprocessed_documents_for_training
    ]

    matching_corpus = [
        dictionary.doc2bow(text) for text in preprocessed_documents_for_matching
    ]
    # Maybe save training_corpus
    # corpora.MmCorpus.serialize('/tmp/deerwester.mm', training_corpus)  # store to disk, for later use

    # Models #

    ## TFIDF

    tfidf = models.TfidfModel(training_corpus)

    training_corpus_tfidf = tfidf[training_corpus]
    tfidf_index = similarities.MatrixSimilarity(
        tfidf[matching_corpus], num_features=len(dictionary)
    )

    tfidf.save(path.join(OUTPUT_DIR, "tfidf.model"))
    tfidf_index.save(path.join(OUTPUT_DIR, "tfidf.index"))

    # LSA
    lsa = models.LsiModel(training_corpus_tfidf, id2word=dictionary, num_topics=300)

    lsa_index = similarities.MatrixSimilarity(
        lsa[matching_corpus], num_features=len(dictionary)
    )
    lsa.save(path.join(OUTPUT_DIR, "lsa.model"))
    lsa_index.save(path.join(OUTPUT_DIR, "lsa.index"))

    # save plan ids to be able to get back to plan id from document index later
    with open(path.join(OUTPUT_DIR, "plan_ids.json"), "w") as plan_id_file:
        json.dump(plan_ids_for_matching, plan_id_file)


if __name__ == "__main__":
    update_gensim_models()
