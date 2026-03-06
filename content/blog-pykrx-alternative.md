# pykrx 대안: KoFinance API로 한국 주식 데이터 가져오기

> **키워드**: pykrx 대안, 한국 주식 API, 재무제표 API, pykrx 안됨, pykrx 에러, 한국 금융 데이터, 코스피 API, 코스닥 API, KRX API, 주식 데이터 파이썬

---

pykrx로 한국 주식 데이터를 가져오려다 에러를 만난 적 있으신가요?

```
ConnectionError: HTTPSConnectionPool(host='data.krx.co.kr', port=443)
```

```python
df = stock.get_market_ohlcv("20260101", "20260305", "005930")
# → Empty DataFrame 또는 ConnectionError
```

**pykrx가 작동하지 않는 이유**는 간단합니다. pykrx는 KRX(한국거래소) 웹사이트를 스크래핑하는 비공식 라이브러리인데, KRX가 2025년 하반기에 웹사이트 구조를 변경하면서 크롤링이 차단되었습니다.

이 글에서는 pykrx의 안정적인 대안인 **KoFinance API**를 소개합니다.

---

## pykrx의 문제점

pykrx는 한국 파이썬 커뮤니티에서 가장 널리 쓰이는 주식 데이터 라이브러리였습니다. 하지만 근본적인 한계가 있습니다.

### 1. KRX 스크래핑 차단

pykrx는 `data.krx.co.kr`의 내부 API를 역공학해서 데이터를 가져옵니다. KRX가 엔드포인트를 변경하거나, User-Agent를 차단하거나, HTML 구조를 바꾸면 즉시 작동이 멈춥니다.

```python
# 2025년 이후 자주 발생하는 에러들
from pykrx import stock

# Case 1: 빈 DataFrame
df = stock.get_market_ohlcv("20260101", "20260305", "005930")
print(df)  # Empty DataFrame

# Case 2: ConnectionError
# ConnectionError: Max retries exceeded with url: /contents/MDC/...

# Case 3: JSONDecodeError
# json.decoder.JSONDecodeError: Expecting value: line 1 column 1
```

### 2. 제한된 데이터

pykrx가 (작동할 때) 제공하는 데이터:
- 시세 (OHLCV)
- 기본 지표 (PER, PBR, EPS, BPS, DIV)

pykrx가 **제공하지 않는** 데이터:
- 손익계산서 (매출, 영업이익, 순이익)
- 재무상태표 (총자산, 총부채, 자본)
- 현금흐름표
- 공시 (DART)
- 종목 스크리닝
- 기술적 분석 시그널

### 3. 느린 속도

pykrx는 매 요청마다 KRX 웹페이지를 파싱합니다. 전 종목 데이터를 가져오려면 종목 수만큼 반복해야 하고, 이는 수십 분이 걸립니다.

---

## KoFinance API 소개

[KoFinance](https://kofinance.ntriq.co.kr)는 한국 상장사 금융 데이터를 REST API로 제공하는 서비스입니다.

### 핵심 차이점

| | pykrx | KoFinance |
|---|---|---|
| **작동 여부** | KRX 차단으로 불안정 | 정상 운영 (99.9% SLA) |
| **데이터 출처** | KRX 웹 스크래핑 | DART + KRX 공식 수집 |
| **인증** | 없음 (공개 크롤링) | API 키 (안정적) |
| **속도** | 수 초/건, 대량 시 수십 분 | < 200ms/건 |
| **재무제표** | 기본 지표만 | 전체 (IS+BS+CF+비율) |
| **공시** | 없음 | DART 공시 + AI 요약 |
| **스크리닝** | 없음 | 조건 필터링 API |
| **시그널** | 없음 | 기술적 분석 시그널 |
| **지원** | 커뮤니티 | 공식 기술 지원 |
| **가격** | 무료 | Free: 일 100건 무료 |

---

## 설치 및 시작

### 1. 설치

```bash
pip install kofinance
```

### 2. API 키 발급

[kofinance.ntriq.co.kr](https://kofinance.ntriq.co.kr)에서 회원가입하면 무료 API 키를 바로 발급받을 수 있습니다.

### 3. 환경변수 설정

```bash
export KOFINANCE_API_KEY="yap_your_key_here"
```

### 4. 첫 번째 요청

```python
from kofinance import KoFinance
import os

kf = KoFinance(os.environ["KOFINANCE_API_KEY"])

# 삼성전자 재무제표
df = kf.financials("005930")
print(df)
```

---

## 실전 예제

### 예제 1: 삼성전자 재무제표 분석

pykrx로는 매출액, 영업이익 같은 재무제표를 직접 가져올 수 없었습니다. DART API를 별도로 연동해야 했죠.

KoFinance는 한 줄이면 됩니다.

```python
from kofinance import KoFinance

kf = KoFinance("your-api-key")

# 3년치 연간 재무제표
df = kf.financials("005930", period="3y", type="annual")

# 주요 지표 확인
print(df[["period", "is_revenue", "is_operating_income", "ratio_roe"]])
```

출력:

```
  period    is_revenue         is_operating_income  ratio_roe
0   2025  302231000000000     58490000000000          13.2
1   2024  262200000000000     44280000000000          11.8
2   2023  258160000000000     36830000000000           9.5
```

### 예제 2: 가치주 스크리닝

"ROE 높고 PER 낮은 종목"을 찾으려면 pykrx로는 전 종목 루프가 필요했습니다 (30분+). KoFinance는 1초입니다.

```python
# ROE 15% 이상, PER 10배 이하, KOSPI
df = kf.screen(roe_gt=15, per_lt=10, market="KOSPI")

print(df[["symbol", "name", "roe", "per", "dividend_yield"]])
```

### 예제 3: 공시 모니터링

pykrx는 공시를 지원하지 않습니다. DART API를 직접 연동하면 corpCode 매핑, ZIP 파싱 등 복잡한 전처리가 필요합니다.

```python
# 삼성전자 최근 30일 공시 + AI 요약
df = kf.disclosures("005930", days=30)

for _, row in df.iterrows():
    print(f"[{row['date']}] {row['title']}")
    print(f"  → {row['summary']}")
    print()
```

### 예제 4: 트레이딩 시그널

골든크로스, RSI 과매도 같은 기술적 분석 시그널을 직접 구현할 필요가 없습니다.

```python
# 전 종목 골든크로스 시그널
signals = kf.signals(signal_type="golden_cross")

for _, s in signals.iterrows():
    print(f"[{s['name']}] {s['description']} (강도: {s['strength']})")
```

---

## 기존 코드 마이그레이션

pykrx에서 KoFinance로 전환하는 건 간단합니다.

### import 변경

```python
# Before
from pykrx import stock

# After
from kofinance import KoFinance
import os
kf = KoFinance(os.environ["KOFINANCE_API_KEY"])
```

### 메서드 매핑

| pykrx | KoFinance | 비고 |
|-------|-----------|------|
| `stock.get_market_ticker_list()` | `kf.stocks()` | DataFrame 반환, 시장/검색 필터 |
| `stock.get_market_fundamental()` | `kf.financials()` | 훨씬 상세 |
| `stock.get_market_ticker_name()` | `kf.stock("005930")["name"]` | 기본정보 포함 |
| _(미지원)_ | `kf.disclosures()` | AI 요약 포함 |
| _(수동 루프)_ | `kf.screen()` | 1줄, < 1초 |
| _(직접 구현)_ | `kf.signals()` | 골든크로스, RSI 등 |

### pandas 호환

KoFinance의 모든 메서드는 **pandas DataFrame**을 반환합니다. 기존에 pykrx 결과로 작성한 분석·시각화 코드는 컬럼명만 맞추면 그대로 사용할 수 있습니다.

```python
import matplotlib.pyplot as plt

df = kf.financials("005930", period="5y")

# 기존 matplotlib 코드 그대로 사용
plt.figure(figsize=(10, 6))
plt.bar(df["period"], df["is_revenue"] / 1e12)
plt.title("삼성전자 매출 추이 (조원)")
plt.show()
```

---

## 에러 처리

pykrx는 에러가 발생하면 불명확한 메시지를 던집니다. KoFinance는 구조화된 예외를 제공합니다.

```python
from kofinance import (
    KoFinance,
    AuthenticationError,
    RateLimitError,
    NotFoundError,
)

kf = KoFinance("your-api-key")

try:
    df = kf.financials("005930")
except AuthenticationError:
    print("API 키를 확인해주세요.")
except RateLimitError:
    print("요청 한도 초과. 잠시 후 다시 시도하세요.")
except NotFoundError:
    print("존재하지 않는 종목코드입니다.")
```

---

## 요금제

| 플랜 | 일일 요청 | 분당 요청 | 가격 |
|------|----------|----------|------|
| **Free** | 100 | 10 | **무료** |
| **Pro** | 10,000 | 100 | 월 29,000원 |
| **Enterprise** | 무제한 | 1,000 | 별도 문의 |

개인 분석·학습 용도라면 Free 플랜으로 충분합니다.

---

## 정리

| | pykrx | KoFinance |
|---|---|---|
| KRX 차단 대응 | 커뮤니티 수정 대기 | 공식 API, 영향 없음 |
| 재무제표 | 기본 지표만 | 전체 재무제표 |
| 공시 | 없음 | DART + AI 요약 |
| 스크리닝 | 수동 루프 (30분+) | API 1줄 (1초) |
| 시그널 | 직접 구현 | 내장 |
| 시작하기 | `pip install pykrx` | `pip install kofinance` + API 키 |

pykrx가 작동하지 않아서 이 글을 찾으셨다면, KoFinance를 시도해보세요.

```bash
pip install kofinance
```

API 키 발급: [kofinance.ntriq.co.kr](https://kofinance.ntriq.co.kr)
전체 문서: [kofinance.ntriq.co.kr/docs](https://kofinance.ntriq.co.kr/docs)

---

_이 글이 도움이 되었다면 공유해주세요. 질문은 dev@ntriq.co.kr로 보내주세요._
