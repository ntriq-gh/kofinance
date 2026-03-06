# 에러 처리

## 에러 응답 형식

모든 에러는 동일한 JSON 구조로 반환됩니다.

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "사람이 읽을 수 있는 에러 메시지",
    "status": 400,
    "details": {}
  }
}
```

## HTTP Status Codes

| Status | 설명 | 대응 방법 |
|--------|------|----------|
| `400` | 잘못된 요청 | 요청 파라미터 확인 |
| `401` | 인증 실패 | API 키 확인 |
| `403` | 권한 없음 | 플랜 업그레이드 필요 |
| `404` | 리소스 없음 | 종목코드 등 확인 |
| `429` | 요청 한도 초과 | 잠시 후 재시도 |
| `500` | 서버 오류 | 잠시 후 재시도, 지속 시 문의 |

## 에러 코드 레퍼런스

| 코드 | Status | 설명 |
|------|--------|------|
| `INVALID_API_KEY` | 401 | 유효하지 않은 API 키 |
| `EXPIRED_API_KEY` | 401 | 만료된 API 키 |
| `RATE_LIMIT_EXCEEDED` | 429 | 요청 한도 초과 |
| `INVALID_SYMBOL` | 400 | 잘못된 종목코드 |
| `SYMBOL_NOT_FOUND` | 404 | 존재하지 않는 종목 |
| `INVALID_PARAMETER` | 400 | 잘못된 파라미터 값 |
| `MISSING_PARAMETER` | 400 | 필수 파라미터 누락 |
| `PLAN_LIMIT` | 403 | 현재 플랜에서 사용 불가 |
| `INTERNAL_ERROR` | 500 | 서버 내부 오류 |

## Python SDK 예외 처리

```python
from kofinance import (
    KoFinance,
    KoFinanceError,
    AuthenticationError,
    RateLimitError,
    NotFoundError,
    APIError,
)

kf = KoFinance("your-api-key")

try:
    df = kf.financials("005930")
except AuthenticationError:
    print("API 키를 확인해주세요.")
except NotFoundError:
    print("존재하지 않는 종목코드입니다.")
except RateLimitError:
    print("요청 한도를 초과했습니다. 잠시 후 다시 시도해주세요.")
except APIError as e:
    print(f"API 에러: {e.message} (code: {e.code})")
except KoFinanceError as e:
    print(f"KoFinance 에러: {e.message}")
```

## 예외 클래스 계층

```
KoFinanceError (기본 예외)
├── AuthenticationError (401)
├── RateLimitError (429)
├── NotFoundError (404)
└── APIError (기타 4xx/5xx)
```

모든 예외는 `message`, `status_code`, `code` 속성을 가집니다.
