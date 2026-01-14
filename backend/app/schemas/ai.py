from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# 交易员策略配置
class TraderStrategy(BaseModel):
    """交易员策略配置"""
    risk_preference: str = Field("medium", description="风险偏好: low, medium, high")
    trend_sensitivity: str = Field("medium", description="趋势敏感度: low, medium, high")
    bias: Optional[str] = Field(None, description="多空偏好: long, short, neutral")

# AI交易员配置
class AIConfig(BaseModel):
    """AI交易员配置"""
    trader_name: str = Field(..., description="交易员名称")
    ai_model: str = Field(..., description="AI模型名称")
    api_url: str = Field(..., description="API URL")
    api_key: str = Field(..., description="API Key")
    strategy: TraderStrategy = Field(..., description="交易策略")

# 历史相似走势
class HistoricalSimilarPattern(BaseModel):
    """历史相似走势"""
    pattern_date: str = Field(..., description="相似走势日期")
    kline_segment: str = Field(..., description="K线片段描述")
    result: str = Field(..., description="走势结果: 上涨, 下跌, 震荡")
    return_value: float = Field(..., alias="return", description="涨跌幅: 正数为上涨，负数为下跌")
    similarity: float = Field(..., description="相似度: 0-1")

# AI分析请求 - 支持交易员策略
class AIAnalysisRequest(BaseModel):
    """AI分析请求"""
    symbol: str = Field(..., description="股票代码")
    start_date: Optional[str] = Field(None, description="开始日期，格式：YYYY-MM-DD")
    end_date: Optional[str] = Field(None, description="结束日期，格式：YYYY-MM-DD")
    # 可选的历史数据缓存（前端可以传入已获取的历史数据，后端将优先使用）
    history_data: Optional[List[Dict[str, Any]]] = Field(None, description="可选的历史数据列表")
    ai_config: Optional[Dict[str, Any]] = Field(None, description="AI模型配置")
    strategy: Optional[TraderStrategy] = Field(None, description="交易员策略")

# AI分析响应 - 结构化输出
class AIAnalysisResponse(BaseModel):
    """AI分析响应"""
    symbol: str
    action: str = Field(..., description="操作建议: 买入, 卖出, 持有")
    trend: str = Field(..., description="趋势判断: 多头, 空头, 震荡")
    logic: str = Field(..., description="分析逻辑")
    confidence: float = Field(..., description="置信度: 0-1")
    expected_return: float = Field(..., description="预期收益率: 0-1")
    will_trade: bool = Field(..., description="是否会进行交易: true/false")
    support_level: Optional[str] = Field(None, description="近期支撑区间")
    resistance_level: Optional[str] = Field(None, description="近期压力区间")
    historical_similar_patterns: List[HistoricalSimilarPattern] = Field(..., description="历史相似走势")
    detailed_analysis: Optional[Dict[str, Any]] = Field(None, description="详细分析")
