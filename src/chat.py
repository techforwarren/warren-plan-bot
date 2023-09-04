#!/usr/bin/env python3

import json
import os
from os import path
import openai
import textwrap


import click
from matching import Strategy

DIRNAME = path.dirname(path.realpath(__file__))

PLANS_FILE = path.abspath(path.join(DIRNAME, "plans.json"))
PLANS_CLUSTERS_FILE = path.abspath(path.join(DIRNAME, "plan_clusters.json"))
PLAN_TEXT_DIR = path.abspath(path.join(DIRNAME, "../data/interim/plan_text")) # must be locally generated TODO move and check into repo

MODEL = "gpt-3.5-turbo-16k" # Need at least 12k tokens in order to fit largest plans
# MODEL = "gpt-4" # Need at least 12k tokens in order to fit largest plans

def match_plan(
    chat_text,
    matching_strategy=Strategy.lsa_gensim_v3,
):
    with open(PLANS_FILE) as json_file:
        pure_plans = json.load(json_file)

    with open(PLANS_CLUSTERS_FILE) as json_file:
        plan_clusters = json.load(json_file)

    for plan in plan_clusters:
        plan["is_cluster"] = True
        plan["plans"] = [
            next(filter(lambda p: p["id"] == plan_id, pure_plans))
            for plan_id in plan["plan_ids"]
        ]

    plans = pure_plans + plan_clusters

    # TODO trigger line stuff with newline or period. use trigger line to match the plan and then allow any question beyond it?
    # TODO handle different depending on whether it matches
    # TODO only one response

    match_info = (
        matching_strategy(plans, chat_text)
    )

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
        return ' '.join([match['plan']['url'] for match in potential_matches[:8]])

class Prompts:
    @staticmethod
    def single_match(user_input, matched_plan):
        full_plan = json.load(open(path.join(PLAN_TEXT_DIR, matched_plan["id"] + ".json")))

        # prompt inspired by https://github.com/jerryjliu/llama_index/blob/main/llama_index/prompts/chat_prompts.py#L21
        return f"""Context information is below.

---------------------\n
The title of Senator Warren's plan: "{matched_plan['display_title']}" 

The URL: {matched_plan['url']}

A summary of this plan: {matched_plan['summary']}

The full text of this plan is:

{full_plan['text']}
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
def chat_plan_bot():
    user_input = ""
    messages = []
    plan_bot_say("I’m the WarrenPlanBot. If Elizabeth Warren has a plan, I can help you find it!")
    user_input = input("\nYou: ")

    messages.append({"role": "system", "content": Prompts.planbot_system_prompt()})
    messages.append({"role": "user", "content": match_plan(user_input)})
    while user_input.lower() not in {"exit", "quit"}:
        response = openai.ChatCompletion.create(
            model=MODEL,
            messages=messages,
            temperature=0,
        )
        # TODO check finish_reason is stop
        assistant_response = response["choices"][0]["message"]["content"]

        messages.append({"role": "assistant", "content": assistant_response})
        plan_bot_say(assistant_response)

        user_input = input("\nYou: ")
        messages.append({"role": "user", "content": user_input})

if __name__ == "__main__":
    chat_plan_bot()
