import datetime
from unittest import mock

import pytest

import plan_bot


class MockSubreddit:
    def __init__(self):
        self.name = "id2wpbsandbox"


class MockAuthor:
    def __init__(self):
        self.name = "aredditusername"


class MockSubmission:
    def __init__(self, text="text of submission", locked=False):
        self.id = "123"
        self.text = text
        self.title = "title"
        self.type = "submission"
        self.permalink = "http://post.post"
        self.reply = mock.Mock()
        self.reply.return_value = "a comment"
        self.locked = locked
        self.author = MockAuthor()


class MockComment:
    def __init__(self, text="text of comment"):
        self.id = "456"
        self.text = text
        self.type = "comment"
        self.permalink = "http://post.post"
        self.submission = MockSubmission()
        self.reply = mock.Mock()
        self.reply.return_value = "a comment"
        self.subreddit = MockSubreddit()


PLANS = [
    {
        "id": "century_21",
        "topic": "21st century title",
        "summary": "The best century",
        "display_title": "A Title for the 21st Century",
        "url": "plan.plan",
        "full_text": "foo",
    },
    {
        "id": "another_plan",
        "topic": "another plan",
        "summary": "This is another plan",
        "display_title": "Another Title To Really Make a Person Think",
        "url": "anotherplan.plan",
        "full_text": "bar",
    },
]

VERBATIMS = [
    {"id": "why_warren", "text": "This is verbatim."},
    {"id": "basic_help", "text": "Basic help."},
    {"id": "advanced_help", "text": "Advanced help."},
]


@pytest.fixture
def mock_submission():
    return MockSubmission()


@pytest.fixture
def mock_comment():
    return MockComment()


@pytest.fixture
def mock_plan():
    return {
        "id": "my_plan",
        "topic": "a plan topic",
        "summary": "a summary",
        "display_title": "Plan Title",
        "url": "http://plan.plan",
        "full_text": "foo bar",
        "is_cluster": False,
    }


@pytest.fixture
def mock_plan_cluster():
    return {
        "display_title": "Plan Cluster Title",
        "is_cluster": True,
        "plans": [
            {
                "summary": "a summary",
                "display_title": "SubPlan Title",
                "url": "http://subplan.plan",
            },
            {
                "summary": "another summary",
                "display_title": "SubPlan 2 Title",
                "url": "http://subplan2.plan",
            },
        ],
    }


def test_reply_default(mock_comment):
    return_val = plan_bot.reply(mock_comment, "post body")
    mock_comment.reply.assert_not_called()
    assert not return_val


def test_reply_simulated(mock_comment):
    return_val = plan_bot.reply(mock_comment, "post body", simulate=True)
    mock_comment.reply.assert_not_called()
    assert return_val is True


def test_reply_send(mock_comment):
    return_val = plan_bot.reply(mock_comment, "post body", send=True)
    mock_comment.reply.assert_called_once_with("post body")
    assert return_val is True


def test_reply_send_and_simulate(mock_comment):
    """
    When both send and simulate are true, it should be the same behavior as simulate

    Ideally this will never happen, but better to be safe
    """
    return_val = plan_bot.reply(mock_comment, "post body", simulate=True, send=True)
    mock_comment.reply.assert_not_called()
    assert return_val is True


def test_build_response_text_pure_plan_with_llm(mock_plan):
    with mock.patch(
        "llm.build_llm_plan_response_text",
        return_value="hamspameggs",
    ) as mock_chat_completion:
        response_text, reply_type = plan_bot.build_plan_response_text(
            mock_plan, "foobarbaz"
        )
    assert type(response_text) is str
    assert "hamspameggs" in response_text
    assert reply_type == "plan_llm"

def test_build_response_text_pure_plan_fallback_to_static_text(mock_plan):
    with mock.patch(
            "llm.build_llm_plan_response_text",
            return_value=None,
    ) as mock_chat_completion:
        response_text, reply_type = plan_bot.build_plan_response_text(
            mock_plan, "foobarbaz"
        )
    assert type(response_text) is str
    assert mock_plan["display_title"] in response_text
    assert mock_plan["url"] in response_text
    assert mock_plan["summary"] in response_text
    assert reply_type == "plan"
def test_build_response_text_pure_plan_llm_fallback_to_static_text_on_early_stop(mock_plan):
    with mock.patch(
            "openai.ChatCompletion.create",
            return_value=(
                    {
                        "id": "chatcmpl-uqkvlQyYK7bGYrRHQ0eXlWi7",
                        "object": "chat.completion",
                        "created": 1589478378,
                        "model": "gpt-3.5-turbo",
                        "choices": [
                            {
                                "message": {
                                    "content": "This is indeed a test",
                                    "role": "assistant"
                                },
                                "index": 0,
                                "finish_reason": "foo", # anything but stop
                            }
                        ],
                        "usage": {
                            "prompt_tokens": 5,
                            "completion_tokens": 7,
                            "total_tokens": 12,
                        },
                    }
            ),
    ) as mock_chat_completion:
        response_text, reply_type = plan_bot.build_plan_response_text(
            mock_plan, "foobarbaz"
        )
    assert type(response_text) is str
    assert mock_plan["display_title"] in response_text
    assert mock_plan["url"] in response_text
    assert mock_plan["summary"] in response_text
    assert reply_type == "plan"

def test_build_no_match_response_text(mock_submission, mock_plan):
    response_text = plan_bot.build_no_match_response_text(
        [{"plan": mock_plan}], mock_submission
    )
    assert type(response_text) is str
    assert f"[{mock_plan['display_title']}]({mock_plan['url']})" in response_text
    assert mock_plan["summary"] not in response_text


def test_build_no_match_response_text_no_potential_matches(mock_submission, mock_plan):
    response_text = plan_bot.build_no_match_response_text([], mock_submission)
    assert type(response_text) is str


def test_build_response_text_to_submission_with_plan_cluster(
    mock_submission, mock_plan_cluster
):
    response_text, reply_type = plan_bot.build_plan_response_text(
        mock_plan_cluster, mock_submission
    )
    assert type(response_text) is str
    assert mock_plan_cluster["display_title"] in response_text
    for plan in mock_plan_cluster["plans"]:
        assert plan["display_title"] in response_text
        assert plan["url"] in response_text
    assert reply_type == "plan_cluster"


def test_build_response_text_to_all_the_plans_operation(
    mock_submission, mock_plan, mock_plan_cluster
):
    response_text = plan_bot.build_all_plans_response_text(
        [mock_plan] * 5 + [mock_plan_cluster] * 3
    )

    assert type(response_text) is str

    assert mock_plan["display_title"] in response_text
    assert mock_plan["url"] in response_text

    assert mock_plan_cluster["display_title"] not in response_text
    for plan in mock_plan_cluster["plans"]:
        assert plan["display_title"] not in response_text
        assert plan["url"] not in response_text


def test_build_response_text_to_state_of_race_operation(
    mock_submission, mock_plan, mock_plan_cluster
):
    response_text = plan_bot.build_state_of_race_response_text(
        datetime.date(2020, 2, 23)
    )

    assert type(response_text) is str

    assert "Feb 23rd" in response_text
    assert "101" in response_text  # pledged so far
    assert "97%" in response_text  # percent so far
    assert "3,979" in response_text  # total

    # before SC
    response_text = plan_bot.build_state_of_race_response_text(
        datetime.date(2020, 2, 27)
    )
    assert "Feb 27th" in response_text
    assert "101" in response_text  # pledged so far
    assert "97%" in response_text  # percent so far
    assert "3,979" in response_text  # total

    # day of SC
    response_text = plan_bot.build_state_of_race_response_text(
        datetime.date(2020, 2, 29)
    )
    assert "Feb 29th" in response_text
    assert "101" in response_text  # pledged so far
    assert "97%" in response_text  # percent so far
    assert "3,979" in response_text  # total


@mock.patch("plan_bot.create_db_record")
@mock.patch(
    "plan_bot.build_plan_response_text", return_value=("response text", "reply_type")
)
@mock.patch("plan_bot.reply")
@pytest.mark.parametrize(
    ["post_text", "expected_matching_plan"],
    [
        ("!WarrenPlanBot A Title for the 21st Century", PLANS[0]),
        ("!WarrenPlanBot Another Title To Really Make a Person Think", PLANS[1]),
        ("!WarrenPlanBot  another title to really make a Person Think   ", PLANS[1]),
    ],
)
def test_process_post_matches_by_display_title(
    mock_reply,
    mock_build_response_text,
    mock_create_db_record,
    post_text,
    expected_matching_plan,
):
    post = MockSubmission(post_text)

    plan_bot.process_post(post, PLANS, VERBATIMS, posts_db=mock.MagicMock())

    mock_build_response_text.assert_called_once_with(expected_matching_plan, post.text)
    mock_reply.assert_called_once_with(
        post, "response text", send=False, simulate=False, parent=False
    )


@mock.patch("plan_bot.create_db_record")
@mock.patch(
    "plan_bot.build_plan_response_text", return_value=("response text", "reply_type")
)
@mock.patch("plan_bot.reply")
@pytest.mark.parametrize(
    ["post_text", "expected_matching_plan"],
    [
        (
            "!WarrenPlanBot --tell-parent another title to really make a Person Think   ",
            PLANS[1],
        ),
        (
            "!WarrenPlanBot --parent another title to really make a Person Think   ",
            PLANS[1],
        ),
    ],
)
def test_process_post_matches_by_display_title_with_parent_option(
    mock_reply,
    mock_build_response_text,
    mock_create_db_record,
    post_text,
    expected_matching_plan,
):
    post = MockSubmission(post_text)

    plan_bot.process_post(post, PLANS, VERBATIMS, posts_db=mock.MagicMock())

    mock_build_response_text.assert_called_once_with(expected_matching_plan, post.text)

    mock_reply.assert_called_once_with(
        post,
        "/u/aredditusername asked me to chime in!\n\nresponse text",
        send=False,
        simulate=False,
        parent=True,
    )


@mock.patch("plan_bot.create_db_record")
@mock.patch("plan_bot.build_verbatim_response_text", return_value="response text")
@mock.patch("plan_bot.reply")
@pytest.mark.parametrize(
    ["post_text", "expected_verbatim"],
    [
        ("!WarrenPlanBot --why-warren", VERBATIMS[0]),
        ("!WarrenPlanBot help", VERBATIMS[1]),
        ("!WarrenPlanBot advanced help", VERBATIMS[2]),
    ],
)
def test_process_post_matches_by_verbatim(
    mock_reply,
    mock_build_response_text,
    mock_create_db_record,
    post_text,
    expected_verbatim,
):
    post = MockSubmission(post_text)

    plan_bot.process_post(post, PLANS, VERBATIMS, posts_db=mock.MagicMock())

    mock_build_response_text.assert_called_once_with(expected_verbatim)
    mock_reply.assert_called_once_with(
        post, "response text", send=False, simulate=False, parent=False
    )


@mock.patch("plan_bot.create_db_record")
@mock.patch("plan_bot.build_verbatim_response_text", return_value="response text")
@mock.patch("plan_bot.reply")
@pytest.mark.parametrize(
    ["post_text", "expected_verbatim"],
    [
        ("!WarrenPlanBot --parent --why-warren", VERBATIMS[0]),
        ("!WarrenPlanBot --why-warren --tell-parent", VERBATIMS[0]),
    ],
)
def test_process_post_matches_by_verbatim_with_parent_option(
    mock_reply,
    mock_build_response_text,
    mock_create_db_record,
    post_text,
    expected_verbatim,
):
    post = MockSubmission(post_text)

    plan_bot.process_post(post, PLANS, VERBATIMS, posts_db=mock.MagicMock())

    mock_build_response_text.assert_called_once_with(expected_verbatim)

    mock_reply.assert_called_once_with(
        post,
        "/u/aredditusername asked me to chime in!\n\nresponse text",
        send=False,
        simulate=False,
        parent=True,
    )


@mock.patch("plan_bot.create_db_record")
@mock.patch("plan_bot.build_plan_response_text")
@mock.patch("plan_bot.reply")
def test_process_post_wont_reply_to_locked_post(
    mock_reply, mock_build_response_text, mock_create_db_record
):
    post = MockSubmission("!WarrenPlanBot A Title for the 21st Century")
    post.locked = True

    plan_bot.process_post(post, PLANS, VERBATIMS, posts_db=mock.MagicMock())

    mock_build_response_text.assert_not_called()
    mock_reply.assert_not_called()


@mock.patch("plan_bot.create_db_record")
@mock.patch(
    "plan_bot.build_plan_response_text",
    return_value=("some response text", "reply_type"),
)
@mock.patch("plan_bot.reply")
def test_process_post_matches_real_plan(
    mock_reply, mock_build_response_text, mock_create_db_record
):
    plans = [
        {
            "id": "universal_child_care",
            "topic": "universal child care",
            "summary": "We're the wealthiest country on the planet ...",
            "display_title": "Universal Child Care",
            "url": "https://medium.com/@teamwarren/my-plan-for-universal-child-care-762535e6c20a",
        }
    ]

    post = MockSubmission(
        "!WarrenPlanBot what's Senator Warren's plan to get child care to all the children who need it?"
    )

    plan_bot.process_post(post, plans, VERBATIMS, posts_db=mock.MagicMock())

    mock_build_response_text.assert_called_once_with(plans[0], post.text)
    mock_reply.assert_called_once_with(
        post, "some response text", send=False, simulate=False, parent=False
    )


@mock.patch("plan_bot.create_db_record")
@mock.patch(
    "plan_bot.build_plan_response_text", return_value=("response text", "reply_type")
)
@mock.patch("plan_bot.reply")
@pytest.mark.parametrize(
    "reddit_username", ["warrenplanbot", "warrenplanbotdev", "WarrenPlanBot"]
)
def test_process_post_wont_reply_to_warren_plan_bot(
    mock_reply, mock_build_response_text, mock_create_db_record, reddit_username
):
    plans = [
        {
            "id": "universal_child_care",
            "topic": "universal child care",
            "summary": "We're the wealthiest country on the planet ...",
            "display_title": "Universal Child Care",
            "url": "https://medium.com/@teamwarren/my-plan-for-universal-child-care-762535e6c20a",
        }
    ]

    post = MockSubmission(
        "!WarrenPlanBot what's Senator Warren's plan to get child care to all the children who need it?"
    )
    post.author.name = reddit_username

    plan_bot.process_post(post, plans, VERBATIMS, posts_db=mock.MagicMock())

    mock_build_response_text.assert_not_called()
    mock_reply.assert_not_called()


def test_get_trigger_line():
    assert (
        plan_bot.get_trigger_line(
            "i love liz warren\n!WarrenPlAnBot do you love Liz too?\ntell me the truth"
        )
        == "do you love Liz too?"
    )

    assert (
        plan_bot.get_trigger_line(
            "I like it here\n!WarrenPlAnBot do you?\n!WarrenPlAnBot do you really?"
        )
        == "do you really?"
    )

    assert plan_bot.get_trigger_line("!WarrenPlanBot, what's up?") == "what's up?"
    assert plan_bot.get_trigger_line("!WarrenPlanBot,what's good?") == "what's good?"
    assert (
        plan_bot.get_trigger_line(
            "/u/WarrenPlanBot hi\n!WarrenPlanBot,what's good?\n/u/WarrenPlanBot hi\nwarrenplanbot ho"
        )
        == "what's good?"
    )

    assert (
        plan_bot.get_trigger_line("!WarrenPlanBot, --tell-parent what's up?")
        == "--tell-parent what's up?"
    )
    assert (
        plan_bot.get_trigger_line("!WarrenPlanBot,--tell-parent what's up?")
        == "--tell-parent what's up?"
    )

    # only get first sentance
    assert (
        plan_bot.get_trigger_line("!WarrenPlanBot what's up? I heard nothing")
        == "what's up?"
    )

    assert plan_bot.get_trigger_line("!WarrenPlanBot what's up! Bees.") == "what's up!"

    assert (
        plan_bot.get_trigger_line("!WarrenPlanBot what's up. Do you know?")
        == "what's up."
    )


@pytest.mark.parametrize(
    "input,expected_rest,expected_flags",
    [
        ("what's up", "what's up", set()),
        ("--tell-parent what's up", "what's up", {"parent"}),
        ("--parent what's up", "what's up", {"parent"}),
        ("--why-warren what's up", "what's up", {"why_warren"}),
        ("-parent what's up", "what's up", set()),
        ("--parnet what's up", "what's up", set()),
        ("--tell-parent, what's up", "what's up", set()),
        ("--parent --why-warren what's up", "what's up", {"parent", "why_warren"}),
        ("--why-warren --parent what's up", "what's up", {"parent", "why_warren"}),
        ("--state-of-race what's up", "what's up", {"state_of_race"}),
        ("--state-of-the-race what's up", "what's up", {"state_of_race"}),
    ],
)
def test_process_flags(input, expected_rest, expected_flags):
    assert plan_bot.process_flags(input) == (expected_rest, expected_flags)
