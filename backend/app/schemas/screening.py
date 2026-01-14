from pydantic import BaseModel, Field
from typing import List, Optional

class ScreeningRule(BaseModel):
    """筛选规则"""
    indicator: str = Field(..., description="指标名称: close|volume|turnover|high|low|open")
    operator: str = Field(..., description="操作符: >|<|>=|<=|==")
    value: float = Field(..., description="指标值")

class RuleScreeningRequest(BaseModel):
    """规则筛选请求"""
    symbols: Optional[List[str]] = Field(None, description="股票代码列表，为空则使用默认列表")
    start_date: str = Field(..., description="开始日期，格式：YYYY-MM-DD")
    end_date: str = Field(..., description="结束日期，格式：YYYY-MM-DD")
    rules: List[ScreeningRule] = Field(..., description="筛选规则列表")
    market: str = Field(..., description="股票市场，如：cn, hk, us")
    exchange: Optional[str] = Field(None, description="证券交易所，如：sh, sz, hkex, nasdaq")

class MatchedStock(BaseModel):
    """匹配的股票"""
    symbol: str
    name: str
    industry: str
    market: str

class RuleScreeningResponse(BaseModel):
    """规则筛选响应"""
    total: int
    stocks: List[MatchedStock]
    request: dict

class AIScreeningRequest(BaseModel):
    """AI筛选请求"""
    query: str = Field(..., description="自然语言查询")
    symbols: Optional[List[str]] = Field(None, description="股票代码列表，为空则使用默认列表")
    start_date: str = Field(..., description="开始日期，格式：YYYY-MM-DD")
    end_date: str = Field(..., description="结束日期，格式：YYYY-MM-DD")
    ai_config: Optional[dict] = Field(None, description="AI模型配置")
    market: str = Field(..., description="股票市场，如：cn, hk, us")
    exchange: Optional[str] = Field(None, description="证券交易所，如：sh, sz, hkex, nasdaq")

class AIScreeningResponse(BaseModel):
    """AI筛选响应"""
    total: int
    stocks: List[MatchedStock]
    query: str
    rules: Optional[List[ScreeningRule]] = Field(None, description="解析出的筛选规则")
    explanation: str
