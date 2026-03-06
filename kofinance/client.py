import httpx
import pandas as pd
from typing import List, Optional, Union

from .exceptions import AuthenticationError, RateLimitError, NotFoundError


class KoFinance:
    """KoFinance API Python SDK"""

    DEFAULT_BASE_URL = "https://api.ntriq.co.kr/kofinance/api/v1"

    def __init__(self, api_key: str, base_url: str = None):
        self.api_key = api_key
        self.base_url = base_url or self.DEFAULT_BASE_URL
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={"X-YAP-Key": api_key},
            timeout=30.0,
        )

    def _request(self, method: str, path: str, params: dict = None) -> dict:
        """HTTP 요청 공통 처리"""
        response = self._client.request(method, path, params=params)
        if response.status_code == 401:
            raise AuthenticationError("Invalid API key", status_code=401)
        if response.status_code == 429:
            raise RateLimitError("Rate limit exceeded", status_code=429)
        if response.status_code == 404:
            raise NotFoundError(f"Resource not found: {path}", status_code=404)
        response.raise_for_status()
        return response.json()

    def stocks(self, market: str = "ALL", search: str = None, limit: int = 100) -> pd.DataFrame:
        """전 상장사 종목 리스트

        Args:
            market: 시장 구분 (ALL, KOSPI, KOSDAQ, KONEX)
            search: 종목명 또는 코드 검색
            limit: 최대 반환 수

        Returns:
            종목 목록 DataFrame
        """
        params = {"market": market, "limit": limit}
        if search:
            params["search"] = search
        data = self._request("GET", "/stocks", params)
        return pd.DataFrame(data.get("stocks", []))

    def stock(self, symbol: str) -> dict:
        """기업 기본정보

        Args:
            symbol: 종목코드 (예: "005930")

        Returns:
            기업 기본정보 dict
        """
        return self._request("GET", f"/stocks/{symbol}")

    def financials(
        self,
        symbol: Union[str, List[str]],
        period: str = "3y",
        type: str = "annual",
        as_dataframe: bool = True,
    ) -> Union[pd.DataFrame, dict]:
        """재무제표 조회

        Args:
            symbol: 종목코드 (단일 문자열 또는 리스트)
            period: 조회 기간 (1y / 3y / 5y)
            type: 재무제표 유형 (annual / quarterly)
            as_dataframe: True면 flat DataFrame 반환, False면 원본 dict 반환

        Returns:
            재무제표 DataFrame 또는 dict
        """
        if isinstance(symbol, list):
            results = []
            for s in symbol:
                data = self._request(
                    "GET",
                    f"/stocks/{s}/financials",
                    {"period": period, "type": type},
                )
                for f in data.get("financials", []):
                    f["symbol"] = s
                    f["name"] = data.get("name")
                    results.append(f)
            if as_dataframe:
                return self._financials_to_df(results)
            return results
        else:
            data = self._request(
                "GET",
                f"/stocks/{symbol}/financials",
                {"period": period, "type": type},
            )
            if as_dataframe:
                return self._financials_to_df(data.get("financials", []))
            return data

    def disclosures(self, symbol: str, days: int = 30, type: str = "all") -> List[dict]:
        """공시 목록 + AI 요약

        Args:
            symbol: 종목코드
            days: 최근 N일 이내 공시
            type: 공시 유형 필터 (all / earnings / material / etc.)

        Returns:
            공시 목록 (AI 요약 포함)
        """
        data = self._request(
            "GET",
            f"/stocks/{symbol}/disclosures",
            {"days": days, "type": type},
        )
        return data.get("disclosures", [])

    def signals(self, symbol: str) -> List[dict]:
        """대체 데이터 시그널 (Phase 2)

        Args:
            symbol: 종목코드

        Returns:
            시그널 목록
        """
        data = self._request("GET", f"/stocks/{symbol}/signals")
        return data.get("signals", [])

    def screen(self, **kwargs) -> pd.DataFrame:
        """조건 기반 종목 스크리닝 (Phase 2)

        Args:
            **kwargs: 스크리닝 조건 (예: market="KOSPI", per_lt=10, roe_gt=15)

        Returns:
            조건에 맞는 종목 DataFrame
        """
        data = self._request("GET", "/screen", params=kwargs)
        return pd.DataFrame(data.get("results", []))

    def _financials_to_df(self, financials: list) -> pd.DataFrame:
        """재무제표 리스트를 flat DataFrame으로 변환"""
        rows = []
        for f in financials:
            row = {
                "symbol": f.get("symbol", ""),
                "name": f.get("name", ""),
                "period": f.get("period", ""),
                "type": f.get("type", ""),
            }
            for k, v in f.get("income_statement", {}).items():
                row[f"is_{k}"] = v
            for k, v in f.get("balance_sheet", {}).items():
                row[f"bs_{k}"] = v
            for k, v in f.get("ratios", {}).items():
                row[f"ratio_{k}"] = v
            for k, v in (f.get("cash_flow") or {}).items():
                row[f"cf_{k}"] = v
            rows.append(row)
        return pd.DataFrame(rows)

    def close(self):
        """HTTP 클라이언트 종료"""
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
