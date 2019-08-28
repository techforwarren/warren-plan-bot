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
    },
    {
        "id": "another_plan",
        "topic": "another plan",
        "summary": "This is another plan",
        "display_title": "Another Title To Really Make a Person Think",
        "url": "anotherplan.plan",
    },
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
        "summary": "a summary",
        "display_title": "Plan Title",
        "url": "http://plan.plan",
    }


@pytest.fixture
def mock_plan_cluster():
    return {
        "display_title": "Plan Title",
        "is_cluster": True,
        "plans": [
            {
                "summary": "a summary",
                "display_title": "Plan Title",
                "url": "http://plan.plan",
            },
            {
                "summary": "another summary",
                "display_title": "Plan 2 Title",
                "url": "http://plan2.plan",
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


def test_build_response_text_to_comment(mock_comment, mock_plan):
    response_text = plan_bot.build_response_text(mock_plan, mock_comment)
    assert type(response_text) is str
    assert mock_plan["display_title"] in response_text
    assert mock_plan["url"] in response_text
    assert mock_plan["summary"] in response_text
    assert mock_comment.permalink in response_text


def test_build_response_text_to_submission(mock_submission, mock_plan):
    response_text = plan_bot.build_response_text(mock_plan, mock_submission)
    assert type(response_text) is str
    assert mock_plan["display_title"] in response_text
    assert mock_plan["url"] in response_text
    assert mock_plan["summary"] in response_text
    assert mock_submission.permalink in response_text


def test_build_no_match_response_text(mock_submission, mock_plan):
    response_text = plan_bot.build_no_match_response_text(
        [{"plan": mock_plan}], mock_submission
    )
    assert type(response_text) is str
    assert f"!WarrenPlanBot {mock_plan['display_title']}" in response_text
    assert mock_plan["url"] not in response_text
    assert mock_plan["summary"] not in response_text
    assert mock_submission.permalink in response_text


def test_build_no_match_response_text_no_potential_matches(mock_submission, mock_plan):
    response_text = plan_bot.build_no_match_response_text([], mock_submission)
    assert type(response_text) is str
    assert mock_submission.permalink in response_text


def test_build_response_text_to_submission_with_plan_cluster(
    mock_submission, mock_plan_cluster
):
    response_text = plan_bot.build_response_text(mock_plan_cluster, mock_submission)
    assert type(response_text) is str
    assert mock_plan_cluster["display_title"] in response_text
    for plan in mock_plan_cluster["plans"]:
        assert plan["display_title"] in response_text
        assert plan["url"] in response_text
    assert mock_submission.permalink in response_text


@mock.patch("plan_bot.create_db_record")
@mock.patch("plan_bot.build_response_text", return_value="response text")
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

    plan_bot.process_post(post, PLANS, posts_db=mock.MagicMock())

    mock_build_response_text.assert_called_once_with(expected_matching_plan, post)
    mock_reply.assert_called_once_with(
        post, "response text", send=False, simulate=False
    )


@mock.patch("plan_bot.create_db_record")
@mock.patch("plan_bot.build_response_text")
@mock.patch("plan_bot.reply")
def test_process_post_wont_reply_to_locked_post(
    mock_reply, mock_build_response_text, mock_create_db_record
):

    post = MockSubmission("!WarrenPlanBot A Title for the 21st Century")
    post.locked = True

    plan_bot.process_post(post, PLANS, posts_db=mock.MagicMock())

    mock_build_response_text.assert_not_called()
    mock_reply.assert_not_called()


@mock.patch("plan_bot.create_db_record")
@mock.patch("plan_bot.build_response_text", return_value="some response text")
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

    plan_bot.process_post(post, plans, posts_db=mock.MagicMock())

    mock_build_response_text.assert_called_once_with(plans[0], post)
    mock_reply.assert_called_once_with(
        post, "some response text", send=False, simulate=False
    )


@mock.patch("plan_bot.create_db_record")
@mock.patch("plan_bot.build_response_text", return_value="some response text")
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

    plan_bot.process_post(post, plans, posts_db=mock.MagicMock())

    mock_build_response_text.assert_not_called()
    mock_reply.assert_not_called()
