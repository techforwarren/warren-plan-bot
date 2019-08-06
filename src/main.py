import praw
import pdb
import re
import os

#change dev to prod to shift to production bot
reddit = praw.Reddit('dev')

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
    
    # If we haven't replied to this post before
    if submission.id not in posts_replied_to:

        # Do a case insensitive search
        if re.search("!warrenplanbot", submission.selftext, re.IGNORECASE):
            # Search for topic keywords
            if re.search("student debt", submission.selftext, re.IGNORECASE):
                # Reply to the post with plan info
                submission.reply('''Senator Warren believes we should treat higher education like our public school system – free and accessible to all Americans. 
                                    That’s why she's calling for something truly transformational – 
                                    the cancellation of up to $50,000 in student loan debt for 42 million Americans and free universal college for everyone. 
                                    Learn more [here](https://medium.com/@teamwarren/im-calling-for-something-truly-transformational-universal-free-public-college-and-cancellation-of-a246cd0f910f)''')
                print("Bot replying to: ", submission.title)
                posts_replied_to.append(submission.id)

# Write the updated list back to the file
with open("posts_replied_to.txt", "w") as f:
    for post_id in posts_replied_to:
        # uncomment next line when ready to start recording post IDs so it doesn't reply multiple times
        # f.write(post_id + "\n")
        print("replied to : ", post_id + "\n")

