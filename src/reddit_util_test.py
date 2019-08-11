from unittest import mock

import pytest

import reddit_util


def _mock_submission():
    mock_submission = mock.MagicMock()
    mock_submission.self_text = "text of submission"
    mock_submission.reply.return_value = "a comment"
    del mock_submission.non_existent  # avoid magic mock's magic
    return mock_submission


@pytest.fixture
def mock_submission():
    return _mock_submission()


@pytest.fixture
def mock_comment():
    mock_comment = mock.MagicMock()
    mock_comment.body = "text of comment"
    mock_comment.submission = _mock_submission()
    mock_comment.reply.return_value = "a comment"
    del mock_comment.non_existent  # avoid magic mock's magic
    return mock_comment


class TestSubmission:
    def test_text(self, mock_submission):
        submission = reddit_util.Submission(mock_submission)
        assert submission.text == "text of submission", "text attribute added"
        assert submission.self_text == "text of submission", "self_text preserved"

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
        assert comment.submission.self_text == "text of submission"

    def test_nonexistent_attribute(self, mock_comment):
        comment = reddit_util.Comment(mock_comment)
        with pytest.raises(AttributeError):
            comment.non_existent
