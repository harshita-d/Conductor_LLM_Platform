from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException, Depends
from contextlib import asynccontextmanager
import logging
from .providers import list_providers, get_provider, GeminiProvider
from typing import Dict, List, Union
from .providers import BaseProvider
from fastapi.middleware.cors import CORSMiddleware
import time
from datetime import timedelta
from .models import (
    HealthResponse,
    ChatResponse,
    ChatRequest,
    Provider,
    SystemStatus,
    ErrorResponse,
    HealthRequest,
)
import os
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

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
            providers[provider_name] = provider
            initialized_count += 1
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


async def check_all_providers_health(
    key_mapping: Dict[str, str] = {},
) -> List[Dict[str, Union[str, bool]]]:
    """
    Check health of all providers using the passed API keys.
    Returns a list of provider name + status.
    Raises HTTPException if any provider fails.
    """
    results: List[Dict[str, Union[str, bool]]] = []
    available_providers = list_providers()

    for name in available_providers:
        provider_class = get_provider(name)
        if name not in key_mapping:
            raise HTTPException(
                status_code=400, detail=f"Missing API key for provider: {name}"
            )

        health_result = await provider_class.health_check(key_mapping[name])
        status = health_result["status"]
        error = health_result["error"]
        if not status:
            raise HTTPException(status_code=400, detail=f"{name}: {error}")
        results.append({"name": name, "status": status})

    return results


@app.post("/health", response_model=HealthResponse, tags=["Health"])
async def health(api_keys: HealthRequest):
    uptime_seconds = time.time() - start_time
    uptime_pretty = str(timedelta(seconds=int(uptime_seconds)))
    key_mapping = {item.name: item.api_key for item in api_keys.providers}
    result = await check_all_providers_health(key_mapping)
    return HealthResponse(provider=result, uptime=uptime_pretty)


async def _select_provider(request: ChatRequest, healthy_providers: List[str]) -> str:
    """Select the optimal provider for the request"""

    if request.provider == Provider.AUTO:
        return healthy_providers[0]

    if request.provider.value not in healthy_providers:
        raise HTTPException(status_code=400, detail="Provided model not availble")

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


@app.post("/chat", response_model=ChatResponse, tags=["chat"])
async def chat_response(request: ChatRequest):
    """
    Generate AI chat completion using the optimal provider.
    **Auto-routing logic:**
    - Complex analysis → Gemini(high quality)
    """
    key_mapping = {item.name: item.api_key for item in request.api_keys or []}
    result = await check_all_providers_health(key_mapping)
    healthy_providers = await _filter_healthy_providers(result)
    selected_provider_name = await _select_provider(request, healthy_providers)

    if selected_provider_name not in providers:
        raise HTTPException(
            status_code=500,
            detail=f"Selected provider '{selected_provider_name}' is not initialized or healthy.",
        )
    selected_provider = providers[selected_provider_name]
    api_key = key_mapping.get(selected_provider_name)
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail=f"Missing API key for selected provider: {selected_provider_name}",
        )
    response = await selected_provider.chat_completion(request, api_key=api_key)
    if not response:
        raise HTTPException(status_code=500, detail=f"AI provider error: {selected_provider_name}")
    return response


        


@app.get("/status", response_model=SystemStatus, tags=["Health"])
async def system_status():
    """Get detailed system status including provider metrics"""
    provider_statuses = []
    total_requests = 0
    for provider in providers.values():
        status = provider.get_status()
        provider_statuses.append(status)
        total_requests += status.total_requests

    uptime = time.time() - start_time
    overall_status = (
        "healthy" if any(p.healthy for p in provider_statuses) else "unhealthy"
    )

    return SystemStatus(
        status=overall_status,
        providers=provider_statuses,
        total_requests=total_requests,
        uptime=uptime,
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    print("===========HTTPException Triggered===========")
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.status_code, detail=exc.detail, provider=None
        ).dict(),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """Handle unexpected exceptions."""
    print(f"=========Unexpected error==========2: {exc.detail}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="internal_server_error",
            detail="An unexpected error occurred. Please try again later.",
            provider=None,
        ).dict(),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    print("======422 Validation Error=====")
    e = exc.errors()
    return JSONResponse(
        status_code=422,
        content={
            "error": 422,
            "detail": "Invalid request format. Check required fields.",
            "validation_errors": e[0]["msg"],
        },
    )
