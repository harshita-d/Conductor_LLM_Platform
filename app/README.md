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

### `File Structure Overview`

    ```
    models.py contains:
    ├── Enums (MessageRole, Provider)
    ├── Request Models (ChatMessage, ChatRequest)
    ├── Response Models (ChatResponse, ProviderStatus, SystemStatus)
    ├── Error Models (ErrorResponse, HealthResponse)
    └── Configuration (examples, validation rules)
    ```

### `imports`

- **_BaseModel_**:
  - Base class for all our data models
- **_Field_**:
  - Adds validation rules and documentation
- **_List_**, **_Optional_**, **_Dict_**:
  - Type hints for complex data
- **_datetime_**:
  - For timestamps
- **_Enum_**:
  - For fixed choices (like provider names)

### `MessageRole Enum`

- Defines valid message roles in conversations
- Prevents typos (can't send "usr" instead of "user")

### `Provider Enum`

- Lists all supported LLM providers
- AUTO lets Conductor choose the best provider
- Prevents users from requesting unsupported providers

### `ChatMessage Models`

- Represents a single message in conversation
- role must be from MessageRole enum
- content must be at least 1 character long
  > "..." means "required field"

### `ChatRequest Models`

- **_provider_**:

  - Must be valid provider
  - Default is Auto
  - Purpose is Which AI service to use

- **_messages_**:

  - List of ChatMessage
  - Required
  - At least 1 message
  - Purpose Conversation history

- **_model_**:

  - Optional string
  - Default None
  - Any string or null
  - Purpose Specific model (e.g., "gpt-4")

- **_temperature_**:

  - float
  - default 0.7
  - must be between 0.0 to 2.0
  - Purpose Response creativity

- **_max_tokens_**
  - Integer
  - Default 1000
  - must be between 1 to 4000
  - Purpose Response length limit

### `ChatResponse Model`

- The AI response
- Metadata
- Analytics data

### `ProviderStatus Models`

- Health status - Is the provider working
- Performance - How fast is it responding?
- Reliability - How often does it succeed?
- Usage - How many requests processed?

### `SystemStatus Model`

- Overall health of entire platform
- All provider metrics in one response
- Total usage statistics
- System uptime

### `ErrorResponse Model`

- Consistent error format across all endpoints
- Detailed error info for debugging
- Error source tracking (which provider failed)
- Error timestamps for monitoring

# providers/init.py

- Provider Factory - Creates provider instances on demand
- Provider Registry - Keeps track of all available providers
- Module Interface - Single entry point for accessing providers
- Extensibility Layer - Easy to add new providers

# providers/base.py

- this provides the blueprint that all LLM providers must follow.
- it ensures all providers have same capability and interface
- it implements **_AbstractBase_** class pattern

### `imports`

- **_ABC, abstractmethod_**: Create AbstractBase class
- **_List, Dict, Any, Optional_**: types
- **_time_**: performance timing measurement
- **_datetime_**: Timestamps for metrics and health checks
- **_models_**: importing models

### `BaseProvider class`

- this is an `AbstractBase` class
- **_Instance Variables_**:
  - **name**: name of the provider
  - **is_healthy**: Current health status
  - **last_check**: Last health check time
  - **total_requests**: Total API calls made
  - **successful_requests**: Successful API calls
  - **failed_requests**: Failed API calls
  - **total_latency**: Cumulative response time
  - **last_error**: Most recent error message
- Through these metrices we will know which provider is fastest

#### `Abstract Method: chat_completion`

- Generate chat completion using the provider
- **Args**:
  - chat competion request
- **Response**:
  - chat response with the generated content
- **Raises**:
  - raises exception if API fails

#### `Abstract Method: health_check`

- It monitors if the API is responding
- Switiches to healthy providers
- Include in system status API
- **Response**:
  - True if healthy else False

#### `Abstract Method: get_available_models`

- Get list of available models for this provider.
- Let users specify which model to use
- **Response**:
  - List of model names/identifiers

#### `Abstract Method: estimate_cost`

- Estimate the cost for a given number of tokens.
- **Args**:
  - tokens: Number of tokens
  - model: Model identifier
- **Response**:
  - Estimated Cost in USD

#### `Concrete Method: update_metrics`

- It update providers performace metrics
-

# providers/gemini_provider.py

- this file is a conceret implementation of the BaseProvider abstract class
- It connects to google Gemeni API using offical SDK

### `imports`

- **_google.generativeai as genai_**:
  - it an offical gemini SDK
- **_time_**:
  - Performance timing
- **_datetime_**:
  - timestamp
- **_os_**:
  - env variable
- **_logging_**:
  - Debug/error logging
- **_BaseProvider_**:
  - import parent class
- **_models_**:
  - importing models

