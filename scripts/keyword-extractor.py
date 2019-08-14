# TODO:
#       def function to feed plan list from db or .json file to populate plans return synonym list if auto processing
#       is desired.
#       Otherwise, write output to file or firestore.
#       Add imports to requirements if function created for future use.

import json
import os
from os import path

import RAKE
import requests
from bs4 import BeautifulSoup
from lxml import html

DIRNAME = path.dirname(path.realpath(__file__))

PLANS_FILE = path.join(DIRNAME, "../src/plans.json")
# RAKE options
MIN_CHARACTERS_IN_PHRASE = 3
MAX_WORDS_IN_PHRASE = 3
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
MIN_RESULT_SCORE = 10.0


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

    parsed_text = "".join(str(x) for x in page_text)

    text = plan["summary"]

    # r.run() returns key value pairs with the keyword or keyphrase as key, score as value
    rake_results = r.run(
        parsed_text,
        minCharacters=MIN_CHARACTERS_IN_PHRASE,
        maxWords=MAX_WORDS_IN_PHRASE,
        minFrequency=MIN_WORD_FREQUENCY,
    )
    key_phrases = []
    for result in rake_results:
        # Limit results inserted into keyword_dict to results scoring above 3.0
        if result[1] > MIN_RESULT_SCORE:
            # appends only the text value from each keyphrase, append results to append phrase and score
            key_phrases.append(result[0])

    keyword_dict.append(
        {
            "id": plan["id"],
            "topic": plan["display_title"],
            "synonym_keyphrases": key_phrases,
        }
    )

# TODO: Could dump to file instead after adding logic for appending keyword groups with scores above threshold or length of 2 words or more
print(
    json.dumps(
        keyword_dict,
        sort_keys=False,
        ensure_ascii=False,
        indent=4,
        separators=(",", ": "),
    )
)
