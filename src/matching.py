from fuzzywuzzy import fuzz


class Strategy:
    """
    Contains methods which accept a plans list and a post object and return a best_match dict
        return {
            "is_match": whether the plan should be considered a match
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
            "is_match": match_confidence > threshold,
            "confidence": match_confidence,
            "plan": match,
            # Can include other metadata about the match here
        }
