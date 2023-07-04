from dataclasses import dataclass


@dataclass
class Alert:
    coin_id: str
    value: float
    chat_id: int
    status: bool = True


@dataclass
class TradingViewData:
    timestamp: float
    open: float
    high: float
    low: float
    current: float
