from unittest import mock

import pytest

import plan_bot


class MockSubmission:
    def __init__(self):
        self.id = "123"
        self.text = "text of submission"
        self.type = "submission"
        self.reply = mock.Mock()
        self.reply.return_value = "a comment"


class MockComment:
    def __init__(self):
        self.id = "456"
        self.text = "text of comment"
        self.type = "comment"
        self.submission = MockSubmission()
        self.reply = mock.Mock()
        self.reply.return_value = "a comment"


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


def test_build_response_text_to_comment(mock_comment, mock_submission, mock_plan):
    response_text = plan_bot.build_response_text(mock_plan, mock_comment)
    assert type(response_text) is str
    assert mock_plan["display_title"] in response_text
    assert mock_plan["url"] in response_text
    assert mock_plan["summary"] in response_text
    assert mock_submission.id in response_text
    assert mock_comment.id in response_text


def test_build_response_text_to_submission(mock_comment, mock_submission, mock_plan):
    response_text = plan_bot.build_response_text(mock_plan, mock_submission)
    assert type(response_text) is str
    assert mock_plan["display_title"] in response_text
    assert mock_plan["url"] in response_text
    assert mock_plan["summary"] in response_text
    assert mock_submission.id in response_text
    assert mock_comment.id not in response_text


@pytest.mark.skip("Needs tests")
def test_process_post():
    pass
