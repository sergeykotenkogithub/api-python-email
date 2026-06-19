"""
AI Service module.

This module provides AI-powered functionality including sentiment analysis,
message classification, and response generation using OpenAI API.
"""

import json
from typing import Optional, Dict, Any
from datetime import datetime
from app.config import settings
from app.utils.logger import get_logger, log_ai_request

logger = get_logger("AIService")


class AIService:
    """AI service for text analysis and generation."""
    
    def __init__(self):
        self.provider = (settings.AI_PROVIDER or "openai").lower()
        self.openai_api_key = settings.OPENAI_API_KEY
        self.groq_api_key = settings.GROQ_API_KEY
        self.model = (
            settings.GROQ_MODEL if self.provider == "groq" else settings.OPENAI_MODEL
        )
        self.is_available = False
        self._initialize_client()

    def _initialize_client(self):
        """Initialize the AI client based on provider."""
        try:
            if self.provider == "groq":
                if not self.groq_api_key:
                    logger.warning("GROQ_API_KEY is not set; AI will use fallback")
                    self.is_available = False
                    return
                from groq import AsyncGroq
                self.client = AsyncGroq(api_key=self.groq_api_key, timeout=30.0)
                self.is_available = True
                logger.info("Groq client initialized successfully")
            elif self.provider == "openai":
                if not self.openai_api_key:
                    logger.warning("OPENAI_API_KEY is not set; AI will use fallback")
                    self.is_available = False
                    return
                import openai
                self.client = openai.AsyncOpenAI(
                    api_key=self.openai_api_key,
                    timeout=30.0,
                )
                self.is_available = True
                logger.info("OpenAI client initialized successfully")
            else:
                logger.warning(f"Unknown AI provider '{self.provider}'")
                self.is_available = False
        except ImportError as e:
            logger.error(f"Required AI package not installed: {e}")
            self.is_available = False
        except Exception as e:
            logger.error(f"Failed to initialize AI client: {e}")
            self.is_available = False
    
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze the sentiment of the given text.
        
        Args:
            text: The text to analyze
            
        Returns:
            Dict with sentiment and confidence score
        """
        if not self.is_available:
            return self._fallback_sentiment_analysis(text)
        
        prompt = f"""Analyze the sentiment of the following message. 
Respond with a JSON object containing:
- sentiment: one of "positive", "negative", or "neutral"
- confidence: a number between 0 and 1
- explanation: brief explanation of the analysis

Message: {text}

Respond only with the JSON object, no other text."""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a sentiment analysis expert. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=150,
            )

            result = response.choices[0].message.content.strip()
            log_ai_request(prompt, result, self.model, response.usage.total_tokens)

            # Parse JSON response
            analysis = json.loads(result)
            return {
                "sentiment": analysis.get("sentiment", "neutral"),
                "confidence": analysis.get("confidence", 0.5),
                "explanation": analysis.get("explanation", "")
            }

        except Exception as e:
            logger.error(f"AI sentiment analysis failed: {e}")
            return self._fallback_sentiment_analysis(text)
    
    async def classify_message(self, text: str) -> Dict[str, Any]:
        """Classify the message into categories.
        
        Args:
            text: The text to classify
            
        Returns:
            Dict with category, priority, and confidence
        """
        if not self.is_available:
            return self._fallback_classification(text)
        
        prompt = f"""Classify this message into one of the following categories:
- project_inquiry (questions about projects or services)
- collaboration (offers to work together)
- job_offer (employment opportunities)
- general_question (general inquiries)
- feedback (comments about existing work)
- support (help requests)
- other (doesn't fit above categories)

Also determine priority: low, medium, high

Message: {text}

Respond with a JSON object containing:
- category: the category name
- priority: low, medium, or high
- confidence: number between 0 and 1
- reasoning: brief explanation

Respond only with the JSON object."""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert in customer communication analysis. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=200,
            )

            result = response.choices[0].message.content.strip()
            log_ai_request(prompt, result, self.model, response.usage.total_tokens)

            analysis = json.loads(result)
            return {
                "category": analysis.get("category", "other"),
                "priority": analysis.get("priority", "medium"),
                "confidence": analysis.get("confidence", 0.5),
                "reasoning": analysis.get("reasoning", "")
            }

        except Exception as e:
            logger.error(f"AI classification failed: {e}")
            return self._fallback_classification(text)
    
    async def generate_response(self, message: str, sender_name: str, sentiment: str = "neutral") -> str:
        """Generate a professional response to the message.
        
        Args:
            message: The original message
            sender_name: Name of the sender
            sentiment: Detected sentiment of the message
            
        Returns:
            Generated response text
        """
        if not self.is_available:
            return self._fallback_response(sender_name, sentiment)
        
        prompt = f"""Generate a professional response to this message from a potential client.
The response should be:
- Polite and professional
- Personalized based on the message content
- Brief (2-3 sentences)
- Include a call to action
- Match the tone of the original message

Sender name: {sender_name}
Original message: {message}
Message sentiment: {sentiment}

Generate a response in the same language as the original message.
Respond only with the response text, no other formatting."""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional developer responding to client inquiries. Be helpful and courteous."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300,
            )

            result = response.choices[0].message.content.strip()
            log_ai_request(prompt, result, self.model, response.usage.total_tokens)

            return result

        except Exception as e:
            logger.error(f"AI response generation failed: {e}")
            return self._fallback_response(sender_name, sentiment)
    
    async def analyze_message(self, message: str, sender_name: str) -> Dict[str, Any]:
        """Perform complete analysis of a message.
        
        Args:
            message: The message to analyze
            sender_name: Name of the sender
            
        Returns:
            Complete analysis including sentiment, classification, and suggested response
        """
        # Run all analyses concurrently
        import asyncio
        
        sentiment_task = self.analyze_sentiment(message)
        classification_task = self.classify_message(message)
        
        sentiment_result, classification_result = await asyncio.gather(
            sentiment_task, 
            classification_task
        )
        
        # Generate response based on analysis
        response = await self.generate_response(
            message, 
            sender_name, 
            sentiment_result["sentiment"]
        )
        
        return {
            "sentiment": sentiment_result["sentiment"],
            "category": classification_result["category"],
            "priority": classification_result["priority"],
            "suggested_response": response,
            "confidence": min(sentiment_result["confidence"], classification_result["confidence"]),
            "analysis_details": {
                "sentiment_explanation": sentiment_result.get("explanation", ""),
                "classification_reasoning": classification_result.get("reasoning", "")
            }
        }
    
    def _fallback_sentiment_analysis(self, text: str) -> Dict[str, Any]:
        """Fallback sentiment analysis using keyword matching."""
        text_lower = text.lower()
        
        positive_words = ['спасибо', 'отлично', 'замечательно', 'хорошо', 'рад', 'интересно', 'хотел бы', 'буду рад']
        negative_words = ['плохо', 'ужасно', 'проблема', 'ошибка', 'не работает', 'жалоба', 'недоволен']
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            sentiment = "positive"
            confidence = min(0.5 + positive_count * 0.1, 0.8)
        elif negative_count > positive_count:
            sentiment = "negative"
            confidence = min(0.5 + negative_count * 0.1, 0.8)
        else:
            sentiment = "neutral"
            confidence = 0.5
        
        return {
            "sentiment": sentiment,
            "confidence": confidence,
            "explanation": "Fallback analysis using keyword matching"
        }
    
    def _fallback_classification(self, text: str) -> Dict[str, Any]:
        """Fallback classification using keyword matching."""
        text_lower = text.lower()
        
        # Define keyword patterns for each category
        patterns = {
            "project_inquiry": ['проект', 'разработка', 'создать', 'сделать', 'сайт', 'приложение', 'стоимость', 'цена'],
            "collaboration": ['сотрудничество', 'вместе', 'партнерство', 'команда', 'работать вместе'],
            "job_offer": ['работа', 'вакансия', 'должность', 'зарплата', 'трудоустройство', 'приглашение'],
            "support": ['помощь', 'поддержка', 'проблема', 'ошибка', 'не работает', 'как'],
            "feedback": ['отзыв', 'мнение', 'оценка', 'нравится', 'не нравится']
        }
        
        # Find matching category
        best_category = "other"
        best_score = 0
        
        for category, keywords in patterns.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > best_score:
                best_score = score
                best_category = category
        
        # Determine priority based on keywords
        high_priority = ['срочно', 'важно', 'критично', 'немедленно']
        low_priority = ['когда будет время', 'не срочно', 'по возможности']
        
        if any(word in text_lower for word in high_priority):
            priority = "high"
        elif any(word in text_lower for word in low_priority):
            priority = "low"
        else:
            priority = "medium"
        
        return {
            "category": best_category,
            "priority": priority,
            "confidence": min(0.3 + best_score * 0.1, 0.7),
            "reasoning": "Fallback classification using keyword matching"
        }
    
    def _fallback_response(self, sender_name: str, sentiment: str) -> str:
        """Generate a fallback response."""
        name = sender_name.split()[0] if sender_name else "Уважаемый клиент"
        
        responses = {
            "positive": f"Спасибо за ваше сообщение, {name}! Я свяжусь с вами в ближайшее время для обсуждения деталей.",
            "negative": f"Спасибо за ваше обращение, {name}. Я обязательно рассмотрю ваше сообщение и свяжусь с вами.",
            "neutral": f"Здравствуйте, {name}! Благодарю за ваше сообщение. Я отвечу вам в ближайшее время."
        }
        
        return responses.get(sentiment, responses["neutral"])
    
    async def health_check(self) -> Dict[str, Any]:
        """Check AI service health."""
        if not self.is_available:
            return {
                "status": "unavailable",
                "provider": self.provider,
                "reason": "API key not configured or client initialization failed"
            }
        
        try:
            # Simple test request
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=5
            )
            
            return {
                "status": "healthy",
                "provider": self.provider,
                "model": self.model,
                "last_check": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "provider": self.provider,
                "error": str(e),
                "last_check": datetime.utcnow().isoformat()
            }


# Create global AI service instance
ai_service = AIService()


def get_ai_service() -> AIService:
    """Get AI service instance."""
    return ai_service