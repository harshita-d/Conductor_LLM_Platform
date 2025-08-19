from dotenv import load_dotenv
from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging
from .providers import list_providers, get_provider

load_dotenv()

logger = logging.getLogger(
    __name__
)
@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan manager for startup and shutdown events"""
    # startup
    logger.info("Starting app....")
    available_provider=list_providers()
    for provider_name in available_provider:
        try:
            provider=get_provider(provider_name)
            
    yield
    


app=FastAPI(
    title="LLM Platform"
    description="""
    **Enterprise LLM Orchestration Platform**

    intelligently routes your requests across multiple AI providers 
    while optimizing for cost, speed, and quality.
    """
    version="1.0.0"
    lifespan=lifespan
)

