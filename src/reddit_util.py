import praw.models


class Wrapper:
    def __init__(self, wrapped):
        self.wrapped = wrapped

    def __getattr__(self, attr):
        return getattr(self.wrapped, attr)


class Submission(Wrapper):
    """
    Wraps a PRAW Submission instance with some standard methods and properties
    """

    def __init__(self, submission):
        super().__init__(submission)
        self.type = "submission"

    @property
    def text(self):
        return self.title + "\n" + self.selftext


class Comment(Wrapper):
    """
    Wraps a PRAW Comment instance with some standard methods and properties
    """

    def __init__(self, comment):
        super().__init__(comment)
        self.type = "comment"

    @property
    def text(self):
        return self.body

    @property
    def submission(self):
        return Submission(self.wrapped.submission)


def standardize(post):
    if isinstance(post, praw.models.Comment):
        return Comment(post)
    elif isinstance(post, praw.models.Submission):
        return Submission(post)
    else:
        raise NotImplementedError(post)
