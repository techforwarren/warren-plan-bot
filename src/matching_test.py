from matching import Preprocess, RuleStrategy


class MockComment:
    def __init__(self):
        self.text = "text of comment"


def mock_comment(text):
    comment = MockComment()
    comment.text = text
    return comment


VERBATIMS = [
    {"id": "basic_help", "text": ""},
    {"id": "advanced_help", "text": ""},
    {"id": "why_warren", "text": ""},
]


class TestRuleStrategy:
    show_me_the_plans_operation = {"operation": "all_the_plans"}
    help_operation = {"operation": "verbatim", "verbatim": VERBATIMS[0]}
    advanced_help_operation = {"operation": "verbatim", "verbatim": VERBATIMS[1]}
    why_warren_operation = {"operation": "verbatim", "verbatim": VERBATIMS[2]}

    def test_show_me_the_plans(self):
        assert (
            RuleStrategy.request_plan_list([], "show me the plans")
            == self.show_me_the_plans_operation
        )

        assert (
            RuleStrategy.request_plan_list(
                [], "show me the plans\n\nI want to show the world the plans"
            )
            == self.show_me_the_plans_operation
        )

        assert (
            RuleStrategy.request_plan_list(
                [], "show me the plans\n\nI want to show the world the plans"
            )
            == self.show_me_the_plans_operation
        )

        assert (
            RuleStrategy.request_plan_list(
                [], "You know I love you now show me the plans"
            )
            == self.show_me_the_plans_operation
        )

        assert (
            RuleStrategy.request_plan_list(
                [], "show me the plans\n\nE: It looks like /u/WarrenPlanBot is offline"
            )
            == self.show_me_the_plans_operation
        )

        assert (
            RuleStrategy.request_plan_list(
                [], "show me the plans about something I love"
            )
            is None
        )

    def test_help(self):
        assert RuleStrategy.match_verbatim(VERBATIMS, "help") == self.help_operation

        assert (
            RuleStrategy.match_verbatim(VERBATIMS, "help\nthanks in advance")
            == self.help_operation
        )

        assert RuleStrategy.match_verbatim(VERBATIMS, "show me the plans") is None

    def test_advanced_help(self):
        assert (
            RuleStrategy.match_verbatim(VERBATIMS, "advanced help")
            == self.advanced_help_operation
        )

        assert (
            RuleStrategy.match_verbatim(VERBATIMS, "advanced help\nthanks in advance")
            == self.advanced_help_operation
        )

        assert (
            RuleStrategy.match_verbatim(VERBATIMS, "advanced show me the plans") is None
        )

    def test_why_warren(self):
        assert (
            RuleStrategy.match_verbatim(VERBATIMS, "", {"why_warren": True})
            == self.why_warren_operation
        )

        assert RuleStrategy.match_verbatim(VERBATIMS, "", {"why_warren": False}) is None

        assert (
            RuleStrategy.match_verbatim(VERBATIMS, "why warren", {"why_warren": False})
            == self.why_warren_operation
        )


class TestPreprocess:
    def test_bigrams(self):
        assert Preprocess.bigrams(["foo", "bar", "baz"]) == ["foo bar", "bar baz"]
