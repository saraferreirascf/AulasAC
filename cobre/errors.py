class BaseError(Exception):
    def __init__(self, wrapped_err=None):
        self.wrapped_err = wrapped_err

class ConnectionError(BaseError):
    ...
