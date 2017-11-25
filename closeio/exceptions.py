class CloseIOError(Exception):
    pass


class RateLimitError(CloseIOError):
    """
    Close.io API rate limit error.

    Attributes:
        message (str): e.g.: "API call count exceeded for this 30 second window"
        rate_reset (int): Seconds remaining before this enforcement window ends.
        rate_limit (int): Request limit enforced for this endpoint.
        rate_window (int): Number of seconds in enforcement window.

    """

    def __init__(self, message, rate_reset, rate_limit, rate_window, rate_limit_type, **kwargs):
        self.message = message
        self.rate_reset = rate_reset
        self.rate_limit = rate_limit
        self.rate_window = rate_window
        self.rate_limit_type = rate_limit_type
        super(RateLimitError, self).__init__()

    def __str__(self):
        return self.message

    def __unicode__(self):
        return self.__str__()
