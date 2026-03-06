# KoFinance

한국 금융 데이터 API — DART 재무제표, 공시, AI 요약을 깨끗한 REST API와 Python SDK로 제공합니다.

> pykrx, FinanceDataReader가 KRX 회원제 전환으로 작동하지 않나요?
> KoFinance는 DART OpenAPI 기반의 안정적인 대안입니다.

## 설치

```bash
pip install kofinance
```

## 빠른 시작

```python
from kofinance import KoFinance

kf = KoFinance(api_key="YOUR_API_KEY")

# 전 종목 리스트 (KOSPI + KOSDAQ + 기타)
stocks = kf.stocks()
print(f"총 {len(stocks)}개 종목")

# 삼성전자 재무제표 (최근 3년)
fs = kf.financials("005930", period="3y")
print(fs[["revenue", "operating_income", "net_income"]])

# 삼성전자 공시 + AI 요약
disclosures = kf.disclosures("005930", days=30)
print(disclosures[["title", "date", "summary"]])

# 조건 스크리닝
results = kf.screen(market="KOSPI", per_lt=10, roe_gt=15)
```

## 제공 데이터

| 데이터 | 설명 | 상태 |
|--------|------|------|
| 전 종목 기본정보 | KOSPI/KOSDAQ/기타 3,900+ 종목 | ✅ |
| 재무제표 | 매출, 영업이익, 순이익 등 35+ 항목 | ✅ |
| 재무비율 | ROE, PER, 부채비율, 영업이익률 등 자동 계산 | ✅ |
| 성장률/트렌드 | YoY 성장률, 3년 CAGR | ✅ |
| 공시 | DART 공시 원문 + AI 요약 | ✅ |
| 배당 | 주당배당금, EPS | ✅ |
| 대체 데이터 시그널 | 특허/소송/정책 (Phase 2) | 🚧 |

## API 엔드포인트

```
GET /kofinance/api/v1/stocks                          전 종목 리스트
GET /kofinance/api/v1/stocks/{symbol}                 기업 기본정보
GET /kofinance/api/v1/stocks/{symbol}/financials      재무제표 + 비율
GET /kofinance/api/v1/stocks/{symbol}/disclosures     공시 + AI 요약
```

## pykrx와 비교

| | pykrx | KoFinance |
|---|---|---|
| 데이터 소스 | KRX 스크래핑 (차단됨) | DART OpenAPI (공식) |
| 안정성 | KRX 변경 시 중단 | API 기반, 안정적 |
| 재무제표 | ❌ 미지원 | ✅ 35+ 항목 |
| AI 요약 | ❌ | ✅ 공시 AI 요약 |
| 대체 데이터 | ❌ | ✅ 특허/소송/정책 (Phase 2) |
| 설치 | `pip install pykrx` | `pip install kofinance` |

## 시작하기

1. **API 키 발급**: [ntriq.co.kr](https://ntriq.co.kr) 에서 무료 발급
2. **SDK 설치**: `pip install kofinance`
3. **데이터 조회**: 위 코드 예시 참고

- 일 1,000건 API 호출 무료
- 신용카드 불필요

## 문서

- [API 문서](https://ntriq.co.kr/kofinance/docs)
- [마이그레이션 가이드 (pykrx → KoFinance)](content/migration-guide.md)
- [삼성전자 재무 분석 예제 (Jupyter)](content/examples/samsung-financial-analysis.ipynb)

## 문의

- **이메일**: support@ntriq.co.kr
- **GitHub Issues**: [이슈 등록](https://github.com/ntriq-gh/kofinance/issues)
- **API 키 발급 / 기술 지원 / Enterprise 문의** 모두 이메일로 연락주세요.

## 데이터 출처

- 재무제표/공시: [금융감독원 전자공시시스템(DART)](https://dart.fss.or.kr)
- 기업정보: DART 기업개황 API

## 라이선스

MIT

---

Built by [ntriq](https://ntriq.co.kr) — 한국 금융 데이터 인프라
