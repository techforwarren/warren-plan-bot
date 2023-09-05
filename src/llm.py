import logging
from typing import Optional

import openai

from plans import PurePlan

MODEL = "gpt-3.5-turbo-16k"  # Need at least 12k tokens in order to fit largest plans

logger = logging.getLogger(__name__)


class Prompts:
    @staticmethod
    def matched_plan_user_prompt(user_input: str, plan: PurePlan) -> str:
        """
        Prompt to use when a single plan has been matched to user's input
        This provides detailed context about the specific plan matched

        This should be provided as the 'user' role

        Inspired by the text qa user prompt from llama_index
        https://github.com/jerryjliu/llama_index/blob/647a9fff672b10f20c34f2b8b23a79930775c827/llama_index/prompts/chat_prompts.py#L23-L33
        """
        return f"""Context information is below.

---------------------\n
The title of Senator Warren's plan: "{plan['display_title']}" 

A summary of this plan: {plan['summary']}

The full text of this plan is:

{plan['full_text']}
-----------
Given the context information and not prior knowledge, answer the question.

Query: {user_input}"
Answer: 
"""

    @staticmethod
    def planbot_system_prompt():
        """
        Prompt to use to set up the general context of the plan bot behavior

        This should be provided as the 'system' role

        Inspired by the TEXT_QA_SYSTEM_PROMPT from llama_index
        https://github.com/jerryjliu/llama_index/blob/647a9fff672b10f20c34f2b8b23a79930775c827/llama_index/prompts/chat_prompts.py#L7-L19
        """
        return """You are the WarrenPlanBot, an expert Reddit bot that is trusted around the world to answer questions about Senator Warren's plans. You are kind and optimistic, and support Elizabeth Warren for president.

Always answer the query using the provided context information, and not prior knowledge.
Some rules to follow:
1. Never directly reference the given context in your answer.
2. Avoid statements like 'Based on the context, ...' or 'The context information ...' or 'the relevant plan' or anything along those lines.
3. Include information about the plan provided in the given context"""


def build_plan_response_text(plan: PurePlan, post_text: str) -> Optional[str]:
    """
    Use ChatGPT to generate a contextual reply to a user's full post.
    The plan has already been matched, and other information in the user's
    post can be used to answer questions about specific aspects of the plan,
    or simply to focus on the most relevant parts of the plan that the user
    is referring to

    :param plan: Single matched plan
    :param post_text: Full text of user post which summoned the bot
    :return: LLM reply to pass to user
    """
    logger.info("Generating LLM response")
    messages = [
        {"role": "system", "content": Prompts.planbot_system_prompt()},
        {
            "role": "user",
            "content": Prompts.matched_plan_user_prompt(
                user_input=post_text, plan=plan
            ),
        },
    ]

    try:
        llm_response = openai.ChatCompletion.create(
            model=MODEL,
            messages=messages,
            temperature=0,  # consistent responses are more desirable than creative responses for a political campaign
        )

        finish_reason = llm_response["choices"][0]["finish_reason"]
        response_text = llm_response["choices"][0]["message"]["content"]
        if finish_reason != "stop":
            logger.warning(f"LLM response did not complete. {finish_reason=}")
            return
    except Exception:
        logger.exception("LLM response failed for unknown reason")
        return

    logger.info(f"LLM response successful. {post_text=} {response_text=}")

    return response_text
