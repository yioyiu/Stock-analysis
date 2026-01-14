from fastapi import APIRouter, HTTPException, Body
from app.services.screening_service import ScreeningService
from app.schemas.screening import RuleScreeningRequest, RuleScreeningResponse, AIScreeningRequest, AIScreeningResponse

router = APIRouter()
screening_service = ScreeningService()

@router.post("/rule", response_model=RuleScreeningResponse)
def rule_screening(
    request: RuleScreeningRequest = Body(..., description="规则筛选请求")
):
    """基于规则的股票筛选"""
    try:
        result = screening_service.rule_based_screening(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ai", response_model=AIScreeningResponse)
def ai_screening(
    request: AIScreeningRequest = Body(..., description="AI筛选请求")
):
    """基于自然语言的AI股票筛选"""
    try:
        result = screening_service.ai_based_screening(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
