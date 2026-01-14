from fastapi import APIRouter, HTTPException, Query
import logging
from app.services.ai_analysis_service import AIAnalysisService
from app.schemas.ai import AIAnalysisRequest, AIAnalysisResponse
from app.services.stock_data_service import StockDataService

# 配置日志记录
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

router = APIRouter()
ai_service = AIAnalysisService()
stock_data_service = StockDataService()

@router.post("/analyze")
def analyze_stock(
    request: AIAnalysisRequest = ...
):
    """AI分析股票数据"""
    try:
        logger.info(f"收到请求: {request}")
        # 步骤1: 验证请求参数
        if not request.symbol:
            raise HTTPException(status_code=400, detail="股票代码不能为空")
        logger.info("步骤1: 请求参数验证通过")
        
        # 步骤2: 检查和更新AI配置
        has_ai_config = hasattr(request, 'ai_config') and request.ai_config
        if has_ai_config:
            try:
                ai_service.update_ai_config(request.ai_config)
                logger.info("步骤2: AI配置更新成功")
            except Exception as e:
                logger.error(f"步骤2: AI配置更新失败: {e}")
                raise HTTPException(status_code=400, detail=f"AI配置更新失败: {str(e)}")
        
        # 验证AI配置是否完整
        current_ai_config = request.ai_config if has_ai_config else ai_service.ai_config
        
        # 验证API密钥
        if not current_ai_config.get('api_key') or current_ai_config.get('api_key').strip() == '':
            raise HTTPException(status_code=400, detail="错误：AI配置不完整 - API密钥为空\n\n请在前端设置中配置有效的API密钥\n- OpenAI: 从 https://platform.openai.com/api-keys 获取\n- 智谱: 从 https://open.bigmodel.cn/apikeys 获取")
        
        # 验证API基础地址
        if not current_ai_config.get('base_url') or current_ai_config.get('base_url').strip() == '':
            raise HTTPException(status_code=400, detail="错误：AI配置不完整 - API基础地址为空\n\n请在前端设置中配置有效的API基础地址\n- OpenAI: https://api.openai.com/v1\n- 智谱: https://open.bigmodel.cn/api/paas/v4")
        
        # 验证AI模型名称
        if not current_ai_config.get('model_name') or current_ai_config.get('model_name').strip() == '':
            raise HTTPException(status_code=400, detail="错误：AI配置不完整 - AI模型名称为空\n\n请在前端设置中配置有效的AI模型名称\n- OpenAI推荐: gpt-3.5-turbo, gpt-4\n- 智谱推荐: glm-4-flash")
        
        logger.info("步骤2: AI配置验证通过")
        
        # 步骤3: 获取或使用历史数据
        if hasattr(request, 'history_data') and request.history_data:
            history_data = request.history_data
            # 如果前端直接传入历史数据，后端尽量保持向下兼容，features 暂为空
            features = {}
            logger.info(f"步骤3: 使用前端传入的历史数据，共{len(history_data)}条")
        else:
            # 获取股票历史数据
            try:
                logger.info("步骤3: 开始获取股票历史数据")
                stock_history = stock_data_service.get_stock_history(
                    symbol=request.symbol,
                    start_date=request.start_date,
                    end_date=request.end_date
                )
                logger.info(f"步骤3: 股票历史数据获取成功，共{len(stock_history.get('data', []))}条")
            except ValueError as e:
                # 处理股票数据不存在的情况
                logger.error(f"步骤3: 股票数据不存在: {e}")
                raise HTTPException(status_code=404, detail=f"获取股票数据失败: {str(e)}")
            except Exception as e:
                # 处理其他股票数据获取错误
                logger.error(f"步骤3: 获取股票数据失败: {e}")
                raise HTTPException(status_code=500, detail=f"获取股票数据失败: {str(e)}")

            # 获取股票特征
            features = stock_history.get("features", {})
            history_data = stock_history.get("data", [])
        
        # 步骤4: AI分析股票
        try:
            logger.info("步骤4: 开始AI分析股票")
            # 使用新的策略化分析方法
            strategy = request.strategy.model_dump() if request.strategy else {}
            result = ai_service.analyze_stock_with_strategy(
                symbol=request.symbol,
                features=features,
                history_data=history_data,
                strategy=strategy,
                ai_config=request.ai_config if has_ai_config else None
            )
            logger.info("步骤4: AI分析完成")
        except Exception as e:
            logger.error(f"步骤4: AI分析失败: {e}")
            # 添加更详细的错误处理，返回具体的错误原因
            error_message = str(e)
            if "AuthenticationError" in error_message or "401" in error_message:
                error_message = "AI模型连接失败: API密钥无效或已过期，请检查您的API密钥设置"
            elif "ConnectionError" in error_message or "无法连接" in error_message:
                error_message = "AI模型连接失败: 无法连接到AI服务，请检查您的网络连接或API基础地址设置"
            elif "Timeout" in error_message or "请求超时" in error_message:
                error_message = "AI模型连接失败: 请求超时，请检查您的网络连接或稍后重试"
            elif "APITimeoutError" in error_message:
                error_message = "AI模型连接失败: API请求超时，请检查您的网络连接或稍后重试"
            elif "RateLimitError" in error_message or "429" in error_message:
                error_message = "AI模型连接失败: API请求频率过高，请稍后重试"
            else:
                error_message = f"AI分析失败: {error_message}"
            raise HTTPException(status_code=500, detail=error_message)
        
        logger.info(f"返回结果: {result}")
        return result
    except HTTPException:
        # 已经是HTTP异常，直接重新抛出
        raise
    except Exception as e:
        logger.error(f"未预期的错误: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"未预期的错误: {str(e)}")

@router.post("/explain")
def explain_screening(
    screening_result: dict = ...,
    query: str = Query(..., description="用户查询的自然语言描述"),
    ai_config: str = Query(None, description="AI模型配置JSON字符串")
):
    """AI解释筛选结果"""
    try:
        # 验证输入参数
        if not screening_result:
            raise HTTPException(status_code=400, detail="筛选结果不能为空")
        if not query:
            raise HTTPException(status_code=400, detail="查询描述不能为空")
        
        # 检查请求中是否包含AI配置
        if ai_config:
            try:
                import json
                parsed_config = json.loads(ai_config)
                ai_service.update_ai_config(parsed_config)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="AI配置JSON格式无效")
        
        explanation = ai_service.explain_screening_result(screening_result, query)
        return {"explanation": explanation}
    except HTTPException:
        # 已经是HTTP异常，直接重新抛出
        raise
    except Exception as e:
        logger.error(f"错误: {e}")
        import traceback
        traceback.print_exc()
        
        # 添加更详细的错误处理，返回具体的错误原因
        error_message = str(e)
        if "AuthenticationError" in error_message or "401" in error_message:
            error_message = "AI模型连接失败: API密钥无效或已过期，请检查您的API密钥设置"
        elif "ConnectionError" in error_message or "无法连接" in error_message:
            error_message = "AI模型连接失败: 无法连接到AI服务，请检查您的网络连接或API基础地址设置"
        elif "Timeout" in error_message or "请求超时" in error_message:
            error_message = "AI模型连接失败: 请求超时，请检查您的网络连接或稍后重试"
        elif "APITimeoutError" in error_message:
            error_message = "AI模型连接失败: API请求超时，请检查您的网络连接或稍后重试"
        elif "RateLimitError" in error_message or "429" in error_message:
            error_message = "AI模型连接失败: API请求频率过高，请稍后重试"
        else:
            error_message = f"AI解释失败: {error_message}"
        
        raise HTTPException(status_code=500, detail=error_message)

@router.post("/test-connection")
def test_ai_connection(
    ai_config: dict = None
):
    """测试AI模型连接"""
    try:
        # 测试连接，直接传递AI配置
        result = ai_service.test_ai_connection(ai_config)
        return result
    except Exception as e:
        logger.error(f"错误: {e}")
        import traceback
        traceback.print_exc()
        
        # 添加更详细的错误处理，返回具体的错误原因
        error_message = str(e)
        if "AuthenticationError" in error_message or "401" in error_message:
            error_message = "API密钥无效或已过期，请检查您的API密钥设置"
        elif "ConnectionError" in error_message or "无法连接" in error_message:
            error_message = "无法连接到AI服务，请检查您的网络连接或API基础地址设置"
        elif "Timeout" in error_message or "请求超时" in error_message:
            error_message = "请求超时，请检查您的网络连接或稍后重试"
        elif "APITimeoutError" in error_message:
            error_message = "API请求超时，请检查您的网络连接或稍后重试"
        elif "RateLimitError" in error_message or "429" in error_message:
            error_message = "API请求频率过高，请稍后重试"
        else:
            error_message = f"连接测试失败: {error_message}"
        
        return {"success": False, "message": error_message}
