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

    def test_show_me_the_plans(self):
        assert (
            RuleStrategy.request_plan_list(
                [], mock_comment("!WarrenPlanBot show me the plans")
            )
            == self.show_me_the_plans_operation
        )

        assert (
            RuleStrategy.request_plan_list(
                [],
                mock_comment(
                    "!WarrenPlanBot show me the plans\n\nI want to show the world the plans"
                ),
            )
            == self.show_me_the_plans_operation
        )

        assert (
            RuleStrategy.request_plan_list(
                [],
                mock_comment(
                    "I love to show people the plans\n!WarrenPlanBot show me the plans\n\nI want to show the world the plans"
                ),
            )
            == self.show_me_the_plans_operation
        )

        assert (
            RuleStrategy.request_plan_list(
                [],
                mock_comment(
                    "!WarrenPlanBot\n\nYou know I love you now show me the plans"
                ),
            )
            == self.show_me_the_plans_operation
        )

        assert (
            RuleStrategy.request_plan_list(
                [],
                mock_comment("!WarrenPlanBot show me the plans about something I love"),
            )
            is None
        )
