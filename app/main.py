from dotenv import load_dotenv
from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging
from .providers import list_providers, get_provider
from typing import Dict
from .providers import BaseProvider

load_dotenv()

logger = logging.getLogger(__name__)

# Global variables
providers: Dict[str, BaseProvider] = {}
initialized_count = 0


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan manager for startup and shutdown events"""
    # startup
    logger.info("Starting app....")
    available_provider = list_providers()
    for provider_name in available_provider:
        try:
            provider = get_provider(provider_name)
            if await provider.health_check():
                providers[provider_name] = provider
                logger.info(f"{provider_name} provider initialized successfully")
                initialized_count += 1
            else:
                logger.warning(f"failed health check for {provider_name} provider")
        except Exception as e:
            logger.error(f"failed to initialize {provider_name} provider")
    if initialized_count == 0:
        logger.error("No providers initialized successfully!")
    else:
        logger.info(f"Available providers: {', '.join(providers.keys())}")

    yield

    # shutdown
    logger.info("Shutting down the service...")


app = FastAPI(
    title="LLM Platform",
    description="""
    **Enterprise LLM Orchestration Platform**

    intelligently routes your requests across multiple AI providers 
    while optimizing for cost, speed, and quality.
    """,
    version="1.0.0",
    lifespan=lifespan,
)
