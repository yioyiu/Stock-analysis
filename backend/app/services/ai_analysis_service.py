from typing import List, Dict, Any
import json
import os
import logging
from langchain_openai import ChatOpenAI
from app.core.config import settings

# 配置日志记录
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AIAnalysisService:
    def __init__(self, ai_config=None):
        # 使用传入的配置或默认配置
        self.ai_config = ai_config or {
            "api_key": settings.OPENAI_API_KEY,
            "base_url": settings.OPENAI_API_BASE,
            "model_name": settings.AI_MODEL_NAME,
            "temperature": 0.1
        }
        
        # 初始化LLM，添加超时设置
        self.llm = ChatOpenAI(
            api_key=self.ai_config["api_key"],
            base_url=self.ai_config["base_url"],
            model_name=self.ai_config["model_name"],
            temperature=self.ai_config["temperature"],
            timeout=60  # 增加到60秒超时
        )
        
        # 加载风险偏好配置
        self.risk_profiles = self._load_risk_profiles()
    
    def _load_risk_profiles(self) -> Dict[str, Dict[str, str]]:
        """加载风险偏好配置文件"""
        profiles = {}
        risk_profiles_dir = os.path.join(os.path.dirname(__file__), "risk_profiles")
        
        # 确保目录存在
        if not os.path.exists(risk_profiles_dir):
            os.makedirs(risk_profiles_dir)
            # 添加默认风险偏好配置
            default_profiles = {
                "low_risk": {
                    "name": "低风险",
                    "description": "你是一个保守型交易员，优先考虑资金安全性。你只在有高度确定性的情况下才会入场，严格控制仓位，设置严格的止损点位。你关注长期趋势，对短期波动不敏感，更看重基本面分析。你倾向于选择低波动率的股票，避免追高杀跌。你的目标是稳定的小幅收益，而不是高风险高回报。"
                },
                "medium_risk": {
                    "name": "中风险",
                    "description": "你是一个平衡型交易员，兼顾收益和风险。你会在确定性和机会之间寻找平衡，合理控制仓位，设置适度的止损点位。你同时关注短期和长期趋势，结合技术面和基本面分析。你倾向于选择中等波动率的股票，既不会错过机会，也不会承担过高风险。你的目标是稳定的中等收益，在风险可控的前提下追求合理回报。"
                },
                "high_risk": {
                    "name": "高风险",
                    "description": "你是一个激进型交易员，追求高收益，容忍高风险。你敢于在不确定性中寻找机会，仓位管理较为激进，止损点位设置较宽松。你更关注短期趋势，善于捕捉市场热点和短期波动。你倾向于选择高波动率的股票，愿意追高杀跌。你的目标是获取高额收益，愿意承担相应的高风险。"
                }
            }
            # 保存默认配置到文件
            for name, profile in default_profiles.items():
                profile_path = os.path.join(risk_profiles_dir, f"{name}.json")
                with open(profile_path, "w", encoding="utf-8") as f:
                    json.dump(profile, f, ensure_ascii=False, indent=2)
            return default_profiles
        
        # 加载所有风险偏好文件
        for profile_file in os.listdir(risk_profiles_dir):
            if profile_file.endswith(".json"):
                profile_path = os.path.join(risk_profiles_dir, profile_file)
                with open(profile_path, "r", encoding="utf-8") as f:
                    profile = json.load(f)
                    profile_name = profile_file.replace(".json", "")
                    profiles[profile_name] = profile
        
        # 如果没有加载到任何配置，使用默认配置
        if not profiles:
            profiles = {
                "low_risk": {
                    "name": "低风险",
                    "description": "你是一个保守型交易员，优先考虑资金安全性。"
                },
                "medium_risk": {
                    "name": "中风险",
                    "description": "你是一个平衡型交易员，兼顾收益和风险。"
                },
                "high_risk": {
                    "name": "高风险",
                    "description": "你是一个激进型交易员，追求高收益，容忍高风险。"
                }
            }
        
        return profiles
    
    def update_ai_config(self, ai_config):
        """更新AI配置"""
        self.ai_config = {
            **self.ai_config,
            **ai_config
        }
        
        # 验证API配置的完整性
        missing_fields = []
        if not self.ai_config["api_key"] or self.ai_config["api_key"].strip() == "":
            missing_fields.append("API密钥")
        if not self.ai_config["base_url"] or self.ai_config["base_url"].strip() == "":
            missing_fields.append("API基础地址")
        if not self.ai_config["model_name"] or self.ai_config["model_name"].strip() == "":
            missing_fields.append("模型名称")
        
        if missing_fields:
            logger.warning(f"AI配置中缺少必要字段: {', '.join(missing_fields)}，这可能导致API调用失败")
        else:
            logger.info(f"AI配置更新成功: 模型={self.ai_config['model_name']}, 基础地址={self.ai_config['base_url']}")
        
        # 重新初始化LLM，添加超时设置
        try:
            self.llm = ChatOpenAI(
                api_key=self.ai_config["api_key"],
                base_url=self.ai_config["base_url"],
                model_name=self.ai_config["model_name"],
                temperature=self.ai_config["temperature"],
                timeout=60  # 增加到60秒超时
            )
            logger.info("LLM初始化成功")
        except Exception as e:
            logger.error(f"LLM初始化失败: {e}")
            import traceback
            traceback.print_exc()
    
    def convert_natural_language_to_rules(self, query: str) -> List[Dict[str, Any]]:
        """将自然语言转换为筛选规则"""
        # 构建提示模板
        prompt_template = """你是一个股票筛选规则转换器，请将用户的自然语言描述转换为结构化的筛选规则。

用户查询: {query}

请按照以下JSON格式输出筛选规则，不要添加任何其他解释：
[
    {
        "indicator": "close|volume|turnover|high|low|open",
        "operator": ">|<|>=|<=|",
        "value": 数值
    }
]

例如：
用户查询：找出收盘价大于100元，成交量大于1000万的股票
输出：
[
    {"indicator": "close", "operator": ">", "value": 100},
    {"indicator": "volume", "operator": ">", "value": 10000000}
]

如果无法理解用户查询，请输出空数组。"""
        
        # 执行LLM调用 - 使用invoke替代predict，添加异常处理
        try:
            result = self.llm.invoke(prompt_template.format(query=query))
            
            # 解析结果
            try:
                rules = json.loads(result.content)
                return rules
            except json.JSONDecodeError:
                logger.error(f"JSON解析失败，原始内容: {result.content}")
                return []
        except Exception as llm_error:
            logger.error(f"LLM调用错误: {llm_error}")
            import traceback
            traceback.print_exc()
            return []
    
    def explain_screening_result(self, screening_result: Dict[str, Any], query: str) -> str:
        """AI解释筛选结果"""
        # 构建提示模板
        prompt_template = """你是一个专业的股票分析师，请基于用户的查询和筛选结果，生成一份专业的分析报告。

用户查询: {query}

筛选结果: {result}

请按照以下结构输出分析报告：
1. 筛选条件解析：解释用户的查询和转换后的筛选规则
2. 筛选结果概览：说明筛选出的股票数量和整体情况
3. 股票分析：对每只股票进行简要分析（如果数量较多，可以只分析前3只）
4. 投资建议：基于筛选结果给出专业的投资建议

请使用专业、客观的语言，避免夸大其词。"""
        
        # 执行LLM调用 - 使用invoke替代predict，添加异常处理
        try:
            result = self.llm.invoke(
                prompt_template.format(
                    query=query,
                    result=str(screening_result)
                )
            )
            
            return result.content
        except Exception as llm_error:
            logger.error(f"LLM调用错误: {llm_error}")
            import traceback
            traceback.print_exc()
            return f"AI模型调用失败: {str(llm_error)}. 无法获取完整分析结果。"
    
    def analyze_stock(self, symbol: str, features: Dict[str, Any], history_data: List[Dict[str, Any]], user_conditions: str, ai_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """AI分析单只股票，基于特征和历史数据"""
        # 获取最近10天的历史数据，避免数据量过大
        recent_history = history_data[-10:] if len(history_data) > 10 else history_data
        
        # 使用传入的AI配置或默认配置
        current_ai_config = ai_config or self.ai_config
        
        # 创建临时LLM实例，避免影响全局配置
        temp_llm = ChatOpenAI(
            api_key=current_ai_config["api_key"],
            base_url=current_ai_config["base_url"],
            model_name=current_ai_config["model_name"],
            temperature=current_ai_config["temperature"],
            timeout=60  # 增加到60秒超时
        )
        
        # 构建提示模板
        prompt_template = """你是一个专业的股票分析师，请基于以下股票特征、历史数据和用户条件，分析该股票是否符合条件，并给出详细分析。

股票代码: {symbol}

股票特征:
{features}

最近{days}天的历史数据:
{history_data}

用户条件: {user_conditions}

请按照以下JSON格式输出分析结果，不要添加任何其他解释：
{
  "stock": "股票代码",
  "meets_conditions": true/false,
  "analysis_reason": "详细分析理由，包括对价格、成交量、换手率及K线形态在一段时间内的变化分析，资金筹码变化趋势，主力或散户行为模式演变",
  "risk_warning": "风险提示"
}

要求：
1. 根据一段时间内的价格、成交量、换手率及K线形态分析资金筹码变化趋势
2. 推理潜在主力或散户行为模式在这段时间内的演变
3. 分析价格和成交量的联动关系，识别资金流入流出情况
4. 严格根据条件判断股票是否符合要求
5. 输出结构化JSON，不要添加其他内容
"""
        
        # 执行LLM调用 - 使用invoke替代predict，添加异常处理
        try:
            result = temp_llm.invoke(
                prompt_template.format(
                    symbol=symbol,
                    features=str(features),
                    days=len(recent_history),
                    history_data=str(recent_history),
                    user_conditions=user_conditions
                )
            )
            
            # 解析结果
            try:
                analysis_result = json.loads(result.content)
                return analysis_result
            except json.JSONDecodeError:
                logger.error(f"JSON解析失败，原始内容: {result.content}")
                return {
                    "stock": symbol,
                    "meets_conditions": False,
                    "analysis_reason": "AI分析结果解析失败",
                    "risk_warning": "无法获取有效分析结果"
                }
        except Exception as llm_error:
            logger.error(f"LLM调用错误: {llm_error}")
            import traceback
            traceback.print_exc()
            return {
                "stock": symbol,
                "meets_conditions": False,
                "analysis_reason": f"AI模型调用失败: {str(llm_error)}. 无法获取完整分析结果。",
                "risk_warning": "无法获取有效分析结果"
            }
    
    def analyze_stock_with_strategy(self, symbol: str, features: Dict[str, Any], history_data: List[Dict[str, Any]], strategy: Dict[str, Any], ai_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """AI分析单只股票，基于策略化趋势判断"""
        # 获取最近30天的历史数据，用于趋势分析
        recent_history = history_data[-30:] if len(history_data) > 30 else history_data
        
        # 获取风险偏好描述
        risk_preference = strategy.get("risk_preference", "medium")
        # 确保risk_preference是有效的值
        if risk_preference not in ["low", "medium", "high"]:
            risk_preference = "medium"
        risk_profile_key = f"{risk_preference}_risk"
        risk_profile = self.risk_profiles.get(risk_profile_key, {
            "description": "你是一个平衡型交易员，兼顾收益和风险。"
        })
        
        # 获取其他策略参数
        trend_sensitivity = strategy.get("trend_sensitivity", "medium")
        bias = strategy.get("bias", "neutral")
        
        # 构建趋势敏感度描述
        trend_sensitivity_desc = {
            "low": "你对短期波动不敏感，更关注长期趋势。",
            "medium": "你平衡考虑短期和长期趋势。",
            "high": "你对短期波动敏感，快速响应市场变化。"
        }.get(trend_sensitivity, "你平衡考虑短期和长期趋势。")
        
        # 构建多空偏好描述
        bias_desc = {
            "neutral": "你客观分析市场，不偏向多头或空头。",
            "long": "你倾向于寻找上涨机会，偏好多头策略。",
            "short": "你倾向于寻找下跌机会，偏好空头策略。"
        }.get(bias, "你客观分析市场，不偏向多头或空头。")
        
        # 构建提示模板
        prompt_template = """{risk_profile_desc}
{trend_sensitivity_desc}
{bias_desc}

基于以下股票特征、历史数据和交易策略配置，分析该股票并提供策略化判断：

股票代码: {symbol}

股票特征:
{features}

最近{days}天的历史数据:
{history_data}

交易策略配置:
- 风险偏好: {risk_preference}
- 趋势敏感度: {trend_sensitivity}
- 多空偏好: {bias}

请按照以下JSON格式输出分析结果，不要添加任何其他解释：
{{
  "symbol": "股票代码",
  "action": "买入|卖出|持有",
  "trend": "多头|空头|震荡",
  "logic": "详细的分析逻辑，包括价格、成交量、换手率、成交量与换手率乘积及K线形态的综合分析，以及你做出该操作决策的具体原因",
  "confidence": 0.0-1.0,
  "expected_return": 0.0-1.0,
  "will_trade": true|false,
  "support_level": "近期支撑区间，例如：10-12元",
  "resistance_level": "近期压力区间，例如：15-17元",
  "historical_similar_patterns": [
    {{
      "pattern_date": "YYYY-MM-DD",
      "kline_segment": "描述该历史时期的K线形态和特征",
      "result": "上涨|下跌|震荡",
      "return": 0.0-1.0,
      "similarity": 0.0-1.0
    }}
  ],
  "detailed_analysis": {{
    "price_analysis": "价格走势分析",
    "volume_analysis": "成交量分析",
    "turnover_analysis": "换手率分析",
    "volume_turnover_analysis": "成交量与换手率乘积分析",
    "kline_pattern_analysis": "K线形态分析",
    "support_resistance_analysis": "支撑压力区间分析"
  }}
}}

要求：
1. 严格按照你的交易员性格和策略配置做出决策
2. 明确说明你会采取的操作（买入、卖出或持有）
3. 提供至少3个历史相似走势案例，包括K线片段描述和涨跌结果
4. 置信度范围为0-1，反映分析的可靠程度
5. 预期收益率范围为0-1，反映预期的涨跌幅度
6. will_trade字段表示是否会进行交易（true/false）
7. 输出结构化JSON，不要添加其他内容
8. 相似历史走势的return字段表示该片段的涨跌幅（正数为上涨，负数为下跌）
9. 在计算支撑区间与压力区间时，必须将成交量与换手率的乘积（volume_turnover_product）作为重要参考因素纳入分析模型中，成交量与换手率乘积高的价格区间应给予更高权重
10. 详细分析成交量与换手率乘积对支撑位和压力位的影响，说明其在支撑压力区间形成过程中的作用
"""
        
        # 使用传入的AI配置或默认配置
        current_ai_config = ai_config or self.ai_config
        
        # 重用现有LLM实例，只有当配置变化时才创建新实例
        llm_to_use = self.llm
        if ai_config:
            # 只有当传入的配置与当前配置不同时，才创建新的LLM实例
            if (current_ai_config["api_key"] != self.ai_config["api_key"] or
                current_ai_config["base_url"] != self.ai_config["base_url"] or
                current_ai_config["model_name"] != self.ai_config["model_name"] or
                current_ai_config["temperature"] != self.ai_config["temperature"]):
                logger.info("创建临时LLM实例")
                llm_to_use = ChatOpenAI(
                    api_key=current_ai_config["api_key"],
                    base_url=current_ai_config["base_url"],
                    model_name=current_ai_config["model_name"],
                    temperature=current_ai_config["temperature"],
                    timeout=60  # 增加到60秒超时
                )
            else:
                logger.info("重用现有LLM实例")
                llm_to_use = self.llm
        
        # 执行LLM调用，添加异常处理
        try:
            logger.info(f"开始调用AI模型: {current_ai_config['model_name']}")
            logger.info(f"API基础地址: {current_ai_config['base_url']}")
            
            result = llm_to_use.invoke(
                prompt_template.format(
                    risk_profile_desc=risk_profile["description"],
                    trend_sensitivity_desc=trend_sensitivity_desc,
                    bias_desc=bias_desc,
                    symbol=symbol,
                    features=str(features),
                    days=len(recent_history),
                    history_data=str(recent_history),
                    risk_preference=risk_preference,
                    trend_sensitivity=trend_sensitivity,
                    bias=bias
                )
            )
            
            logger.info("AI模型调用成功")
        except Exception as llm_error:
            # 捕获LLM调用中的所有异常
            logger.error(f"LLM调用错误: {llm_error}")
            import traceback
            traceback.print_exc()
            
            # 检查错误类型，返回更详细的错误信息
            error_message = str(llm_error)
            error_detail = ""
            
            # 网络连接错误
            if any(keyword in error_message.lower() for keyword in ["network", "timeout", "connection", "connect", "socket", "dns", "refused"]):
                error_detail = f"网络连接问题: {str(llm_error)}\n\n请检查：\n1. 您的网络连接是否正常\n2. API基础地址是否正确（当前: {current_ai_config['base_url']}）\n3. 是否需要配置代理服务器\n4. 防火墙是否允许访问该地址"
            # API密钥错误
            elif any(keyword in error_message.lower() for keyword in ["401", "unauthorized", "invalid api key", "api key", "authentication"]):
                error_detail = f"API密钥无效或已过期\n\n请检查：\n1. 您的API密钥是否正确配置\n2. 密钥是否已过期\n3. 密钥是否有足够的权限\n\n获取API密钥：\n- OpenAI: https://platform.openai.com/api-keys\n- 智谱: https://open.bigmodel.cn/apikeys"
            # 模型不存在错误
            elif any(keyword in error_message.lower() for keyword in ["404", "not found", "model does not exist", "invalid model"]):
                error_detail = f"模型不存在: {current_ai_config['model_name']}\n\n请检查您配置的模型名称是否正确，推荐模型：\n- OpenAI: gpt-3.5-turbo, gpt-4\n- 智谱: glm-4-flash, glm-4"
            # 速率限制错误
            elif any(keyword in error_message.lower() for keyword in ["429", "rate limit", "too many requests"]):
                error_detail = f"AI模型调用频率过高\n\n请：\n1. 稍后重试\n2. 减少请求频率\n3. 联系服务提供商增加配额\n4. 使用更高层级的API密钥"
            # 服务器错误
            elif any(keyword in error_message.lower() for keyword in ["500", "server error", "internal error"]):
                error_detail = f"AI服务端内部错误\n\n请：\n1. 稍后重试\n2. 检查服务提供商的状态页面\n3. 联系服务提供商获取支持"
            # 模型访问被拒绝
            elif any(keyword in error_message.lower() for keyword in ["403", "forbidden", "access denied"]):
                error_detail = f"模型访问被拒绝\n\n请检查：\n1. 您的API密钥是否有权限访问该模型\n2. 模型是否处于可用状态\n3. 地区限制：您的IP是否被允许访问"
            # 上下文长度超过限制
            elif any(keyword in error_message.lower() for keyword in ["context length", "token limit", "max tokens", "context window"]):
                error_detail = f"上下文长度超过限制\n\n请：\n1. 减少请求中的历史数据量\n2. 使用支持更长上下文的模型\n3. 优化提示词，减少不必要的内容"
            # 其他错误
            else:
                error_detail = f"AI模型调用失败: {str(llm_error)}\n\n请检查：\n1. AI配置是否正确\n2. 网络连接是否正常\n3. 稍后重试\n\n详细错误信息：{str(llm_error)}"
            
            # 返回包含详细错误信息的结果
            return {
                "symbol": symbol,
                "action": "持有",
                "trend": "震荡",
                "logic": error_detail,
                "confidence": 0.0,
                "expected_return": 0.0,
                "will_trade": False,
                "support_level": "",
                "resistance_level": "",
                "historical_similar_patterns": [],
                "detailed_analysis": {}
            }
        
        # 解析结果
        try:
            # 尝试直接解析
            analysis_result = json.loads(result.content)
            return analysis_result
        except json.JSONDecodeError:
            # 如果直接解析失败，尝试提取JSON部分
            content = result.content
            logger.error(f"原始AI输出: {content}")
            
            # 尝试提取JSON部分
            import re
            # 寻找完整的JSON对象，使用更可靠的正则表达式
            # 匹配从第一个 { 到最后一个 } 的内容
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                try:
                    analysis_result = json.loads(json_match.group())
                    return analysis_result
                except json.JSONDecodeError:
                    pass
            
            # 如果还是失败，尝试清理内容
            cleaned_content = content.strip()
            # 移除可能的代码块标记
            if cleaned_content.startswith('```json'):
                cleaned_content = cleaned_content[7:]
            if cleaned_content.endswith('```'):
                cleaned_content = cleaned_content[:-3]
            cleaned_content = cleaned_content.strip()
            
            try:
                analysis_result = json.loads(cleaned_content)
                # 确保返回结果包含所有必要字段
                if "expected_return" not in analysis_result:
                    analysis_result["expected_return"] = 0.0
                if "will_trade" not in analysis_result:
                    analysis_result["will_trade"] = False
                return analysis_result
            except json.JSONDecodeError:
                # 如果所有尝试都失败，返回默认结果
                logger.error(f"JSON解析失败，原始内容: {content[:100]}...")
                return {
                    "symbol": symbol,
                    "action": "持有",
                    "trend": "震荡",
                    "logic": f"AI分析结果解析失败，原始输出: {content[:100]}...",
                    "confidence": 0.0,
                    "expected_return": 0.0,
                    "will_trade": False,
                    "support_level": "",
                    "resistance_level": "",
                    "historical_similar_patterns": [],
                    "detailed_analysis": {
                        "price_analysis": "",
                        "volume_analysis": "",
                        "turnover_analysis": "",
                        "volume_turnover_analysis": "",
                        "kline_pattern_analysis": "",
                        "support_resistance_analysis": ""
                    }
                }
    
    def analyze_stocks_batch(self, stocks_data: List[Dict[str, Any]], user_conditions: str, ai_config: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """批量分析股票"""
        results = []
        for stock_data in stocks_data:
            symbol = stock_data["symbol"]
            features = stock_data["features"]
            history_data = stock_data["history_data"]
            analysis_result = self.analyze_stock(symbol, features, history_data, user_conditions, ai_config)
            results.append(analysis_result)
        return results
    
    def test_ai_connection(self, ai_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """测试AI模型连接"""
        # 使用传入的AI配置或默认配置
        current_ai_config = ai_config or self.ai_config
        
        # 创建临时LLM实例，避免影响全局配置
        temp_llm = ChatOpenAI(
            api_key=current_ai_config["api_key"],
            base_url=current_ai_config["base_url"],
            model_name=current_ai_config["model_name"],
            temperature=current_ai_config["temperature"],
            timeout=60  # 增加到60秒超时
        )
        
        try:
            # 发送一个简单的测试请求 - 使用invoke替代predict
            result = temp_llm.invoke("Hello, are you available?")
            response_content = result.content
            logger.info(f"AI模型连接测试成功: {response_content[:50]}...")
            return {
                "success": True,
                "message": "AI模型连接成功",
                "response": response_content[:50] + "..." if len(response_content) > 50 else response_content
            }
        except Exception as e:
            logger.error(f"AI模型连接测试失败: {str(e)}")
            return {
                "success": False,
                "message": f"AI模型连接失败: {str(e)}"
            }
