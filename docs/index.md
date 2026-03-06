# KoFinance API 문서

KoFinance는 한국 상장사의 **재무제표, 공시, 종목 스크리닝, 트레이딩 시그널**을 하나의 API로 제공합니다.

## 목차

- [Quick Start](#quick-start)
- [인증 (Authentication)](./authentication.md)
- [엔드포인트 레퍼런스](./endpoints.md)
- [Rate Limit](./rate-limits.md)
- [에러 처리](./errors.md)

---

## Quick Start

### 1. API 키 발급

[kofinance.ntriq.co.kr](https://kofinance.ntriq.co.kr)에서 회원가입 후 API 키를 발급받으세요.

### 2. SDK 설치

```bash
pip install kofinance
```

### 3. 첫 번째 요청

```python
from kofinance import KoFinance

kf = KoFinance("your-api-key")

# 삼성전자 재무제표 조회
df = kf.financials("005930")
print(df)
```

### 4. curl로 직접 호출

```bash
curl -H "X-YAP-Key: your-api-key" \
  "https://api.ntriq.co.kr/kofinance/api/v1/stocks/005930/financials?period=3y&type=annual"
```

---

## 주요 기능

| 기능 | 엔드포인트 | 설명 |
|------|-----------|------|
| 종목 리스트 | `GET /stocks` | KOSPI/KOSDAQ/KONEX 전 상장사 |
| 기업정보 | `GET /stocks/{symbol}` | 기업 기본정보 |
| 재무제표 | `GET /stocks/{symbol}/financials` | 손익계산서, 재무상태표, 현금흐름표, 주요 비율 |
| 공시 | `GET /stocks/{symbol}/disclosures` | DART 공시 + AI 요약 |
| 스크리닝 | `GET /screen` | 조건 기반 종목 필터링 |
| 시그널 | `GET /signals` | 기술적 분석 시그널 (골든크로스, RSI 등) |

## Base URL

```
https://api.ntriq.co.kr/kofinance/api/v1
```

모든 요청은 HTTPS로만 접수됩니다.
