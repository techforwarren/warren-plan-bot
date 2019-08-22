#!/usr/bin/env python3

# TODO:
#       def function to feed plan list from db or .json file to populate plans return synonym list if auto processing
#       is desired.
#       Otherwise, write output to file or firestore.

import json
import logging
import os
from os import path
import re

import RAKE
import requests
from bs4 import BeautifulSoup

DIRNAME = path.dirname(path.realpath(__file__))

OUTPUT_DIR = path.abspath(path.join(DIRNAME, "../data/keyphrases/"))

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

logging.basicConfig(format="%(levelname)s : %(message)s", level=logging.INFO)

logger = logging.getLogger(__name__)

PLANS_FILE = path.join(DIRNAME, "../src/plans.json")
# RAKE options
MIN_CHARACTERS_IN_PHRASE = 3
MAX_WORDS_IN_PHRASE = 4
MIN_WORD_FREQUENCY = 1  # value greater than 1 is not recommended with such short text.
RAKE_STOPLIST = RAKE.NLTKStopList()
# Alternate RAKE stopword lists that can be used instead
# NLTKStopList()
# SmartStopList()
# FoxStopList()
# NLTKStopList()
# MySQLStopList
# GoogleSearchStopList()
# RanksNLStopList()
# RanksNLLongStopList()

# minimum score allowed for keyword extracted to be inserted into synonym list
MIN_RESULT_SCORE = 7.0


with open(PLANS_FILE) as json_file:
    plans = json.load(json_file)

r = RAKE.Rake(RAKE_STOPLIST)

# Initialize keyword_dict and text with empty values
keyword_dict = []
text = ""

# Iterate through plans_dict, rake the summary section, append keyphrases to each topic
for plan in plans:
    # TODO: Consider importing text from full article from plan URL instead of summary to get better keyword selection and increasing usefulness of frequency
    page = requests.get(plan["url"]).text

    page_soup = BeautifulSoup(page, "html.parser")
    blacklist = [
        "style",
        "script",
        "doctype",
        # other elements,
    ]
    page_text = [
        t for t in page_soup.find_all(text=True) if t.parent.name not in blacklist
    ]

    parsed_text: str = "".join(str(x) for x in page_text)
    parsed_text = parsed_text.lower()

    # Remove punctuation
    regx = re.compile(r"([^\w\s]+)|([_-]+)")
    parsed_text = regx.sub(repl=" ", string=parsed_text)

    # Replace all newlines and blanklines with special strings
    regx = re.compile(r"\n")
    parsed_text = regx.sub(repl=" ", string=parsed_text)
    regx = re.compile(r"\n\n")
    parsed_text = regx.sub(repl=" ", string=parsed_text)

    # Make all white space a single space
    regx = re.compile(r"\s+")
    parsed_text = regx.sub(repl=" ", string=parsed_text)

    # r.run() returns key value pairs with the keyword or keyphrase as key, score as value
    rake_results = r.run(
        parsed_text,
        minCharacters=MIN_CHARACTERS_IN_PHRASE,
        maxWords=MAX_WORDS_IN_PHRASE,
        minFrequency=MIN_WORD_FREQUENCY,
    )
    key_phrases = []
    for result in rake_results:
        # Limit results inserted into keyword_dict to results scoring above MIN_RESULT_SCORE
        if result[1] > MIN_RESULT_SCORE:

            # Create keyphrase and scoring entry from result
            key_phrases.append({"keyphrase": result[0], "score": round(result[1],2)})

    keyword_dict.append(
        {
            "id": plan["id"],
            "topic": plan["display_title"],
            "synonym_keyphrases": key_phrases,
        }
    )

# Write keyphrases to JSON file
filename = path.join(OUTPUT_DIR, "extracted_keyphrases.json")
logger.info(f"Writing extracted keyphrases to {filename}")

with open(filename, "w") as extracted_keyphrases_file:
    extracted_keyphrases_file.write(
        json.dumps(
            keyword_dict,
            sort_keys=False,
            ensure_ascii=False,
            indent=4,
            separators=(",", ": "),
        )
    )
