import praw

#change dev to prod to shift to production bot
reddit = praw.Reddit('dev')

subreddit = reddit.subreddit("politics")

for submission in subreddit.new(limit=5):
    print(submission)
    print("Title: ", submission.title)
    print("Text: ", submission.selftext)
    print("Score: ", submission.score)
    print("----------------------------------\n")
