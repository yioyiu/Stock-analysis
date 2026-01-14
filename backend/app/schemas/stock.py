from pydantic import BaseModel, Field
from typing import List, Optional

class StockDataItem(BaseModel):
    """股票数据项"""
    date: str
    open: float
    close: float
    high: float
    low: float
    volume: int
    turnover: float

class StockHistoryResponse(BaseModel):
    """股票历史数据响应"""
    symbol: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    adjust: str
    data: List[StockDataItem]

class StockBasicResponse(BaseModel):
    """股票基本信息响应"""
    symbol: str
    name: str
    industry: str
    area: str
    market: str
