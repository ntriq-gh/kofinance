# pykrx에서 KoFinance로 이전하기

한국 주식 데이터를 다뤄본 파이썬 개발자라면 [pykrx](https://github.com/sharebook-kr/pykrx)를 한 번쯤 써봤을 것입니다. pykrx는 KRX 데이터를 파이썬으로 가져올 수 있는 유용한 라이브러리이지만, 프로덕션 환경에서 사용하기에는 여러 한계가 있습니다.

이 글에서는 pykrx의 한계점과, KoFinance API로 이전하면 얻을 수 있는 장점을 코드 비교와 함께 살펴봅니다.

---

## 왜 이전해야 할까?

### pykrx의 한계

| 항목 | pykrx | 비고 |
|------|-------|------|
| 데이터 출처 | KRX 웹사이트 스크래핑 | 비공식, 구조 변경 시 깨짐 |
| 안정성 | KRX 점검/변경 시 에러 | 주말/야간 불안정 |
| 속도 | 요청마다 웹페이지 파싱 | 대량 조회 시 느림 |
| 재무제표 | 제한적 (기본 지표만) | 현금흐름표, AI 분석 없음 |
| 공시 | 지원 안 함 | DART API 직접 연동 필요 |
| 스크리닝 | 지원 안 함 | 수동 루프 필요 |
| 시그널 | 지원 안 함 | ta-lib 등 별도 구현 |
| 에러 처리 | 불명확한 에러 메시지 | 디버깅 어려움 |
| 지원 | 커뮤니티 기반 | 공식 지원 없음 |

### KoFinance의 장점

| 항목 | KoFinance | 비고 |
|------|-----------|------|
| 데이터 출처 | 공식 API (DART, KRX 직접 수집) | 안정적, 검증된 데이터 |
| 안정성 | 99.9% SLA | 24/7 모니터링 |
| 속도 | 캐싱된 API | 평균 응답 < 200ms |
| 재무제표 | 손익/재무상태/현금흐름/비율 전체 | 연간 + 분기 |
| 공시 | DART 공시 + AI 요약 | 핵심 요약 자동 제공 |
| 스크리닝 | 조건 기반 필터링 API | 한 줄이면 끝 |
| 시그널 | 기술적 분석 시그널 | 골든크로스, RSI 등 |
| 에러 처리 | 구조화된 에러 코드 | 명확한 예외 클래스 |
| 지원 | 공식 기술 지원 | 문서 + 이메일 |

---

## Before vs After 코드 비교

### 1. 재무제표 조회

**Before (pykrx):**

```python
from pykrx import stock
import pandas as pd

# pykrx는 재무제표 직접 조회 불가
# stock.get_market_fundamental로 기본 지표만 가능
df = stock.get_market_fundamental("20260305", market="KOSPI")
# PER, PBR, EPS, DIV, BPS 정도만 제공
# 매출액, 영업이익, 순이익? → 별도 크롤링 필요

# DART OpenAPI를 직접 호출해야 함
import requests
url = "https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json"
params = {
    "crtfc_key": "DART_API_KEY",  # 별도 발급 필요
    "corp_code": "00126380",       # 종목코드가 아닌 고유번호!
    "bsns_year": "2025",
    "reprt_code": "11011",
    "fs_div": "CFS",
}
res = requests.get(url, params=params)
data = res.json()
# 데이터 파싱 20줄 추가 필요...
```

**After (KoFinance):**

```python
from kofinance import KoFinance

kf = KoFinance("your-api-key")

# 한 줄로 재무제표 전체 조회
df = kf.financials("005930", period="3y", type="annual")
print(df[["period", "is_revenue", "is_operating_income", "ratio_roe"]])
#   period    is_revenue  is_operating_income  ratio_roe
# 0   2025  302231000...        58490000...       13.2
# 1   2024  262200000...        44280000...       11.8
# 2   2023  258160000...        36830000...        9.5
```

### 2. 종목 스크리닝

**Before (pykrx):**

```python
from pykrx import stock
import pandas as pd

# ROE 15% 이상, PER 10배 이하 종목 찾기
date = "20260305"
tickers = stock.get_market_ticker_list(date, market="KOSPI")

results = []
for ticker in tickers:  # 900개+ 종목 순회...
    try:
        fund = stock.get_market_fundamental(date, date, ticker)
        if fund.empty:
            continue
        per = fund.iloc[-1]["PER"]
        # ROE는 get_market_fundamental에 없음!
        # → DART에서 별도로 가져와야 함
        if per > 0 and per < 10:
            name = stock.get_market_ticker_name(ticker)
            results.append({"ticker": ticker, "name": name, "PER": per})
    except Exception:
        continue  # 에러 무시...

df = pd.DataFrame(results)
# 수십 분 소요, ROE 필터링 불가
```

**After (KoFinance):**

```python
from kofinance import KoFinance

kf = KoFinance("your-api-key")

# 한 줄로 끝
df = kf.screen(roe_gt=15, per_lt=10, market="KOSPI")
print(df[["symbol", "name", "roe", "per", "market_cap"]])
# 1초 이내 응답
```

### 3. 공시 조회

**Before (pykrx → 지원 안 됨, DART 직접 호출):**

```python
import requests

# DART API 키 별도 발급 필요
DART_KEY = "your-dart-api-key"

# 1) 먼저 기업 고유번호 조회 (종목코드 ≠ 고유번호)
# corpCode.xml 다운로드 + 파싱 필요...

# 2) 공시 목록 조회
url = "https://opendart.fss.or.kr/api/list.json"
params = {
    "crtfc_key": DART_KEY,
    "corp_code": "00126380",  # 삼성전자 고유번호
    "bgn_de": "20260201",
    "end_de": "20260305",
    "page_count": 100,
}
res = requests.get(url, params=params)
data = res.json()

# 3) 결과 파싱
disclosures = data.get("list", [])
for d in disclosures:
    print(f"{d['rcept_dt']} {d['report_nm']}")
    # AI 요약? → 직접 구현해야 함
```

**After (KoFinance):**

```python
from kofinance import KoFinance

kf = KoFinance("your-api-key")

# 한 줄. AI 요약까지 포함.
df = kf.disclosures("005930", days=30)
print(df[["date", "title", "summary"]])
# date        title                      summary
# 2026-03-01  사업보고서 (2025.12)       2025년 연결 매출 302.2조원...
```

### 4. 트레이딩 시그널

**Before (직접 구현):**

```python
from pykrx import stock
import pandas as pd
import numpy as np

# 골든크로스 감지를 위한 수동 구현
ticker = "005930"
df = stock.get_market_ohlcv("20250901", "20260305", ticker)

# 이동평균 계산
df["MA20"] = df["종가"].rolling(20).mean()
df["MA60"] = df["종가"].rolling(60).mean()

# 골든크로스 감지
df["signal"] = np.where(
    (df["MA20"] > df["MA60"]) & (df["MA20"].shift(1) <= df["MA60"].shift(1)),
    "golden_cross",
    None,
)

golden_cross_dates = df[df["signal"] == "golden_cross"]
# 한 종목만 가능, 전 종목 스캔하려면 루프...
# RSI, MACD, 볼린저 밴드도 각각 구현 필요
```

**After (KoFinance):**

```python
from kofinance import KoFinance

kf = KoFinance("your-api-key")

# 전 종목 골든크로스 시그널 한 줄
signals = kf.signals(signal_type="golden_cross")
print(signals[["symbol", "name", "strength", "description"]])

# 특정 종목의 모든 시그널
my_signals = kf.signals(symbol="005930")
```

---

## 이전 체크리스트

### Step 1: SDK 설치

```bash
pip install kofinance
# pykrx는 제거하지 않아도 됩니다 (공존 가능)
```

### Step 2: API 키 발급

1. [kofinance.ntriq.co.kr](https://kofinance.ntriq.co.kr) 회원가입
2. 대시보드에서 API 키 발급
3. 환경 변수 설정:

```bash
export KOFINANCE_API_KEY="yap_your_key_here"
```

### Step 3: import 변경

```python
# Before
from pykrx import stock

# After
from kofinance import KoFinance
import os

kf = KoFinance(os.environ["KOFINANCE_API_KEY"])
```

### Step 4: 메서드 매핑

| pykrx | KoFinance | 비고 |
|-------|-----------|------|
| `stock.get_market_ticker_list()` | `kf.stocks()` | DataFrame 반환 |
| `stock.get_market_fundamental()` | `kf.financials()` | 훨씬 풍부한 데이터 |
| (지원 안 함) | `kf.disclosures()` | AI 요약 포함 |
| (직접 구현) | `kf.screen()` | 조건 필터링 |
| (직접 구현) | `kf.signals()` | 기술적 분석 |

### Step 5: 에러 처리 추가

```python
from kofinance import KoFinance, KoFinanceError, RateLimitError

try:
    df = kf.financials("005930")
except RateLimitError:
    time.sleep(60)
    df = kf.financials("005930")
except KoFinanceError as e:
    print(f"에러: {e.message}")
```

---

## FAQ

**Q: pykrx와 KoFinance를 같이 쓸 수 있나요?**
A: 네, 독립적인 패키지이므로 동시 설치/사용이 가능합니다. 점진적으로 이전하세요.

**Q: pykrx에서 가져오던 OHLCV(일별 시세) 데이터도 있나요?**
A: 현재는 재무제표, 공시, 스크리닝, 시그널에 집중하고 있으며, OHLCV 엔드포인트는 추후 추가 예정입니다.

**Q: Free 플랜으로 충분한가요?**
A: 개인 학습/분석 용도라면 일 100건으로 충분합니다. 자동화나 대량 조회가 필요하면 Pro 플랜을 추천합니다.

**Q: 데이터 정확도는 어떤가요?**
A: DART 전자공시와 KRX 공식 데이터를 직접 수집·검증합니다. pykrx의 스크래핑 방식보다 안정적이고 정확합니다.

**Q: 기존 Jupyter 노트북을 바로 전환할 수 있나요?**
A: 네, import와 메서드 호출만 변경하면 됩니다. 반환 형식이 pandas DataFrame이므로 기존 분석 코드는 그대로 사용 가능합니다.
