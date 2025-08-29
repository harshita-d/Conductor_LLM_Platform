from abc import ABC, abstractmethod
from datetime import datetime, timezone
from ..models import ChatRequest, ChatResponse, ProviderStatus
from typing import Optional


class BaseProvider(ABC):
    """Base Provider class"""

    def __init__(self, name):
        self.name = name
        self.is_healthy = True
        self.last_check = datetime.now(timezone.utc)
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.total_latency = 0.0
        self.last_error = None

    @abstractmethod
    def chat_completion(self, request: ChatRequest, api_key: str) -> ChatResponse:
        """Generate a Chat Completion"""
        pass

    @abstractmethod
    def estimated_cost(self, tokens: int, model: str) -> float:
        """Estimate the cost for a given number of tokens"""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check health of a particular provider"""
        pass

    def update_metrics(
        self, latency_ms: float, success: bool, error: Optional[str] = None
    ):
        """update provider performance metrix"""
        self.total_requests += 1
        self.total_latency += latency_ms
        if success:
            self.successful_requests += 1
            self.last_error = None
        else:
            self.failed_requests += 1
            self.last_error = error

        print("self.total_requests========", self.total_requests)

    def get_status(self) -> ProviderStatus:
        """Get current provider status and metrics"""

        avg_latency = self.total_latency / max(self.total_requests, 1)
        success_rate = self.successful_requests / max(self.total_requests, 1)
        return ProviderStatus(
            name=self.name,
            healthy=self.is_healthy,
            last_check=self.last_check,
            average_latency=avg_latency,
            success_rate=success_rate,
            total_requests=self.total_requests,
        )
