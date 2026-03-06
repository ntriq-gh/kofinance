# 인증 (Authentication)

KoFinance API는 **API 키** 방식으로 인증합니다.

## API 키 발급

1. [kofinance.ntriq.co.kr](https://kofinance.ntriq.co.kr) 회원가입
2. 대시보드 → API 키 관리 → 새 키 생성
3. 발급된 키를 안전하게 보관

## 요청 시 인증

모든 API 요청에 `X-YAP-Key` 헤더를 포함해야 합니다.

### curl

```bash
curl -H "X-YAP-Key: yap_your_api_key_here" \
  "https://api.ntriq.co.kr/kofinance/api/v1/stocks"
```

### Python SDK

```python
from kofinance import KoFinance

kf = KoFinance("yap_your_api_key_here")
```

### 환경 변수 사용 (권장)

```bash
# .env 또는 쉘 환경변수
export KOFINANCE_API_KEY="yap_your_api_key_here"
```

```python
import os
from kofinance import KoFinance

kf = KoFinance(os.environ["KOFINANCE_API_KEY"])
```

## 보안 가이드라인

| 규칙 | 설명 |
|------|------|
| 환경 변수 사용 | 코드에 API 키를 직접 넣지 마세요 |
| `.gitignore`에 `.env` 추가 | API 키가 Git에 커밋되지 않도록 |
| 키 로테이션 | 키가 노출되면 즉시 재발급 |
| 서버 사이드 호출 | 프론트엔드에서 직접 호출하지 마세요 |

## 인증 실패 시

```json
{
  "error": {
    "code": "INVALID_API_KEY",
    "message": "유효하지 않은 API 키입니다.",
    "status": 401
  }
}
```

| 상황 | HTTP Status | 원인 |
|------|------------|------|
| 키 누락 | 401 | `X-YAP-Key` 헤더 없음 |
| 잘못된 키 | 401 | 존재하지 않는 API 키 |
| 만료된 키 | 401 | 비활성화된 API 키 |
| 한도 초과 | 429 | Rate limit 초과 ([상세](./rate-limits.md)) |
