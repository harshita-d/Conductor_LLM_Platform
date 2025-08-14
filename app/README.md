# Folder Structure

```
conductor-llm-platform/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   └── providers/
│       ├── __init__.py
│       ├── base.py
│       └── gemini_provider.py
├── requirements.txt
├── .env
├── Dockerfile
├── docker-compose.yml
└── .dockerignore
```

# Models.py

- The models.py file defines data structures using Pydantic that:
    - Validate incoming requests (prevent bad data)
    - Format outgoing responses (consistent API responses)
    - Generate API documentation (automatic Swagger docs)
    - Provide type hints (better IDE support)

## File Structure Overview

    ```
    models.py contains:
    ├── Enums (MessageRole, Provider)
    ├── Request Models (ChatMessage, ChatRequest)  
    ├── Response Models (ChatResponse, ProviderStatus, SystemStatus)
    ├── Error Models (ErrorResponse, HealthResponse)
    └── Configuration (examples, validation rules)
    ```