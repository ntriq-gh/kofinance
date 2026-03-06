class KoFinanceError(Exception):
    """KoFinance API 기본 예외"""

    def __init__(self, message: str, status_code: int = None, code: str = None):
        self.message = message
        self.status_code = status_code
        self.code = code
        super().__init__(message)


class AuthenticationError(KoFinanceError):
    """인증 실패 (401)"""


class RateLimitError(KoFinanceError):
    """요청 한도 초과 (429)"""


class NotFoundError(KoFinanceError):
    """리소스 없음 (404)"""


class APIError(KoFinanceError):
    """기타 API 에러 (4xx/5xx)"""
