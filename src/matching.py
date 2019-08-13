from fuzzywuzzy import fuzz


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

        match_confidence = 0
        match = None

        for plan in plans:
            plan_match_confidence = fuzz.token_sort_ratio(post.text, plan["topic"])

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
