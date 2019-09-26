import pytest

from matching import RuleStrategy, get_trigger_line


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

    def test_help(self):
        assert (
            RuleStrategy.request_help([], mock_comment("!WarrenPlanBot help"))
            == self.help_operation
        )

        assert (
            RuleStrategy.request_help(
                [], mock_comment("blah blah\n!WarrenPlanBot help\nthanks in advance")
            )
            == self.help_operation
        )

        assert (
            RuleStrategy.request_help(
                [], mock_comment("!WarrenPlanBot show me the plans")
            )
            is None
        )


def test_get_trigger_line():
    assert (
        get_trigger_line(
            "i love liz warren\n!WarrenPlAnBot do you love Liz too?\ntell me the truth"
        )
        == "do you love Liz too?"
    )

    assert (
        get_trigger_line(
            "I like it here\n!WarrenPlAnBot do you?\n!WarrenPlAnBot do you really?"
        )
        == "do you really?"
    )

    assert get_trigger_line("!WarrenPlanBot, what's up?") == "what's up?"
    assert get_trigger_line("!WarrenPlanBot,what's good?") == "what's good?"
