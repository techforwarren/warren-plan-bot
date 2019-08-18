#!/usr/bin/env python3


import glob
import json
import logging
import os
from os import path

from gensim import corpora, models, similarities
from gensim.parsing.preprocessing import (
    preprocess_string,
    remove_stopwords,
    stem_text,
    strip_multiple_whitespaces,
    strip_numeric,
    strip_punctuation,
    strip_short,
)

logging.basicConfig(format="%(levelname)s : %(message)s", level=logging.INFO)

logger = logging.getLogger(__name__)

DIRNAME = path.dirname(path.realpath(__file__))

OUTPUT_DIR = path.abspath(path.join(DIRNAME, "../src/models/gensim_strategy_v1"))

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)


PLAN_TEXT_DIR = path.abspath(path.join(DIRNAME, "../data/interim/plan_text"))

plan_file_paths = [f for f in glob.glob(path.join(PLAN_TEXT_DIR, "*"))]


CUSTOM_STOPWORDS = {"elizabeth", "warren", "plan", "warrenplanbot", "warrenplanbotdev"}


def remove_custom_stopwords(s):
    return " ".join(w for w in s.split() if w.lower() not in CUSTOM_STOPWORDS)


def preprocess(doc):
    # Run preprocessing
    preprocessing_filters = [  # TODO maybe add additional stopwords
        strip_punctuation,
        strip_multiple_whitespaces,
        strip_numeric,
        remove_stopwords,
        remove_custom_stopwords,
        strip_short,
        stem_text,  # This is the Porter stemmer  # TODO lemmatization might be better for this
    ]

    return preprocess_string(doc, preprocessing_filters)


def prepare_gensim_models():
    """
    Prepare TFIDF and LSA models for later similarity comparisons
    """
    # save plan ids to be able to get back to plan id from document index later
    plan_ids = [path.basename(plan_file_path) for plan_file_path in plan_file_paths]
    with open(path.join(OUTPUT_DIR, "plan_ids.json"), "w") as plan_id_file:
        json.dump(plan_ids, plan_id_file)

    documents = [open(plan_file_path).read() for plan_file_path in plan_file_paths]

    # Run preprocessing
    preprocessed_documents = [preprocess(doc) for doc in documents]

    dictionary = corpora.Dictionary(preprocessed_documents)

    dictionary.save(path.join(OUTPUT_DIR, "plans.dict"))

    corpus = [dictionary.doc2bow(text) for text in preprocessed_documents]
    # Maybe save corpus
    # corpora.MmCorpus.serialize('/tmp/deerwester.mm', corpus)  # store to disk, for later use

    # Models #

    ## TFIDF

    tfidf = models.TfidfModel(corpus)

    corpus_tfidf = tfidf[corpus]
    tfidf_index = similarities.MatrixSimilarity(tfidf[corpus])

    tfidf.save(path.join(OUTPUT_DIR, "tfidf.model"))
    tfidf_index.save(path.join(OUTPUT_DIR, "tfidf.index"))

    # LSI
    lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=300)

    lsi_index = similarities.MatrixSimilarity(lsi[corpus])
    lsi.save(path.join(OUTPUT_DIR, "lsi.model"))
    lsi_index.save(path.join(OUTPUT_DIR, "lsi.index"))


if __name__ == "__main__":
    prepare_gensim_models()
