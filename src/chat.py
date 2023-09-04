#!/usr/bin/env python3

import json
import os
import textwrap
from os import path
from plans import load_plans

import click
import openai

from matching import Strategy

MODEL = "gpt-3.5-turbo-16k"  # Need at least 12k tokens in order to fit largest plans
def match_plan(chat_text, matching_strategy=Strategy.lsa_gensim_v3):


    plans = load_plans()

    # TODO handle different depending on whether it matches

    match_info = matching_strategy(plans, chat_text)

    match = match_info.get("match")
    plan_confidence = match_info.get("confidence")
    plan = match_info.get("plan", {})
    potential_matches = match_info.get("potential_matches")
    plan_id = plan.get("id")

    post_record_update = {}

    # If plan is matched with confidence, build and send reply
    if match:
        print(match)
        return Prompts.single_match(user_input=chat_text, matched_plan=plan)
    else:
        print("no match")
        # TODO
        return " ".join([match["plan"]["url"] for match in potential_matches[:8]])


class Prompts:
    @staticmethod
    def single_match(user_input, matched_plan):

        # prompt inspired by https://github.com/jerryjliu/llama_index/blob/main/llama_index/prompts/chat_prompts.py#L21
        return f"""Context information is below.

---------------------\n
The title of Senator Warren's plan: "{matched_plan['display_title']}" 

The URL: {matched_plan['url']}

A summary of this plan: {matched_plan['summary']}

The full text of this plan is:

{matched_plan['full_text']}
-----------
Given the context information and not prior knowledge, answer the question. Please include the name and url of the plan in your reply.

Query: {user_input}"
Answer: 
"""

    @staticmethod
    def planbot_system_prompt():
        return """You are the WarrenPlanBot, an expert Reddit bot that is trusted around the world to answer questions about Senator Warren's plans. You are kind and optimistic, and support Elizabeth Warren for president.

Always answer the query using the provided context information, and not prior knowledge.
Some rules to follow:
1. Never directly reference the given context in your answer.
2. Avoid statements like 'Based on the context, ...' or 'The context information ...' or "the relevant plan" or anything along those lines.
3. Include information about the plan provided in the given context"""


# Also, if a user asks you to provide information about a different plan or topic, do not answer it. Instead, ask them to start a new conversation.


def plan_bot_say(text, width=80):
    print("\n" + "\n".join(textwrap.wrap(f"WPB: {text}", width)))


# TODO handle plan clusters (or don't match them)
# TODO user broke out of just this plan


@click.command()
@click.argument("post_text", type=str)
def chat_plan_bot(post_text: str):
    messages = [
        {"role": "system", "content": Prompts.planbot_system_prompt()},
        {"role": "user", "content": match_plan(post_text)},
    ]
    llm_response = openai.ChatCompletion.create(
        model=MODEL,
        messages=messages,
        temperature=0,  # consistent responses are more desirable than creative responses for a political campaign
    )

    print(llm_response)
    finish_reason = llm_response["choices"][0]["finish_reason"]
    response_text = llm_response["choices"][0]["message"]["content"]

    if finish_reason == "stop":
        plan_bot_say(response_text)


if __name__ == "__main__":
    chat_plan_bot()
