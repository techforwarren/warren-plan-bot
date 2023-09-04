#!/usr/bin/env python3

from llm import build_llm_plan_response_text
from matching import Strategy
from plans import load_plans
import click
import textwrap
from plan_bot import get_trigger_line


def plan_bot_say(text, width=80):
    print("\n" + "\n".join(textwrap.wrap(f"WPB: {text}", width)))


@click.command()
@click.argument("post_text", type=str)
def llm_plan_bot(post_text: str):
    """
    Helper command for exploring LLM responses.

    If a single plan is matched, generate an LLM response, otherwise do nothing.
    """

    # use current best matching strategy for testing purposes
    match_info = Strategy.lsa_gensim_v3(load_plans(), get_trigger_line(post_text))
    match = match_info["match"]
    best_match_plan = match_info["plan"]

    if not match:
        print("No single plan matched. Skipping LLM and exiting")
        return

    if best_match_plan["is_cluster"]:
        print("Plan cluster matched. Skipping LLM and exiting")
        return

    plan_bot_say(build_llm_plan_response_text(best_match_plan, post_text))




if __name__ == "__main__":
    llm_plan_bot()
