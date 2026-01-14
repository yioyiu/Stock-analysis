from fastapi import APIRouter
from app.api.endpoints import stock_data, ai_analysis

router = APIRouter()

# 注册路由
router.include_router(stock_data.router, prefix="/stock", tags=["stock"])
router.include_router(ai_analysis.router, prefix="/ai", tags=["ai"])
