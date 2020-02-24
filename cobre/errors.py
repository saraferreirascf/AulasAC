class BaseError(Exception):
    def __init__(self, wrapped_err=None):
        self.wrapped_err = wrapped_err

class CreationError(BaseError):
    ...

class ClientError(BaseError):
    ...

class ServerError(BaseError):
    ...

class SendError(BaseError):
    ...

class RecvError(BaseError):
    ...

class ConnectError(ClientError):
    ...

class BindError(ServerError):
    ...

class ListenError(ServerError):
    ...

class AcceptError(ServerError):
    ...
