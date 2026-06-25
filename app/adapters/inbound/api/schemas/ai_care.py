from pydantic import BaseModel, Field


class AIQuestion(BaseModel):
    question: str = Field(min_length=3, max_length=1000)


class AIAnswer(BaseModel):
    answer: str


class FAQItem(BaseModel):
    question: str
    answer: str


class ChatMessageSchema(BaseModel):
    role: str = Field(pattern=r"^(user|assistant)$")
    content: str = Field(min_length=1, max_length=2000)


class ChatRequest(BaseModel):
    messages: list[ChatMessageSchema] = Field(min_length=1)


class ChatReply(BaseModel):
    reply: str


class AIStateResponse(BaseModel):
    ai_enabled: bool
