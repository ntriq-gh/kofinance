# KoFinance Python SDK

한국 상장사 재무제표, 공시, 종목 스크리닝, 트레이딩 시그널을 pandas DataFrame으로 간편하게 조회하세요.

## 설치

```bash
pip install kofinance
```

## Quick Start

```python
from kofinance import KoFinance

kf = KoFinance("your-api-key")

# 삼성전자 재무제표 (최근 3년)
df = kf.financials("005930")
print(df[["period", "is_revenue", "is_operating_income", "ratio_roe"]])

# 공시 조회 (최근 30일)
disclosures = kf.disclosures("005930")
print(disclosures[["date", "title", "summary"]])

# 종목 스크리닝 (ROE 15% 이상, PER 10배 이하)
screened = kf.screen(roe_gt=15, per_lt=10)
print(screened)

# 트레이딩 시그널
signals = kf.signals(signal_type="golden_cross")
print(signals)
```

## API 메서드

| 메서드 | 설명 | 반환 |
|--------|------|------|
| `stocks(market, search, limit)` | 종목 리스트 조회 | DataFrame |
| `stock(symbol)` | 기업 기본정보 | dict |
| `financials(symbol, period, type)` | 재무제표 | DataFrame |
| `disclosures(symbol, days, type)` | 공시 + AI 요약 | DataFrame |
| `screen(**filters)` | 조건 스크리닝 | DataFrame |
| `signals(symbol, signal_type)` | 트레이딩 시그널 | DataFrame |

## API 키 발급

[kofinance.ntriq.co.kr](https://kofinance.ntriq.co.kr)에서 가입 후 발급받으세요.

```python
import os
kf = KoFinance(os.environ["KOFINANCE_API_KEY"])
```

## 문서

전체 API 문서: [kofinance.ntriq.co.kr/docs](https://kofinance.ntriq.co.kr/docs)

## License

MIT
