import requests


def search_comments(q, subreddit, limit):
    payload = {
        "q": q,
        "subreddit": subreddit,
        "size": limit,
        "sort": "desc",
        "after": "30d",
    }

    # fields must be comma-delimited and not escaped, so put it directly in the url
    url = "https://api.pushshift.io/reddit/comment/search?fields=author,author_fullname,body,created_utc,id,link_id,locked,parent_id,permalink,subreddit,subreddit_id"

    resp = requests.get(url, params=payload)

    resp.raise_for_status()

    comments = resp.json()["data"]

    return comments
