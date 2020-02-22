class BaseError(Exception):
    def __init__(self, wrapped_err=None):
        self.wrapped_err = wrapped_err

class CreationError(BaseError):
    ...

class ConnectionError(BaseError):
    ...

class SendError(BaseError):
    ...

class RecvError(BaseError):
    ...
