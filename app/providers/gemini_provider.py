import logging
from .base import BaseProvider
import os
import google.generativeai as genai
from ..models import ChatRequest, ChatResponse, ChatMessage
import time
from typing import List, Dict, Union
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException

logger = logging.getLogger(__name__)


class GeminiProvider(BaseProvider):
    """Google gemeni LLM provider"""

    def __init__(self):
        """initialize the gemini provider"""
        super().__init__("gemini")

        self.model_name = "gemini-2.0-flash"
        self.model = None  # Will be initialized dynamically

    def _initialize_model(self, api_key: str):
        if not api_key:
            raise ValueError("API KEY variable is required")

        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(f"models/{self.model_name}")
        except Exception as e:
            print(f"Failed to initialize Gemini provider: {e}")
            self.is_healthy = False
            raise HTTPException(status_code=401, detail="Invalid Gemini API key")

    def _format_message(self, messages: List[ChatMessage]) -> str:
        """Converts Chat messages to GEMINI compatible prompt"""
        formatted_message = []
        for message in messages:
            if message.role == "system":
                formatted_message.append(f"Context: {message.content}")
            elif message.role == "user":
                formatted_message.append(f"User: {message.content}")
            elif message.role == "assistant":
                formatted_message.append(f"Assistant:{message.content}")
        return "\n".join(formatted_message)

    def _estimate_token(self, prompt: str, response: str) -> int:
        """Estimated token count"""
        total_chars = len(response)
        estimated_token = int(total_chars / 4)
        return int(estimated_token * 1.1)

    def estimated_cost(self, tokens: int, model: str) -> float:
        """Estimated cost for GEMINI api usage"""
        return 0.0  # current;y GEMINI is free

    async def chat_completion(self, request: ChatRequest, api_key: str) -> ChatResponse:
        """Generate Chat completion using GEMINI"""
        self._initialize_model(api_key)
        start_time = time.time()
        try:
            prompt = self._format_message(request.message)
            generation_config = genai.types.GenerationConfig(
                temperature=request.temperature,
                max_output_tokens=request.max_tokens,
                candidate_count=1,
                top_p=0.8,
                top_k=10,
            )
            safety_settings = {
                genai.types.HarmCategory.HARM_CATEGORY_HARASSMENT: genai.types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                genai.types.HarmCategory.HARM_CATEGORY_HATE_SPEECH: genai.types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                genai.types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: genai.types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                genai.types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: genai.types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            }

            print("Sending request to gemini")

            response = ""
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config=generation_config,
                    safety_settings=safety_settings,
                )
            except Exception as e:
                raise HTTPException(
                    status=400, detail=f"error while getting response: {e}"
                )
            latency_ms: float = (time.time() - start_time) * 1000

            if not response.text:
                if response.candidates[0].finish_reason.name == "SAFETY":
                    raise Exception("Content blocked by safety filters")
                elif response.candidates[0].finish_reason.name == "MAX_TOKENS":
                    raise Exception("Content hit token limit")
                else:
                    raise Exception(
                        f"No response generated: {response.candidates[0].finish_reason.name}"
                    )

            token_used = self._estimate_token(prompt, response.text)
            cost = self.estimated_cost(token_used, "gemini-pro")
            self.update_metrics(latency_ms, True)
            return ChatResponse(
                provider="gemini",
                model=self.model_name,
                response=response.text.strip(),
                token_used=token_used,
                cost=cost,
                latency_ms=str(timedelta(seconds=int(latency_ms))),
                timestamp=datetime.now(timezone.utc),
            )

        except Exception as e:
            latency_ms: float = (time.time() - start_time) * 1000
            self.update_metrics(latency_ms, False, str(e))
            raise Exception(f"GEMINI API Error: {str(e)}")

    async def health_check(self, api_key: str) -> Dict[str, Union[bool, str]]:
        """
        Check if GEMINI API is accessible and responding.
        Returns a dict with status and optional error message.
        """
        self._initialize_model(api_key)

        try:
            test_config = genai.types.GenerationConfig(
                max_output_tokens=10,
                temperature=0
            )
            response = self.model.generate_content(
                "hello",
                generation_config=test_config
            )
            content = response.candidates[0].content.parts[0]
            is_healthy = bool(content.text and len(content.text.strip()) > 0)
            self.is_healthy = is_healthy
            self.last_check = datetime.now(timezone.utc)

            return {"status": is_healthy, "error": None}

        except Exception as e:
            error_message = str(e).split("\n")[0]  # Simplify verbose tracebacks
            print("❌ Gemini Health Check Failed:", error_message)
            self.is_healthy = False
            self.last_check = datetime.now(timezone.utc)
            return {"status": False, "error": error_message}