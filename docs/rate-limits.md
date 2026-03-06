# Rate Limit (요청 한도)

KoFinance API는 안정적인 서비스를 위해 요청 한도를 적용합니다.

## 플랜별 한도

| 플랜 | 일일 요청 | 분당 요청 | 가격 |
|------|----------|----------|------|
| **Free** | 100 | 10 | 무료 |
| **Pro** | 10,000 | 100 | 월 29,000원 |
| **Enterprise** | 무제한 | 1,000 | 별도 문의 |

## 응답 헤더

모든 API 응답에 Rate Limit 정보가 포함됩니다.

```
X-RateLimit-Limit: 100          # 일일 최대 요청 수
X-RateLimit-Remaining: 87       # 남은 요청 수
X-RateLimit-Reset: 1709683200   # 리셋 시각 (Unix timestamp)
X-RateLimit-Limit-Minute: 10    # 분당 최대 요청 수
X-RateLimit-Remaining-Minute: 8 # 분당 남은 요청 수
```

## 한도 초과 시 (429 Too Many Requests)

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "요청 한도를 초과했습니다. 잠시 후 다시 시도해주세요.",
    "status": 429,
    "details": {
      "limit": 10,
      "window": "minute",
      "retry_after": 32
    }
  }
}
```

`Retry-After` 헤더에 대기 시간(초)이 포함됩니다.

## Best Practices

### 1. 캐싱

재무제표 등 자주 바뀌지 않는 데이터는 캐싱하세요.

```python
import functools

@functools.lru_cache(maxsize=100)
def get_financials(symbol: str):
    return kf.financials(symbol)
```

### 2. 배치 조회

여러 종목을 조회할 때는 리스트로 한번에 요청하세요.

```python
# 비효율적 (5회 요청)
for symbol in ["005930", "000660", "035420", "051910", "006400"]:
    kf.financials(symbol)

# 효율적 (내부적으로 순차 처리하지만 연결 재사용)
df = kf.financials(["005930", "000660", "035420", "051910", "006400"])
```

### 3. Exponential Backoff

429 에러 발생 시 점진적으로 대기 시간을 늘리세요.

```python
import time
from kofinance import KoFinance, RateLimitError

kf = KoFinance("your-api-key")

def safe_request(func, *args, max_retries=3, **kwargs):
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except RateLimitError:
            wait = 2 ** attempt
            print(f"Rate limited. {wait}초 후 재시도...")
            time.sleep(wait)
    raise RateLimitError("Max retries exceeded")

df = safe_request(kf.financials, "005930")
```
