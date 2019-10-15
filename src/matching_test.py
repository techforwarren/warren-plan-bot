import pytest

from matching import RuleStrategy

class MockComment:
    def __init__(self):
        self.text = "text of comment"


def mock_comment(text):
    comment = MockComment()
    comment.text = text
    return comment


class TestRuleStrategy:
    show_me_the_plans_operation = {"operation": "all_the_plans"}
    help_operation = {"operation": "help"}
    advanced_help_operation = {"operation": "advanced_help"}

    def test_show_me_the_plans(self):
        assert (
            RuleStrategy.request_plan_list(
                [], "show me the plans"
            )
            == self.show_me_the_plans_operation
        )

        assert (
            RuleStrategy.request_plan_list(
                [], "show me the plans\n\nI want to show the world the plans",
            )
            == self.show_me_the_plans_operation
        )

        assert (
            RuleStrategy.request_plan_list(
                [],
                "show me the plans\n\nI want to show the world the plans",
            )
            == self.show_me_the_plans_operation
        )

        assert (
            RuleStrategy.request_plan_list(
                [],
                "You know I love you now show me the plans",
            )
            == self.show_me_the_plans_operation
        )

        assert (
            RuleStrategy.request_plan_list(
                [],
                "show me the plans\n\nE: It looks like /u/WarrenPlanBot is offline",
            )
            == self.show_me_the_plans_operation
        )

        assert (
            RuleStrategy.request_plan_list(
                [],
                "show me the plans about something I love",
            )
            is None
        )

    def test_help(self):
        assert (
            RuleStrategy.request_help([], "help")
            == self.help_operation
        )

        assert (
            RuleStrategy.request_help(
                [], "help\nthanks in advance"
            )
            == self.help_operation
        )

        assert (
            RuleStrategy.request_help(
                [], "show me the plans"
            )
            is None
        )

    def test_advanced_help(self):
        assert (
            RuleStrategy.request_help([], "advanced help")
            == self.advanced_help_operation
        )

        assert (
            RuleStrategy.request_help(
                [], "advanced help\nthanks in advance"
            )
            == self.advanced_help_operation
        )

        assert (
            RuleStrategy.request_help(
                [], "advanced show me the plans"
            )
            is None
        )
