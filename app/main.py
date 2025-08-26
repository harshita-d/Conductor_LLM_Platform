from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException, Depends
from contextlib import asynccontextmanager
import logging
from .providers import list_providers, get_provider, GeminiProvider
from typing import Dict, List
from .providers import BaseProvider
from fastapi.middleware.cors import CORSMiddleware
import time
from datetime import timedelta
from .models import HealthResponse, ChatResponse, ChatRequest, Provider
import os

load_dotenv()

logger = logging.getLogger(__name__)

# Global variables
providers: Dict[str, BaseProvider] = {}
start_time = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan manager for startup and shutdown events"""
    # startup
    logger.info("Starting app....")
    initialized_count = 0
    available_provider = list_providers()
    for provider_name in available_provider:
        try:
            provider = get_provider(provider_name)
            print("provider==", provider)
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH"],
    allow_headers=["*"],
)

# ROOT END POINT


@app.get("/", tags=["General"])
async def root():
    """Welcome endpoint"""
    return {"message": "Wemcome to LLM Platform", "providers": list(providers.keys())}


async def check_all_providers_health():
    results = []
    available_providers = list_providers()
    for name in available_providers:
        try:
            provider_class = get_provider(name)
            healthy = await provider_class.health_check()
        except Exception as e:
            print(f"Failed health check for {name}: {e}")
            healthy = False
        results.append({"name": name, "status": healthy})
    return results


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health():
    uptime_seconds = time.time() - start_time
    uptime_pretty = str(timedelta(seconds=int(uptime_seconds)))
    result = await check_all_providers_health()
    return HealthResponse(provider=result, uptime=uptime_pretty)


async def Validate_api_key(api_key: str = Header(..., alias="X-API-Key")):
    """Validate API Key from the request Header"""
    expected_key = os.getenv("GEMINI_API_KEY")
    if api_key != expected_key:
        raise HTTPException(
            status_code=401, detail="Invalid API key. Please check your API-Key header."
        )


async def _select_provider(request: ChatRequest, healthy_providers: List[str]) -> str:
    """Select the optimal provider for the request"""

    if request.provider == Provider.AUTO:
        return healthy_providers[0]

    if request.provider.value not in healthy_providers:
        raise HTTPException(status=40, detail="Provided model not avavailble")

    return request.provider.value


async def _filter_healthy_providers(providers: List[Dict[str, bool]]) -> List[str]:
    """Filter only healthy providers"""
    healthy_providers = [
        provider["name"] for provider in providers if provider["status"]
    ]
    if not healthy_providers:
        raise HTTPException(
            status_code=503,
            detail="No AI providers are currently available. Please try again later.",
        )
    return healthy_providers


@app.post("/chat", tags=["chat"])
async def chat_response(request: ChatRequest, api_key: str = Depends(Validate_api_key)):
    """
    Generate AI chat completion using the optimal provider.
    **Auto-routing logic:**
    - Complex analysis → Gemini(high quality)
    """
    result = await check_all_providers_health()
    healthy_providers = await _filter_healthy_providers(result)
    selected_provider_name = await _select_provider(request, healthy_providers)

    selected_provider = providers[selected_provider_name]
    try:
        response = await selected_provider.chat_completion(request)
        return response

    except Exception as e:
        pass
