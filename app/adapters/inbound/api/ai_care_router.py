from fastapi import APIRouter, Depends, HTTPException
from app.adapters.inbound.api.schemas.ai_care import (
    AIAnswer,
    AIQuestion,
    AIStateResponse,
    ChatReply,
    ChatRequest,
    FAQItem,
)
from app.application.ai_care_service import AICareService
from app.dependencies import get_ai_care_service
from app.domain.ports.ai_provider import ChatMessage

router = APIRouter(prefix="/ai-care", tags=["ai-care"])


@router.get("/state", response_model=AIStateResponse)
async def state(service: AICareService = Depends(get_ai_care_service)) -> AIStateResponse:
    return AIStateResponse(ai_enabled=service.is_enabled())


@router.get("/faq", response_model=list[FAQItem])
async def faq(service: AICareService = Depends(get_ai_care_service)) -> list[FAQItem]:
    return [FAQItem(**item) for item in service.list_faq()]


@router.post("/ask", response_model=AIAnswer)
async def ask(
    body: AIQuestion, service: AICareService = Depends(get_ai_care_service)
) -> AIAnswer:
    if not service.is_enabled():
        raise HTTPException(status_code=503, detail="AI not configured")
    try:
        return AIAnswer(answer=await service.ask_question(body.question))
    except (ValueError, RuntimeError) as error:
        raise HTTPException(status_code=502, detail=str(error)) from error


@router.post("/chat", response_model=ChatReply)
async def chat(
    body: ChatRequest, service: AICareService = Depends(get_ai_care_service)
) -> ChatReply:
    if not service.is_enabled():
        raise HTTPException(status_code=503, detail="AI not configured")
    try:
        messages = [ChatMessage(role=m.role, content=m.content) for m in body.messages]
        reply = await service.chat(messages)
        return ChatReply(reply=reply)
    except (ValueError, RuntimeError) as error:
        raise HTTPException(status_code=502, detail=str(error)) from error
