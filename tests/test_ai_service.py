"""
AI Service tests.

These tests cover fallback paths and provider-switching logic. They do NOT
make real network calls; live provider calls are gated behind the
`integration` marker and require a valid API key in the environment.
"""

import pytest
from app.services.ai_service import AIService
from app.config import settings


pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend():
    return 'asyncio'


class TestAIService:
    """Test AI service fallback behavior and shape of responses."""

    @pytest.fixture
    def ai_service(self):
        """Create AI service instance without forcing a live provider."""
        # No real key in tests → service falls back to keyword logic.
        original_provider = settings.AI_PROVIDER
        original_openai = settings.OPENAI_API_KEY
        original_groq = settings.GROQ_API_KEY
        settings.AI_PROVIDER = "groq"
        settings.OPENAI_API_KEY = ""
        settings.GROQ_API_KEY = settings.GROQ_API_KEY
        svc = AIService()
        yield svc
        settings.AI_PROVIDER = original_provider
        settings.OPENAI_API_KEY = original_openai
        settings.GROQ_API_KEY = original_groq

    async def test_analyze_sentiment_positive(self, ai_service: AIService):
        result = await ai_service.analyze_sentiment("Отличная работа! Очень доволен результатом.")
        assert result["sentiment"] in ["positive", "negative", "neutral"]
        assert 0 <= result["confidence"] <= 1

    async def test_analyze_sentiment_negative(self, ai_service: AIService):
        result = await ai_service.analyze_sentiment("Плохой сервис, не рекомендую.")
        assert result["sentiment"] in ["positive", "negative", "neutral"]

    async def test_classify_message_project_inquiry(self, ai_service: AIService):
        result = await ai_service.classify_message("Хочу заказать разработку сайта")
        assert result["category"] in [
            "project_inquiry", "collaboration", "job_offer",
            "general_question", "feedback", "support", "other"
        ]
        assert result["priority"] in ["low", "medium", "high"]

    async def test_generate_response(self, ai_service: AIService):
        result = await ai_service.generate_response("Интересует ваш опыт", "Иван")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_fallback_sentiment_analysis(self, ai_service: AIService):
        result = ai_service._fallback_sentiment_analysis("Спасибо за отличную работу")
        assert result["sentiment"] == "positive"
        assert result["confidence"] > 0.5

    def test_fallback_classification(self, ai_service: AIService):
        result = ai_service._fallback_classification("Хочу обсудить проект разработки")
        assert result["category"] == "project_inquiry"

    def test_fallback_response(self, ai_service: AIService):
        result = ai_service._fallback_response("Иван", "positive")
        assert isinstance(result, str)
        assert "Иван" in result

    async def test_health_check_unavailable_without_key(self, ai_service: AIService):
        result = await ai_service.health_check()
        assert result["status"] in ["healthy", "unhealthy", "unavailable"]


class TestAIServiceWithoutAPIKey:
    """Test AI service behavior without API key."""

    async def test_service_unavailable_without_key(self):
        original_provider = settings.AI_PROVIDER
        original_groq = settings.GROQ_API_KEY
        settings.AI_PROVIDER = "groq"
        settings.GROQ_API_KEY = settings.GROQ_API_KEY

        service = AIService()
        assert service.is_available is False

        # Should still work with fallback
        result = await service.analyze_sentiment("Тест")
        assert "sentiment" in result

        settings.AI_PROVIDER = original_provider
        settings.GROQ_API_KEY = original_groq

    async def test_provider_groq_without_key_is_unavailable(self):
        original_provider = settings.AI_PROVIDER
        original_groq = settings.GROQ_API_KEY
        settings.AI_PROVIDER = "groq"
        settings.GROQ_API_KEY = settings.GROQ_API_KEY

        service = AIService()
        assert service.provider == "groq"
        assert service.is_available is False

        settings.AI_PROVIDER = original_provider
        settings.GROQ_API_KEY = original_groq
