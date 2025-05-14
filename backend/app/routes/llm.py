from fastapi import APIRouter
from app.models.llm_request import LLMRequest

router = APIRouter()

@router.post("/")
async def generate_text(request: LLMRequest):
    # 예시 응답 (실제 모델 호출로 대체 가능)
    return {"result": f"LLM 응답: {request.prompt}"}
