from typing import List, Dict, Any
from app.services.stock_data_service import StockDataService
from app.services.ai_analysis_service import AIAnalysisService
from app.schemas.screening import RuleScreeningRequest, AIScreeningRequest

class ScreeningService:
    def __init__(self):
        self.stock_data_service = StockDataService()
        self.ai_analysis_service = AIAnalysisService()
    
    def rule_based_screening(self, request: RuleScreeningRequest):
        """基于规则的股票筛选"""
        # 获取股票列表
        market = getattr(request, 'market', 'cn')
        exchange = getattr(request, 'exchange', None)
        symbols = request.symbols or self.stock_data_service.get_stock_symbols(market=market, exchange=exchange)
        
        # 筛选结果
        matched_stocks = []
        
        # 遍历股票进行筛选
        for symbol in symbols[:50]:  # 限制处理50只股票，避免请求过多
            try:
                # 获取股票历史数据
                stock_history = self.stock_data_service.get_stock_history(
                    symbol=symbol,
                    start_date=request.start_date,
                    end_date=request.end_date
                )
                
                # 获取股票基本信息
                stock_basic = self.stock_data_service.get_stock_basic(symbol=symbol)
                
                # 应用筛选规则
                if self._match_rules(stock_history, request.rules):
                    matched_stocks.append({
                        "symbol": symbol,
                        "name": stock_basic["name"],
                        "industry": stock_basic["industry"],
                        "market": stock_basic["market"]
                    })
            except Exception as e:
                print(f"处理股票 {symbol} 时出错: {e}")
                continue
        
        return {
            "total": len(matched_stocks),
            "stocks": matched_stocks,
            "request": request.dict()
        }
    
    def _match_rules(self, stock_history: Dict[str, Any], rules: List[Dict[str, Any]]) -> bool:
        """匹配筛选规则"""
        data = stock_history["data"]
        if not data:
            return False
        
        # 获取最新数据
        latest_data = data[-1]
        
        # 遍历所有规则
        for rule in rules:
            indicator = rule["indicator"]
            operator = rule["operator"]
            value = rule["value"]
            
            # 获取指标值
            if indicator == "close":
                indicator_value = latest_data["close"]
            elif indicator == "volume":
                indicator_value = latest_data["volume"]
            elif indicator == "turnover":
                indicator_value = latest_data["turnover"]
            elif indicator == "high":
                indicator_value = latest_data["high"]
            elif indicator == "low":
                indicator_value = latest_data["low"]
            elif indicator == "open":
                indicator_value = latest_data["open"]
            else:
                continue
            
            # 应用操作符
            if operator == ">":
                if not (indicator_value > value):
                    return False
            elif operator == "<":
                if not (indicator_value < value):
                    return False
            elif operator == ">=":
                if not (indicator_value >= value):
                    return False
            elif operator == "<=":
                if not (indicator_value <= value):
                    return False
            elif operator == "==":
                if not (indicator_value == value):
                    return False
        
        return True
    
    def ai_based_screening(self, request: AIScreeningRequest):
        """基于自然语言的AI股票筛选，使用通用分析思考框架"""
        # 1. 获取股票列表
        market = getattr(request, 'market', 'cn')
        exchange = getattr(request, 'exchange', None)
        symbols = request.symbols or self.stock_data_service.get_stock_symbols(market=market, exchange=exchange)
        
        # 2. 获取每只股票的历史数据和特征
        stocks_with_features = []
        for symbol in symbols[:30]:  # 限制处理30只股票，避免请求过多
            try:
                # 获取股票历史数据（包含特征）
                stock_history = self.stock_data_service.get_stock_history(
                    symbol=symbol,
                    start_date=request.start_date,
                    end_date=request.end_date
                )
                
                # 获取股票基本信息
                stock_basic = self.stock_data_service.get_stock_basic(symbol=symbol)
                
                # 构建包含特征的股票数据
                stock_with_features = {
                    "symbol": symbol,
                    "name": stock_basic["name"],
                    "industry": stock_basic["industry"],
                    "market": stock_basic["market"],
                    "features": stock_history["features"],
                    "history_data": stock_history["data"]
                }
                
                stocks_with_features.append(stock_with_features)
            except Exception as e:
                print(f"处理股票 {symbol} 时出错: {e}")
                continue
        
        # 获取AI配置
        ai_config = getattr(request, 'ai_config', None)
        
        # 3. 使用AI批量分析股票，传递AI配置
        ai_analysis_results = self.ai_analysis_service.analyze_stocks_batch(
            stocks_data=stocks_with_features,
            user_conditions=request.query,
            ai_config=ai_config
        )
        
        # 4. 整合结果
        matched_stocks = []
        for stock_data, analysis_result in zip(stocks_with_features, ai_analysis_results):
            if analysis_result["meets_conditions"]:
                matched_stocks.append({
                    "symbol": stock_data["symbol"],
                    "name": stock_data["name"],
                    "industry": stock_data["industry"],
                    "market": stock_data["market"],
                    "analysis": analysis_result["analysis_reason"],
                    "risk_warning": analysis_result["risk_warning"]
                })
        
        # 5. AI解释筛选结果，传递AI配置
        explanation = self.ai_analysis_service.explain_screening_result(
            {
                "total": len(matched_stocks),
                "stocks": matched_stocks,
                "request": request.dict()
            },
            request.query
        )
        
        return {
            "total": len(matched_stocks),
            "stocks": matched_stocks,
            "query": request.query,
            "explanation": explanation,
            "analysis_results": ai_analysis_results
        }
