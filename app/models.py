from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Optional
from datetime import datetime, timezone, timedelta


class MessageRole(str, Enum):
    """Message roles for chat conservation"""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Provider(str, Enum):
    """Available LLM Providers"""

    AUTO = "auto"
    GEMINI = "gemini"


class ChatMessage(BaseModel):
    """Individual message in a chat conversation"""

    role: MessageRole = Field(..., description="Role of the message")
    content: str = Field(..., description="content of the message", min_length=1)

    class config:
        json_schema_extra = {
            "example": {"role": "user", "content": "Hello, how are you?"}
        }


class ChatRequest(BaseModel):
    """Request model for chat completion"""

    provider: Provider = Field(default=Provider.AUTO, description="LLM provider to use")
    message: List[ChatMessage] = Field(
        ..., min_length=1, description="List of messages in the conversation"
    )
    model: Optional[str] = Field(
        default=None,
        description="Specific model to use (optional, provider default used if not specified)",
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Controls randomness: 0 = deterministic, 2 = very random",
    )
    max_tokens: int = Field(
        default=1000, ge=1, le=4000, description="Maximum number of tokens to generate"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "provider": "auto",
                "message": [{"role": "user", "content": "Write a short poem about AI"}],
                "temperature": 0.7,
                "max_tokens": 1000,
            }
        }


class ChatResponse(BaseModel):
    """Response model for chat completion"""

    provider: str = Field(..., description="Provider that handled the request")
    model: str = Field(..., description="Specific model that was used")
    response: str = Field(..., description="Generated AI response")
    token_used: int = Field(..., description="Number of tokens consumed")
    cost: float = Field(..., description="Cost in USD (0.00 for free tiers)")
    latency_ms: str = Field(..., description="Response time in milliseconds")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )

    class Congig:
        json_schema_extra = {
            "example": {
                "provider": "auto",
                "model": "gemini-pro",
                "response": "Artificial minds that learn and grow,\nIn silicon dreams they come to know...",
                "tokens_used": 150,
                "cost": 0.0,
                "latency_ms": 1250.5,
                "timestamp": "2024-01-15T10:30:00Z",
            }
        }


class ProviderStatus(BaseModel):
    name: str = Field(..., description="name of the service provider")
    status: bool = Field(..., description="status of the service provider")


class HealthResponse(BaseModel):
    provider: List[ProviderStatus] = Field(
        ..., description="list of providers and their status"
    )
    uptime: str = Field(..., description="Service uptime")


class ProviderStatus(BaseModel):
    """Status information for a single provider"""

    name: str = Field(..., description="Provider name")
    healthy: bool = Field(..., description="Whether the provider is currently healthy")
    last_check: datetime = Field(..., description="last health check timestamp")
    average_latency: float = Field(..., description="Average response time")
    success_rate: float = Field(..., description="success rate between 0.0 to 0.1")
    total_request: int = Field(default=0, description="total request processed")


class SystemStatus(BaseModel):
    """Status information for a single provider"""

    status: str = Field(..., description="Overall System Status")
    providers: List[ProviderStatus] = Field(..., description="Status of all providers")
    total_requests: int = Field(..., description="total requests accross all providers")
    uptime: timedelta = Field(..., description="System uptime")
