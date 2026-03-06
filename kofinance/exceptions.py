class KoFinanceError(Exception):
    def __init__(self, message: str, status_code: int = None):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class AuthenticationError(KoFinanceError): ...


class RateLimitError(KoFinanceError): ...


class NotFoundError(KoFinanceError): ...
