from fastapi import APIRouter, HTTPException, Query
from app.services.stock_data_service import StockDataService
from app.schemas.stock import StockHistoryResponse, StockBasicResponse

router = APIRouter()
stock_service = StockDataService()

@router.get("/history", response_model=StockHistoryResponse)
def get_stock_history(
    symbol: str = Query(..., description="股票代码，如：sh600000"),
    start_date: str = Query(None, description="开始日期，格式：YYYY-MM-DD"),
    end_date: str = Query(None, description="结束日期，格式：YYYY-MM-DD"),
    adjust: str = Query("qfq", description="复权类型：qfq（前复权）、hfq（后复权）、None（不复权）")
):
    """获取股票历史K线数据"""
    try:
        data = stock_service.get_stock_history(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            adjust=adjust
        )
        return data
    except ValueError as e:
        # 处理股票数据不存在的情况，返回404状态码
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        # 处理其他异常，返回500状态码
        raise HTTPException(status_code=500, detail=f"获取股票数据失败: {str(e)}")

@router.get("/basic", response_model=StockBasicResponse)
def get_stock_basic(
    symbol: str = Query(..., description="股票代码，如：sh600000")
):
    """获取股票基本信息"""
    try:
        data = stock_service.get_stock_basic(symbol=symbol)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/symbols")
def get_stock_symbols(
    market: str = Query("cn", description="市场类型：cn（A股）、hk（港股）、us（美股）")
):
    """获取股票代码列表"""
    try:
        symbols = stock_service.get_stock_symbols(market=market)
        return {"symbols": symbols}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
