"""KoFinance SDK 빠른 시작 예시"""
from kofinance import KoFinance

kf = KoFinance(api_key="kf_xxxxx")

# 종목 목록 조회
stocks = kf.stocks(market="KOSPI")
print("KOSPI 상장사 수:", len(stocks))
print(stocks.head())

# 기업 기본정보
info = kf.stock("005930")
print("\n삼성전자 기본정보:")
print(info)

# 재무제표 (단일 종목)
fs = kf.financials("005930", period="3y")
print("\n삼성전자 재무제표:")
print(fs)

# 재무제표 (여러 종목 한번에)
fs = kf.financials(["005930", "000660", "035420"], period="3y")
print("\n여러 종목 재무제표:")
print(fs.head())

# 공시 + AI 요약
disclosures = kf.disclosures("005930", days=30)
print("\n최근 30일 공시:")
for d in disclosures:
    print(f"[{d['date']}] {d['title']}")
    if d.get("summary"):
        print(f"  → {d['summary']}")
    if d.get("key_points"):
        for point in d["key_points"]:
            print(f"  • {point}")

# 컨텍스트 매니저로 사용 (자동 close)
with KoFinance(api_key="kf_xxxxx") as kf2:
    result = kf2.financials("005930", period="1y", type="quarterly")
    print("\n삼성전자 분기 재무제표:")
    print(result)

# 스크리닝 (Phase 2 - 현재 미지원)
# results = kf.screen(market="KOSPI", per_lt=10, roe_gt=15)
# print(results)

# 대체 데이터 시그널 (Phase 2 - 현재 미지원)
# signals = kf.signals("005930")
# for s in signals:
#     print(s)
