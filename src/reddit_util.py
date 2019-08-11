class Wrapper:
    def __init__(self, wrapped):
        self.wrapped = wrapped

    def __getattr__(self, attr):
        return getattr(self.wrapped, attr)


class Submission(Wrapper):
    def __init__(self, submission):
        super().__init__(submission)
        self.type = "submission"

    @property
    def text(self):
        return self.self_text


class Comment(Wrapper):
    def __init__(self, comment):
        super().__init__(comment)
        self.type = "comment"

    @property
    def text(self):
        return self.body

    @property
    def submission(self):
        return Submission(self.wrapped.submission)
