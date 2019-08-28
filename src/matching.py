import json
from functools import lru_cache, partial
from os import path

from fuzzywuzzy import fuzz
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
from unidecode import unidecode

DIRNAME = path.dirname(path.realpath(__file__))

GENSIM_V1_MODELS_PATH = path.abspath(path.join(DIRNAME, "models/gensim_strategy_v1"))
GENSIM_V2_MODELS_PATH = path.abspath(path.join(DIRNAME, "models/gensim_strategy_v2"))


class Strategy:
    """
    Defines strategies used for matching posts to plans

    Strategies must each accept a plans list and a post object and return a best_match dict

    Each strategy must adhere to the following contract

    :param plans: List of plan dicts
    :type plans: list of dict
    :param post: Post object
    :type post: reddit_util.Comment/reddit_util.Submission
    :param threshold: Confidence threshold between 0-100. If confidence > threshold, then the plan is considered a match
    :type threshold: int
    :return: {
        "match": plan id if the plan is considered a match, otherwise None
        "confidence": the confidence that the plan is a match (0 - 100)
        "plan": the best matching plan
        # Can include other metadata about the match here
    }
    """

    @staticmethod
    def token_sort_ratio(plans: list, post, threshold=50):
        """
        Match plans based on hardcoded plan topics, using fuzzywuzzy's token_sort_ratio for fuzzy matching
        """

        match_confidence = 0
        match = None

        for plan in plans:
            plan_match_confidence = fuzz.token_sort_ratio(
                post.text.lower(), plan["topic"].lower()
            )

            if plan_match_confidence > match_confidence:
                # Update match
                match_confidence = plan_match_confidence
                match = plan

        return {
            "match": match["id"] if match_confidence > threshold else None,
            "confidence": match_confidence,
            "plan": match,
            # Can include other metadata about the match here
        }

    @staticmethod
    # TODO allow thresholds
    def _composite_strategy(plans: list, post, strategies: list):
        """
        Run strategies in order until one has a match
        """
        for strategy in strategies:
            match_info = strategy(plans, post)
            if match_info["match"]:
                return match_info
        return match_info

    @staticmethod
    @lru_cache(maxsize=8)
    def _load_gensim_models(model_name, model, similarity, model_path):
        plan_ids = json.load(open(path.join(model_path, "plan_ids.json")))

        dictionary = corpora.Dictionary.load(path.join(model_path, "plans.dict"))

        index = similarity.load(path.join(model_path, f"{model_name}.index"))
        model = model.load(path.join(model_path, f"{model_name}.model"))

        return plan_ids, dictionary, index, model

    @staticmethod
    def _gensim_similarity(
        plans: list,
        post,
        model_name,
        model,
        similarity,
        threshold,
        model_path=GENSIM_V1_MODELS_PATH,
    ):
        plan_ids, dictionary, index, model = Strategy._load_gensim_models(
            model_name, model, similarity, model_path
        )

        preprocessed_post = Preprocess.preprocess_gensim_v1(post.text)

        vec_post = dictionary.doc2bow(preprocessed_post)

        # find similar plans
        sims = index[model[vec_post]]
        # sort by descending match
        sims = list(sorted(enumerate(sims), key=lambda item: -item[1]))

        top_similarity = sims[0]

        matched_plan_id = plan_ids[top_similarity[0]]
        match_confidence = top_similarity[1] * 100

        match = [p for p in plans if p["id"] == matched_plan_id][0]

        return {
            "match": matched_plan_id if match_confidence > threshold else None,
            "confidence": match_confidence,
            "plan": match,
            # Can include other metadata about the match here
        }

    @staticmethod
    def token_sort_lsi_v1_composite(plans: list, post, threshold=60):
        """
        Tries the following strategies in order:
         1) fuzzy matching based on hardcoded topics
         2) LSI using gensim models
        """

        return Strategy._composite_strategy(
            plans,
            post,
            [
                partial(Strategy.token_sort_ratio, threshold=threshold),
                partial(Strategy.lsi_gensim_v1, threshold=80),
            ],
        )

    @staticmethod
    def lsi_gensim_v1(plans: list, post, threshold=80):
        """
        LSI – Latent Semantic Indexing  (aka Latent Semantic Analysis)

        Using gensim

        Models have been precomputed using ../scripts/update_gensim_models_v1.py
        """
        return Strategy._gensim_similarity(
            plans,
            post,
            "lsi",
            models.LsiModel,
            similarities.MatrixSimilarity,
            threshold,
        )

    @staticmethod
    def lsa_gensim_v2(plans: list, post, threshold=80):
        """
        LSI – Latent Semantic Indexing  (aka Latent Semantic Analysis)

        This version includes the hand-written topics from plans.json in the corpus
        of documents posts are matched against

        Models have been precomputed using ../scripts/update_gensim_models_v2.py
        """
        return Strategy._gensim_similarity(
            plans,
            post,
            "lsa",
            models.LsiModel,
            similarities.MatrixSimilarity,
            threshold,
            model_path=GENSIM_V2_MODELS_PATH,
        )

    @staticmethod
    def tfidf_gensim_v2(plans: list, post, threshold=20):
        """
        TFIDF – Term Frequency–Inverse Document Frequency

        Using gensim

        Models have been precomputed using ../scripts/update_gensim_models_v2.py
        """
        return Strategy._gensim_similarity(
            plans,
            post,
            "tfidf",
            models.TfidfModel,
            similarities.MatrixSimilarity,
            threshold,
            model_path=GENSIM_V2_MODELS_PATH,
        )


class Preprocess:
    """
    Defines strategies used for preprocessing text before model building and similarity scoring

    Strategies must each accept a string and return a string
    """

    @staticmethod
    def _remove_custom_stopwords(s):
        return " ".join(
            w
            for w in s.split()
            if w.lower()
            not in {
                "elizabeth",
                "warren",
                "plan",
                "warrenplanbot",
                "warrenplanbotdev",
                "sen",
                "senator",
            }
        )

    @staticmethod
    def preprocess_gensim_v1(doc):
        # Run preprocessing
        preprocessing_filters = [
            unidecode,
            lambda x: x.lower(),
            strip_punctuation,
            strip_multiple_whitespaces,
            strip_numeric,
            remove_stopwords,
            Preprocess._remove_custom_stopwords,
            strip_short,  # remove words shorter than 3 chars
            stem_text,  # This is the Porter stemmer
        ]

        return preprocess_string(doc, preprocessing_filters)

    # TODO try a preprocessed that does lemmatization
