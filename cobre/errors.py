class ConnectionError(Exception):
    def __init__(self, e):
        self.error = e
