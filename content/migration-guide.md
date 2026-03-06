# pykrx에서 KoFinance로 이전하기

> pykrx가 더 이상 작동하지 않나요? KRX 웹사이트 구조 변경으로 크롤링이 차단되었습니다. KoFinance API는 공식 데이터 소스 기반의 안정적인 대안입니다.

---

## pykrx, 왜 안 되나요?

2025년 하반기부터 KRX(한국거래소)가 웹사이트 구조를 대폭 변경하면서, pykrx의 핵심 크롤링 로직이 작동하지 않게 되었습니다.

```python
from pykrx import stock

# 2025년 이후: 빈 DataFrame 반환 또는 에러
df = stock.get_market_ohlcv("20260101", "20260305", "005930")
# → ConnectionError, empty DataFrame, 또는 파싱 실패
```

pykrx는 KRX 웹페이지를 스크래핑하는 비공식 라이브러리이기 때문에, KRX가 HTML 구조나 API 엔드포인트를 변경하면 즉시 깨집니다. 유지보수도 커뮤니티 기반이라 수정이 느립니다.

### pykrx의 근본적 한계

| 문제 | 설명 |
|------|------|
| **KRX 크롤링 차단** | 2025년 하반기 KRX 구조 변경으로 주요 기능 작동 불가 |
| **비공식 스크래핑** | KRX가 언제든 차단 가능, SLA 없음 |
| **느린 속도** | 매 요청마다 웹페이지 파싱, 대량 조회 시 수십 분 소요 |
| **제한된 데이터** | 기본 시세/지표만 제공, 재무제표·공시·시그널 없음 |
| **에러 처리 미흡** | 불명확한 에러 메시지, 디버깅 어려움 |
| **지원 없음** | 공식 기술 지원 없음 |

---

## KoFinance: 공식 API 기반 대안

KoFinance는 DART, KRX 공식 데이터를 직접 수집·가공하여 안정적인 REST API로 제공합니다.

| 항목 | pykrx | KoFinance |
|------|-------|-----------|
| 데이터 출처 | KRX 웹 스크래핑 (비공식) | DART + KRX 공식 수집 |
| 현재 상태 | **KRX 차단으로 작동 불가** | 정상 운영 (99.9% SLA) |
| 응답 속도 | 수 초~수십 분 | 평균 < 200ms |
| 재무제표 | PER/PBR/EPS 정도 | 손익계산서+재무상태표+현금흐름+비율 전체 |
| 공시 | 미지원 | DART 공시 + AI 요약 |
| 스크리닝 | 미지원 (수동 루프) | 조건 기반 API 1줄 |
| 시그널 | 미지원 (직접 구현) | 골든크로스, RSI 등 기술적 분석 |
| 에러 처리 | 불명확 | 구조화된 예외 클래스 |
| 반환 형식 | DataFrame (일부) | 전부 pandas DataFrame |

---

## 설치 비교

### Before (pykrx)

```bash
pip install pykrx
```

```python
from pykrx import stock
# 인증 불필요 (공개 크롤링)
# → 하지만 KRX 차단으로 작동 안 함
```

### After (KoFinance)

```bash
pip install kofinance
```

```python
from kofinance import KoFinance
import os

# API 키 인증 (안정적, 추적 가능)
kf = KoFinance(os.environ["KOFINANCE_API_KEY"])
```

> API 키는 [kofinance.ntriq.co.kr](https://kofinance.ntriq.co.kr)에서 무료로 발급받을 수 있습니다. Free 플랜: 일 100건.

---

## 코드 비교: 재무제표 조회

### Before (pykrx) — 작동 안 됨

```python
from pykrx import stock

# pykrx는 재무제표 직접 조회 불가!
# get_market_fundamental → PER, PBR, EPS, DIV, BPS만 제공
df = stock.get_market_fundamental("20260305", market="KOSPI")
# → KRX 차단으로 빈 DataFrame 또는 에러

# 재무제표가 필요하면? DART API를 직접 호출해야 함
import requests

url = "https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json"
params = {
    "crtfc_key": "DART_API_KEY_별도발급",  # DART 키 별도 발급 필요
    "corp_code": "00126380",                # 종목코드가 아니라 '고유번호'!
    "bsns_year": "2025",
    "reprt_code": "11011",                  # 사업보고서
    "fs_div": "CFS",                        # 연결재무제표
}
res = requests.get(url, params=params)
data = res.json()

# list 안에서 '매출액', '영업이익' 등을 수동으로 찾아야 함
for item in data.get("list", []):
    if item["account_nm"] == "매출액":
        revenue = item["thstrm_amount"]
    elif item["account_nm"] == "영업이익":
        operating_income = item["thstrm_amount"]
# ... 20줄 이상의 파싱 코드 필요
```

### After (KoFinance) — 한 줄

```python
from kofinance import KoFinance

kf = KoFinance("your-api-key")

# 삼성전자 3년치 연간 재무제표 — 한 줄
df = kf.financials("005930", period="3y", type="annual")

print(df[["period", "is_revenue", "is_operating_income", "ratio_roe", "ratio_per"]])
#   period    is_revenue         is_operating_income  ratio_roe  ratio_per
# 0   2025  302231000000000     58490000000000          13.2       12.5
# 1   2024  262200000000000     44280000000000          11.8       14.1
# 2   2023  258160000000000     36830000000000           9.5       18.3

# 여러 종목 동시 비교도 가능
df = kf.financials(["005930", "000660"], period="3y")
```

---

## 코드 비교: 종목 스크리닝

### Before (pykrx) — 작동 안 됨 + 비효율

```python
from pykrx import stock
import pandas as pd

# "ROE 15% 이상 + PER 10배 이하" 종목 찾기
date = "20260305"

# 1단계: 전체 종목 리스트 (900개+) — KRX 차단으로 실패
tickers = stock.get_market_ticker_list(date, market="KOSPI")

results = []
for ticker in tickers:  # 900개 종목 하나씩 조회...
    try:
        fund = stock.get_market_fundamental(date, date, ticker)
        if fund.empty:
            continue
        per = fund.iloc[-1]["PER"]
        # 문제: ROE는 get_market_fundamental에 없음!
        # → DART에서 별도 조회해야 함 (종목당 1회 API 호출)
        if 0 < per < 10:
            name = stock.get_market_ticker_name(ticker)
            results.append({"ticker": ticker, "name": name, "PER": per})
    except Exception:
        continue  # 에러 무시하고 계속...

df = pd.DataFrame(results)
# 실행 시간: 30분 이상 (작동한다면)
# ROE 필터링: 불가능
```

### After (KoFinance) — 한 줄, 1초

```python
from kofinance import KoFinance

kf = KoFinance("your-api-key")

# ROE 15% 이상, PER 10배 이하 — 한 줄
df = kf.screen(roe_gt=15, per_lt=10, market="KOSPI")

print(df[["symbol", "name", "roe", "per", "market_cap", "dividend_yield"]])
# symbol   name     roe   per  market_cap  dividend_yield
# 003550   LG      18.5   7.2     152000          3.4
# 034730   SK      16.2   8.9      98500          2.8
# ...

# 응답 시간: < 1초
# 추가 조건도 자유롭게:
df = kf.screen(
    roe_gt=15,
    per_lt=10,
    market="KOSPI",
    dividend_yield_gt=2.0,
    debt_ratio_lt=50,
)
```

---

## 코드 비교: 공시 조회

### Before — pykrx 미지원, DART 직접 호출

```python
import requests
import zipfile
import xml.etree.ElementTree as ET

DART_KEY = "your-dart-key"  # 별도 발급

# 1단계: 기업 고유번호 파일(corpCode.xml) 다운로드 + 파싱
# → 종목코드(005930)와 DART 고유번호(00126380)는 다름!
url = "https://opendart.fss.or.kr/api/corpCode.xml"
res = requests.get(url, params={"crtfc_key": DART_KEY})
# → ZIP 파일 → 압축 해제 → XML 파싱 → 매핑 딕셔너리 구성
# ... 15줄의 파싱 코드 ...

# 2단계: 공시 목록 조회
url = "https://opendart.fss.or.kr/api/list.json"
params = {
    "crtfc_key": DART_KEY,
    "corp_code": "00126380",
    "bgn_de": "20260201",
    "end_de": "20260305",
    "page_count": 100,
}
res = requests.get(url, params=params)

for d in res.json().get("list", []):
    print(f"{d['rcept_dt']} {d['report_nm']}")
    # AI 요약? → 없음. 제목과 URL만 제공.
```

### After (KoFinance) — AI 요약 포함

```python
from kofinance import KoFinance

kf = KoFinance("your-api-key")

# 공시 + AI 요약까지 한 줄
df = kf.disclosures("005930", days=30)

print(df[["date", "title", "summary"]])
# date        title                    summary
# 2026-03-01  사업보고서 (2025.12)     2025년 연결 매출 302.2조원(+15.3%)...
# 2026-02-28  배당결정                  주당 1,444원 현금배당 결정...
```

---

## 코드 비교: 트레이딩 시그널

### Before — 직접 구현 필요

```python
from pykrx import stock  # KRX 차단으로 실패
import numpy as np

# 골든크로스 감지: 전부 직접 구현
ticker = "005930"
df = stock.get_market_ohlcv("20250901", "20260305", ticker)  # 실패

# 이동평균 계산
df["MA20"] = df["종가"].rolling(20).mean()
df["MA60"] = df["종가"].rolling(60).mean()

# 골든크로스 감지
df["signal"] = np.where(
    (df["MA20"] > df["MA60"]) & (df["MA20"].shift(1) <= df["MA60"].shift(1)),
    "golden_cross", None
)
# RSI, MACD, 볼린저 밴드? → 각각 20줄씩 추가 구현 필요
# 전 종목 스캔? → 900개 종목 × 수백일 데이터 = 수 시간
```

### After (KoFinance) — 전 종목, 한 줄

```python
from kofinance import KoFinance

kf = KoFinance("your-api-key")

# 전 종목 골든크로스 시그널
signals = kf.signals(signal_type="golden_cross")
print(signals[["symbol", "name", "strength", "description"]])

# 특정 종목 모든 시그널
my_signals = kf.signals(symbol="005930")
```

---

## 이전 체크리스트

### Step 1: 설치

```bash
pip install kofinance
```

### Step 2: API 키 발급

1. [kofinance.ntriq.co.kr](https://kofinance.ntriq.co.kr) 회원가입
2. 대시보드 → API 키 발급
3. 환경변수 설정:

```bash
export KOFINANCE_API_KEY="yap_your_key_here"
```

### Step 3: import 교체

```python
# Before
from pykrx import stock

# After
from kofinance import KoFinance
import os
kf = KoFinance(os.environ["KOFINANCE_API_KEY"])
```

### Step 4: 메서드 매핑 표

| 기존 (pykrx) | 대체 (KoFinance) | 비고 |
|--------------|-----------------|------|
| `stock.get_market_ticker_list()` | `kf.stocks()` | DataFrame 반환 |
| `stock.get_market_fundamental()` | `kf.financials()` | 훨씬 상세한 데이터 |
| `stock.get_market_ohlcv()` | 추후 지원 예정 | |
| (미지원) | `kf.disclosures()` | AI 요약 포함 |
| (수동 루프) | `kf.screen()` | 조건 필터링 1줄 |
| (직접 구현) | `kf.signals()` | 기술적 분석 시그널 |

### Step 5: 에러 처리 추가

```python
from kofinance import KoFinance, RateLimitError, NotFoundError
import time

kf = KoFinance("your-api-key")

try:
    df = kf.financials("005930")
except RateLimitError:
    time.sleep(60)
    df = kf.financials("005930")
except NotFoundError:
    print("존재하지 않는 종목코드입니다.")
```

---

## FAQ

**Q: pykrx가 다시 작동하면 돌아가도 되나요?**
A: pykrx는 비공식 스크래핑이라 KRX가 언제든 다시 차단할 수 있습니다. 프로덕션 환경이라면 공식 API 기반인 KoFinance를 권장합니다.

**Q: Free 플랜으로 충분한가요?**
A: 개인 분석/학습용이면 일 100건으로 충분합니다. 자동화나 대량 조회가 필요하면 Pro(일 10,000건, 월 29,000원)를 추천합니다.

**Q: 기존 Jupyter 노트북을 그대로 쓸 수 있나요?**
A: import와 메서드 호출만 변경하면 됩니다. 반환이 pandas DataFrame이므로 기존 분석·시각화 코드는 그대로 사용 가능합니다.

**Q: OHLCV(일별 시세) 데이터도 있나요?**
A: 현재는 재무제표·공시·스크리닝·시그널에 집중하고 있으며, OHLCV 엔드포인트는 추후 추가 예정입니다.

**Q: pykrx와 동시에 설치해도 되나요?**
A: 네, 독립 패키지이므로 충돌 없이 공존합니다. 점진적으로 이전하세요.
