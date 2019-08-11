from unittest import mock

import pytest

import reddit_util


class MockSubmission:
    def __init__(self):
        self.selftext = "text of submission"
        self.reply = mock.Mock()
        self.reply.return_value = "a comment"


class MockComment:
    def __init__(self):
        self.body = "text of comment"
        self.submission = MockSubmission()
        self.reply = mock.Mock()
        self.reply.return_value = "a comment"


@pytest.fixture
def mock_submission():
    return MockSubmission()


@pytest.fixture
def mock_comment():
    return MockComment()


class TestSubmission:
    def test_text(self, mock_submission):
        submission = reddit_util.Submission(mock_submission)
        assert submission.text == "text of submission", "text attribute added"
        assert submission.selftext == "text of submission", "selftext preserved"

    def test_type(self, mock_submission):
        submission = reddit_util.Submission(mock_submission)
        assert submission.type == "submission"

    def test_reply(self, mock_submission):
        submission = reddit_util.Submission(mock_submission)
        reply = submission.reply("a nice reply")
        assert reply == "a comment"
        mock_submission.reply.assert_called_once_with("a nice reply")

    def test_nonexistent_attribute(self, mock_submission):
        submission = reddit_util.Submission(mock_submission)
        with pytest.raises(AttributeError):
            submission.non_existent


class TestComment:
    def test_text(self, mock_comment):
        comment = reddit_util.Comment(mock_comment)
        assert comment.text == "text of comment", "text attribute added"
        assert comment.body == "text of comment", "body preserved"

    def test_type(self, mock_comment):
        comment = reddit_util.Comment(mock_comment)
        assert comment.type == "comment"

    def test_reply(self, mock_comment):
        comment = reddit_util.Comment(mock_comment)
        reply = comment.reply("a nice reply")
        assert reply == "a comment"
        mock_comment.reply.assert_called_once_with("a nice reply")

    def test_submission(self, mock_comment):
        comment = reddit_util.Comment(mock_comment)
        assert type(comment.submission) == reddit_util.Submission
        assert comment.submission.text == "text of submission"
        assert comment.submission.selftext == "text of submission"

    def test_nonexistent_attribute(self, mock_comment):
        comment = reddit_util.Comment(mock_comment)
        with pytest.raises(AttributeError):
            comment.non_existent
