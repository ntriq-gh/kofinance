from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class Stock:
    symbol: str
    name: str
    market: str  # KOSPI, KOSDAQ, KONEX


@dataclass
class Financial:
    period: str
    type: str  # annual, quarterly
    consolidated: bool
    income_statement: Dict[str, Any]
    balance_sheet: Dict[str, Any]
    ratios: Dict[str, Any]
    cash_flow: Optional[Dict[str, Any]] = None


@dataclass
class Disclosure:
    id: str
    title: str
    type: str
    date: str
    url: Optional[str] = None
    summary: Optional[str] = None
    key_points: Optional[List[str]] = None
