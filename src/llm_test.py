from unittest import mock

from llm import build_plan_response_text
from plan_bot_test import mock_plan


def test_build_plan_response_text(mock_plan):
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
                            "role": "assistant",
                        },
                        "index": 0,
                        "finish_reason": "stop",
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
        response_text = build_plan_response_text(mock_plan, "foobarbaz")
    assert "This is indeed a test" == response_text


def test_build_plan_response_text_on_error(mock_plan):
    with mock.patch(
        "openai.ChatCompletion.create", side_effect=ValueError("foo")
    ) as mock_chat_completion:
        response_text = build_plan_response_text(mock_plan, "foobarbaz")
    assert None is response_text


def test_build_plan_response_text_on__early_stop(mock_plan):
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
                            "role": "assistant",
                        },
                        "index": 0,
                        "finish_reason": "foo",  # anything but stop
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
        response_text = build_plan_response_text(mock_plan, "foobarbaz")
        assert None is response_text
