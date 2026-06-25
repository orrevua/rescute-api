from collections.abc import Sequence

from app.domain.ports.ai_provider import AIProvider, ChatMessage

_SYSTEM_PROMPT = (
    "You are a basic cat care assistant called Rescute AI. "
    "Reply in English, in a warm and concise manner. "
    "Only answer questions about cat care, health, and well-being. "
    "For urgent symptoms, recommend a veterinarian. "
    "Politely decline questions outside the topic of feline care."
)

_FAQ: list[dict[str, str]] = [
    {
        "question": "When should I take my cat to the vet?",
        "answer": "Seek immediate care if there is difficulty breathing, severe lethargy, pain, persistent vomiting, or absence of urination.",
    },
    {
        "question": "How often should I offer water?",
        "answer": "Fresh water should be available at all times, in more than one spot around the house.",
    },
    {
        "question": "Do cats need environmental enrichment?",
        "answer": "Yes. Scratching posts, elevated spots, and daily play reduce stress and promote well-being.",
    },
]


class AICareService:
    def __init__(self, provider: AIProvider) -> None:
        self._provider = provider

    def is_enabled(self) -> bool:
        return self._provider.is_configured()

    async def ask_question(self, question: str) -> str:
        return await self._provider.generate_response(question)

    async def chat(self, messages: Sequence[ChatMessage]) -> str:
        return await self._provider.reply(_SYSTEM_PROMPT, messages)

    def list_faq(self) -> list[dict[str, str]]:
        return _FAQ
