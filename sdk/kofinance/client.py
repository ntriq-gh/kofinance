import httpx
import pandas as pd
from typing import Dict, List, Optional, Union

from .exceptions import (
    APIError,
    AuthenticationError,
    KoFinanceError,
    NotFoundError,
    RateLimitError,
)


class KoFinance:
    """KoFinance API Python SDK

    한국 상장사 재무제표, 공시, 종목 스크리닝, 트레이딩 시그널을
    pandas DataFrame으로 간편하게 조회할 수 있습니다.

    Usage:
        >>> from kofinance import KoFinance
        >>> kf = KoFinance("your-api-key")
        >>> df = kf.financials("005930")
    """

    DEFAULT_BASE_URL = "https://api.ntriq.co.kr/kofinance/api/v1"

    def __init__(self, api_key: str, base_url: str = None, timeout: float = 30.0):
        """KoFinance 클라이언트 초기화

        Args:
            api_key: KoFinance API 키
            base_url: API 서버 URL (기본값: 프로덕션 서버)
            timeout: 요청 타임아웃 (초)
        """
        self.api_key = api_key
        self.base_url = base_url or self.DEFAULT_BASE_URL
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={
                "X-YAP-Key": api_key,
                "User-Agent": "kofinance-python/0.1.0",
            },
            timeout=timeout,
        )

    def _request(
        self, method: str, path: str, params: dict = None, json: dict = None
    ) -> dict:
        """HTTP 요청 공통 처리"""
        response = self._client.request(method, path, params=params, json=json)

        if response.status_code == 401:
            raise AuthenticationError("Invalid API key", status_code=401)
        if response.status_code == 429:
            raise RateLimitError("Rate limit exceeded", status_code=429)
        if response.status_code == 404:
            raise NotFoundError(f"Resource not found: {path}", status_code=404)
        if response.status_code >= 400:
            try:
                err = response.json().get("error", {})
                msg = err.get("message", response.text)
                code = err.get("code")
            except Exception:
                msg = response.text
                code = None
            raise APIError(msg, status_code=response.status_code, code=code)

        return response.json()

    def stocks(
        self, market: str = "ALL", search: str = None, limit: int = 100
    ) -> pd.DataFrame:
        """전 상장사 종목 리스트

        Args:
            market: 시장 구분 (ALL, KOSPI, KOSDAQ, KONEX)
            search: 종목명 또는 코드 검색
            limit: 최대 반환 수 (기본 100)

        Returns:
            종목 목록 DataFrame (columns: symbol, name, market, sector, ...)
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
            type: annual (연간) 또는 quarterly (분기)
            as_dataframe: True면 DataFrame 반환, False면 원본 dict

        Returns:
            재무제표 DataFrame (is_revenue, is_operating_income, bs_total_assets, ratio_roe 등)
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

    def disclosures(
        self, symbol: str, days: int = 30, type: str = "all"
    ) -> pd.DataFrame:
        """공시 목록 + AI 요약

        Args:
            symbol: 종목코드
            days: 최근 N일 이내 공시 (기본 30일)
            type: 공시 유형 (all / earnings / material / etc.)

        Returns:
            공시 목록 DataFrame (columns: id, title, type, date, url, summary)
        """
        data = self._request(
            "GET",
            f"/stocks/{symbol}/disclosures",
            {"days": days, "type": type},
        )
        return pd.DataFrame(data.get("disclosures", []))

    def screen(self, **filters) -> pd.DataFrame:
        """조건 기반 종목 스크리닝

        Args:
            **filters: 스크리닝 조건
                - market: 시장 (KOSPI, KOSDAQ)
                - per_lt: PER 상한
                - per_gt: PER 하한
                - roe_gt: ROE 하한
                - roe_lt: ROE 상한
                - pbr_lt: PBR 상한
                - market_cap_gt: 시가총액 하한 (억원)
                - dividend_yield_gt: 배당수익률 하한 (%)
                - sector: 업종

        Returns:
            조건에 맞는 종목 DataFrame
        """
        data = self._request("GET", "/screen", params=filters)
        return pd.DataFrame(data.get("results", []))

    def signals(
        self, symbol: str = None, signal_type: str = None
    ) -> pd.DataFrame:
        """트레이딩 시그널 조회

        Args:
            symbol: 종목코드 (None이면 전체)
            signal_type: 시그널 유형 (golden_cross, death_cross,
                         volume_spike, rsi_oversold, rsi_overbought 등)

        Returns:
            시그널 목록 DataFrame (columns: symbol, name, signal_type,
                                  strength, timestamp, description)
        """
        params = {}
        if symbol:
            params["symbol"] = symbol
        if signal_type:
            params["signal_type"] = signal_type
        data = self._request("GET", "/signals", params=params)
        return pd.DataFrame(data.get("signals", []))

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

    def __repr__(self):
        return f"KoFinance(base_url='{self.base_url}')"
