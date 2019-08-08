import praw
import pdb
import re
import os
import json
import fuzzywuzzy
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

#change dev to prod to shift to production bot
reddit = praw.Reddit('dev')

# JSON filename of policy plans
plans_file = "plans.json"

with open(plans_file) as json_file:
    plans_dict = json.load(json_file)

# init topic keyword array
query_terms = []

for entry in plans_dict["plans"]:
    query_terms.append({"id": entry["id"], "topic": entry["topic"]})

print(query_terms)

# Check if replied posts exists, if not create an empty list
if not os.path.isfile("posts_replied_to.txt"):
    posts_replied_to = []

# If replied posts file exists, load the list of posts replied to from it
else:
    # Read the file into a list and remove any empty values
    with open("posts_replied_to.txt", "r") as f:
        posts_replied_to = f.read()
        posts_replied_to = posts_replied_to.split("\n")
        posts_replied_to = list(filter(None, posts_replied_to))

# Get the subreddit
subreddit = reddit.subreddit("WPBSandbox")

# Set const for number of posts to return
post_limit = 10

# Get the number of new posts up to the limit
for submission in subreddit.new(limit=post_limit):
    submission_ID = submission.id
    
    # If we haven't replied to this post before
    if submission.id not in posts_replied_to:

        # Do a case insensitive search
        if re.search("!warrenplanbot | /u/WarrenPlanBot", submission.selftext, re.IGNORECASE):
            # Log Submission Data
            print("submission id: ", submission.id)
            print("submission text: ", submission.selftext)
            
            # Initialize match_confidence and match_id before fuzzy searching

            match_confidence = 0
            match_id = 0
            # Search topic keywords and response body for best match
            for item in plans_dict["plans"]:
                item_match_confidence = fuzz.WRatio(submission.selftext, item["topic"])
                item_id = item["id"]
                print("item confidence score: ", item_match_confidence)
                print("current topic: ", item["topic"])
                if item_match_confidence > match_confidence:
                    match_confidence = item_match_confidence
                    match_id = item_id
                    print("new topic match: ", item["topic"])
                
                    #print("topic found in post text: ", topic_match_in_post[0])
                
                    #print("topic found in post confidence: ", topic_match_in_post[1])

            # Reply to the post with plan info, uncomment next line to activate post replies
            #submission.reply(plans_dict[topic_match_in_post[0]]) 
            #print("Bot replying to: ", submission.title)
            #posts_replied_to.append(submission.id)
        
        # After checking submission.selftext, check comments
        # Get comments for submission and search for trigger in comment body
        submission.comments.replace_more(limit=None)
        for comment in submission.comments.list():
            # If we haven't replied to the comment before
            if comment.id not in posts_replied_to:
                # Log Comment Data
                print("comment id: ", comment.id)
                print("comment text: ", comment.body)

                # Search for trigger phrases in the comment
                if re.search("!warrenplanbot | /u/warrenplanbot", comment.body, re.IGNORECASE):
                    print("doing nothing for now")
                    # Search for matching topic keywords in comment body
                    #topic_match_in_comments = process.extractOne(comment.body, query_terms, scorer=fuzz.WRatio)
                    #print("topic found in comment ID", comment.id)
                    #print("topic found in comment: ", topic_match_in_comments[0])
                    #print("topic found in comments confidence: ", topic_match_in_comments[1])
                    
                    #comment.reply(plans_dict[topic_match_in_comments[0]]) 
                    #print("Bot replying to: ", comment.id)
                    #posts_replied_to.append(comment.id)

# Write the updated list back to the file
with open("posts_replied_to.txt", "w") as f:
    for post_id in posts_replied_to:
        # uncomment next line when ready to start recording post IDs so it doesn't reply multiple times
        f.write(post_id + "\n")
        print("replied to : ", post_id + "\n")

