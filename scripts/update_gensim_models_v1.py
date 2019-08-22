#!/usr/bin/env python3


import glob
import json
import logging
import os
from os import path

from gensim import corpora, models, similarities

from matching import GENSIM_V1_MODELS_PATH, Preprocess

logging.basicConfig(format="%(levelname)s : %(message)s", level=logging.INFO)

logger = logging.getLogger(__name__)

DIRNAME = path.dirname(path.realpath(__file__))

OUTPUT_DIR = GENSIM_V1_MODELS_PATH

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)


PLAN_TEXT_DIR = path.abspath(path.join(DIRNAME, "../data/interim/plan_text"))

plan_file_paths = [f for f in glob.glob(path.join(PLAN_TEXT_DIR, "*"))]


def update_gensim_models():
    """
    Prepare TFIDF and LSA models for later similarity comparisons
    """

    parsed_plans = [
        json.load(open(plan_file_path)) for plan_file_path in plan_file_paths
    ]

    # save plan ids to be able to get back to plan id from document index later
    plan_ids = [p["id"] for p in parsed_plans]
    with open(path.join(OUTPUT_DIR, "plan_ids.json"), "w") as plan_id_file:
        json.dump(plan_ids, plan_id_file)

    documents = [p["text"] for p in parsed_plans]

    # Run preprocessing
    preprocessed_documents = [Preprocess.preprocess_gensim_v1(doc) for doc in documents]

    dictionary = corpora.Dictionary(preprocessed_documents)

    dictionary.save(path.join(OUTPUT_DIR, "plans.dict"))

    corpus = [dictionary.doc2bow(text) for text in preprocessed_documents]
    # Maybe save corpus
    # corpora.MmCorpus.serialize('/tmp/deerwester.mm', corpus)  # store to disk, for later use

    # Models #

    ## TFIDF

    tfidf = models.TfidfModel(corpus)

    corpus_tfidf = tfidf[corpus]

    # LSI
    lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=300)

    lsi_index = similarities.MatrixSimilarity(lsi[corpus], num_features=len(dictionary))
    lsi.save(path.join(OUTPUT_DIR, "lsi.model"))
    lsi_index.save(path.join(OUTPUT_DIR, "lsi.index"))


if __name__ == "__main__":
    update_gensim_models()
