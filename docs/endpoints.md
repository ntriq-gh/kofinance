# 엔드포인트 레퍼런스

Base URL: `https://api.ntriq.co.kr/kofinance/api/v1`

---

## 1. 종목 리스트 - `GET /stocks`

전 상장사(KOSPI, KOSDAQ, KONEX) 종목 목록을 조회합니다.

### Parameters

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `market` | string | - | `ALL` | 시장 구분: `ALL`, `KOSPI`, `KOSDAQ`, `KONEX` |
| `search` | string | - | - | 종목명 또는 종목코드 검색 |
| `limit` | integer | - | `100` | 최대 반환 수 (1~500) |

### Request

```bash
curl -H "X-YAP-Key: your-api-key" \
  "https://api.ntriq.co.kr/kofinance/api/v1/stocks?market=KOSPI&search=삼성&limit=10"
```

```python
df = kf.stocks(market="KOSPI", search="삼성", limit=10)
```

### Response

```json
{
  "stocks": [
    {
      "symbol": "005930",
      "name": "삼성전자",
      "market": "KOSPI",
      "sector": "반도체",
      "market_cap": 3580000,
      "listed_date": "1975-06-11"
    }
  ],
  "total": 1
}
```

---

## 2. 기업 기본정보 - `GET /stocks/{symbol}`

특정 종목의 기본정보를 조회합니다.

### Path Parameters

| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| `symbol` | string | Y | 종목코드 (예: `005930`) |

### Request

```bash
curl -H "X-YAP-Key: your-api-key" \
  "https://api.ntriq.co.kr/kofinance/api/v1/stocks/005930"
```

```python
info = kf.stock("005930")
```

### Response

```json
{
  "symbol": "005930",
  "name": "삼성전자",
  "name_en": "Samsung Electronics",
  "market": "KOSPI",
  "sector": "반도체",
  "industry": "전자부품, 컴퓨터, 영상, 음향 및 통신장비 제조업",
  "ceo": "한종희",
  "homepage": "https://www.samsung.com/sec/",
  "listed_date": "1975-06-11",
  "fiscal_month": 12,
  "market_cap": 3580000
}
```

---

## 3. 재무제표 - `GET /stocks/{symbol}/financials`

재무제표(손익계산서, 재무상태표, 현금흐름표, 주요 비율)를 조회합니다.

### Parameters

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `symbol` | path | Y | - | 종목코드 |
| `period` | query | - | `3y` | 조회 기간: `1y`, `3y`, `5y` |
| `type` | query | - | `annual` | `annual` (연간), `quarterly` (분기) |

### Request

```bash
curl -H "X-YAP-Key: your-api-key" \
  "https://api.ntriq.co.kr/kofinance/api/v1/stocks/005930/financials?period=3y&type=annual"
```

```python
df = kf.financials("005930", period="3y", type="annual")

# 여러 종목 동시 조회
df = kf.financials(["005930", "000660"], period="3y")
```

### Response

```json
{
  "symbol": "005930",
  "name": "삼성전자",
  "financials": [
    {
      "period": "2025",
      "type": "annual",
      "consolidated": true,
      "income_statement": {
        "revenue": 302231000000000,
        "operating_income": 58490000000000,
        "net_income": 42680000000000,
        "ebitda": 89230000000000
      },
      "balance_sheet": {
        "total_assets": 455280000000000,
        "total_liabilities": 121340000000000,
        "total_equity": 333940000000000,
        "retained_earnings": 298760000000000
      },
      "ratios": {
        "roe": 13.2,
        "roa": 9.6,
        "per": 12.5,
        "pbr": 1.4,
        "eps": 6328,
        "debt_ratio": 36.3,
        "operating_margin": 19.4,
        "net_margin": 14.1,
        "dividend_yield": 2.1
      },
      "cash_flow": {
        "operating": 72340000000000,
        "investing": -53210000000000,
        "financing": -18920000000000
      }
    }
  ]
}
```

### DataFrame 컬럼 (as_dataframe=True)

SDK에서 DataFrame으로 변환 시 컬럼명 규칙:

| 접두사 | 출처 | 예시 |
|--------|------|------|
| `is_` | income_statement | `is_revenue`, `is_operating_income` |
| `bs_` | balance_sheet | `bs_total_assets`, `bs_total_equity` |
| `ratio_` | ratios | `ratio_roe`, `ratio_per` |
| `cf_` | cash_flow | `cf_operating`, `cf_investing` |

---

## 4. 공시 - `GET /stocks/{symbol}/disclosures`

DART 공시 목록과 AI 요약을 조회합니다.

### Parameters

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `symbol` | path | Y | - | 종목코드 |
| `days` | query | - | `30` | 최근 N일 이내 공시 (1~365) |
| `type` | query | - | `all` | 공시 유형: `all`, `earnings`, `material`, `ownership`, `governance` |

### Request

```bash
curl -H "X-YAP-Key: your-api-key" \
  "https://api.ntriq.co.kr/kofinance/api/v1/stocks/005930/disclosures?days=30&type=all"
```

```python
df = kf.disclosures("005930", days=30)
```

### Response

```json
{
  "symbol": "005930",
  "name": "삼성전자",
  "disclosures": [
    {
      "id": "20260301000123",
      "title": "사업보고서 (2025.12)",
      "type": "earnings",
      "date": "2026-03-01",
      "url": "https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20260301000123",
      "summary": "2025년 연결 매출 302.2조원(전년 대비 +15.3%), 영업이익 58.5조원(+32.1%) 달성. 반도체 부문 실적 개선이 주요 동인.",
      "key_points": [
        "연결 매출 302.2조원 (+15.3% YoY)",
        "영업이익 58.5조원 (+32.1% YoY)",
        "반도체 부문 매출 비중 확대"
      ]
    }
  ]
}
```

---

## 5. 종목 스크리닝 - `GET /screen`

조건 기반으로 종목을 필터링합니다.

### Parameters

| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| `market` | string | - | 시장: `KOSPI`, `KOSDAQ` |
| `sector` | string | - | 업종명 |
| `per_lt` | float | - | PER 상한 |
| `per_gt` | float | - | PER 하한 |
| `pbr_lt` | float | - | PBR 상한 |
| `roe_gt` | float | - | ROE 하한 (%) |
| `roe_lt` | float | - | ROE 상한 (%) |
| `market_cap_gt` | integer | - | 시가총액 하한 (억원) |
| `market_cap_lt` | integer | - | 시가총액 상한 (억원) |
| `dividend_yield_gt` | float | - | 배당수익률 하한 (%) |
| `debt_ratio_lt` | float | - | 부채비율 상한 (%) |

### Request

```bash
curl -H "X-YAP-Key: your-api-key" \
  "https://api.ntriq.co.kr/kofinance/api/v1/screen?roe_gt=15&per_lt=10&market=KOSPI"
```

```python
df = kf.screen(roe_gt=15, per_lt=10, market="KOSPI")
```

### Response

```json
{
  "results": [
    {
      "symbol": "003550",
      "name": "LG",
      "market": "KOSPI",
      "sector": "지주회사",
      "market_cap": 152000,
      "per": 7.2,
      "pbr": 0.8,
      "roe": 18.5,
      "dividend_yield": 3.4,
      "debt_ratio": 28.1
    }
  ],
  "total": 1
}
```

---

## 6. 트레이딩 시그널 - `GET /signals`

기술적 분석 기반 트레이딩 시그널을 조회합니다.

### Parameters

| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| `symbol` | string | - | 종목코드 (없으면 전체) |
| `signal_type` | string | - | 시그널 유형 (아래 참고) |

#### 시그널 유형

| signal_type | 설명 |
|------------|------|
| `golden_cross` | 골든크로스 (단기 이평선이 장기 이평선 상향 돌파) |
| `death_cross` | 데드크로스 (단기 이평선이 장기 이평선 하향 돌파) |
| `volume_spike` | 거래량 급증 (평균 대비 200% 이상) |
| `rsi_oversold` | RSI 과매도 (RSI < 30) |
| `rsi_overbought` | RSI 과매수 (RSI > 70) |
| `macd_bullish` | MACD 매수 신호 |
| `macd_bearish` | MACD 매도 신호 |
| `bollinger_lower` | 볼린저 밴드 하단 이탈 |
| `bollinger_upper` | 볼린저 밴드 상단 이탈 |

### Request

```bash
curl -H "X-YAP-Key: your-api-key" \
  "https://api.ntriq.co.kr/kofinance/api/v1/signals?signal_type=golden_cross"
```

```python
df = kf.signals(signal_type="golden_cross")
```

### Response

```json
{
  "signals": [
    {
      "symbol": "005930",
      "name": "삼성전자",
      "signal_type": "golden_cross",
      "strength": "strong",
      "timestamp": "2026-03-05T09:15:00+09:00",
      "description": "20일 이평선이 60일 이평선을 상향 돌파. 거래량 동반 증가."
    }
  ]
}
```
