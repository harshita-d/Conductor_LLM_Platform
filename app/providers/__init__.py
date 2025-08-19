"""This file contais all the helper functions required"""

from .base import BaseProvider
from .gemini_provider import GeminiProvider
from typing import List

AVAILABLE_PROVIDERS = {
    "gemini": GeminiProvider,
}


def list_providers() -> List[str]:
    """Get list of avaiable providers"""
    return list(AVAILABLE_PROVIDERS.keys())


def get_provider(provider_name: str) -> BaseProvider:
    """Factory Function to get a provider instance"""
    if provider_name not in AVAILABLE_PROVIDERS:
        supported_providers = ", ".join(AVAILABLE_PROVIDERS.keys())
        raise ValueError(
            f"Provider {provider_name} not supported. Available providers are: {supported_providers}"
        )

    provider_class = AVAILABLE_PROVIDERS[provider_name]
    return provider_class()


__all__ = [
    BaseProvider,
    GeminiProvider,
    AVAILABLE_PROVIDERS,
    list_providers,
]
