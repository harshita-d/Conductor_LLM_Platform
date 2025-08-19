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
- It records performance data after every API call (success or failure) to build analytics and monitoring capabilities.
- **Args**:
  - latency_ms: Total time spent waiting for responses in milliseconds
  - success: Whether the request was successful
  - error: Error message if request failed
- **total_requests**: otal API calls made
- **latency_ms**: Total time spent waiting for responses
- **success: True**: to track how many calls worked
  - **successful_requests**: total successfull calls
  - **last_error**: Clear error when things work again
- **success: False**: tracking how many calls fail
  - **failed_requests**: total failed request
  - **last_error**: Store most recent error message

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

#### `chat_completion`

- its an asynchronous function
- **Args**:
  - ChatRequest
- **Response**:
  - ChatResponse
- Calculating API call time
- processing end to end latency time
- **GenerationConfig**:
  - configure the AI's text generation behavior
  - temperature: Randomness and creativity
  - max_output_tokens: maximum output length
  - candidate_count: number of different response variants to generate
  - top_p: this is a text generation sampling method that controls how the AI choose the next word/token when generating response
    - top_p=0.8 means: Pick words until cumulative probability ≥ 80%
    - example: sunny (30%) + cloudy (25%) + rainy (20%) + hot (10%)
  - top_k: Vocabulary selection by limiting to K most probable words. - top_k=10 means: - Only consider the top 10 most likely words - [pizza, pasta, sushi, burgers, salad, tacos, fish, chicken, rice, bread]
    > top_k is applied first, then top_p is applied to the remaining candidates.
- the char response for GEMINI API:

  ```
  response.text (str)
  – The generated text content (empty string if nothing generated or blocked).

  response.candidates (List[Candidate])
  – A list of one or more Candidate objects, each representing a possible completion. Each Candidate has:
  – text (str): the candidate’s generated text
  – finish_reason (Enum): why generation stopped, e.g.

  STOP – reached natural end

  MAX_TOKENS – hit token limit

  SAFETY – blocked by safety filters

  RECITATION – blocked for copyright

  OTHER – other error

  response.metadata (optional)
  – Additional metadata such as model version, request ID, or timing info, depending on SDK version.
  ```

- **Exception**:
  - latency_ms: Captures how long the request took before failing, so failures still contribute to your performance metrics.
  - update_metrics: Increments total_requests and failed_requests, adds latency_ms to total_latency, and stores last_error = error_msg. This keeps your success rate and average latency calculations accurate.

#### `_format_messages`

- its a helper message converts standard chat messages into GEMINI specific prompt.
- it convert a list of messages into a single string that gemini understands
- its a private method
- **Args**:
  - List[ChatMessages]
- **Response**:

  - single formated prompt string

  ```python
  messages = [
    ChatMessage(role="system", content="You are a helpful coding assistant"),
    ChatMessage(role="user", content="How do I create a Python list?"),
    ChatMessage(role="assistant", content="You can create a list using square brackets: my_list = [1, 2, 3]"),
    ChatMessage(role="user", content="Can you show me more examples?")
  ]

  # final output
  """Context: You are a helpful coding assistant
  User: How do I create a Python list?
  Assistant: You can create a list using square brackets: my_list = [1, 2, 3]
  User: Can you show me more examples?"""
  ```

#### `_estimate_token`

- **token**: prompt + response
- 1 token ≈ 4 characters on average for English text; ≈ 0.75 words.
- Gemini-Pro supports up to 30,720 tokens of input + output combined. If your prompt + response exceed that, generation is truncated.
- Generating text happens one token at a time; each token requires a full forward pass through the model.
- \_estimate_tokens() sums prompt + response character lengths, divides by 4, then adds a ~10% buffer to approximate the true token count
- **Args**:
  prompt: Input prompt
  response: Generated response
- **Response**:
  Estimated token count

# Main.py

- This is the entry point of the application

### `imports`

- FastAPI Modules: app creation, exceptions, header/dep injection, responses.
  ```python
  from fastapi import FastAPI, HTTPException, Header, Depends
  from fastapi.responses import JSONResponse
  ```
- CORS middleware: cross-origin support.
  ```python
  from fastapi.middleware.cors import CORSMiddleware
  ```
- asynccontextmanager: manage startup/shutdown lifecycle.
  ```python
  from contextlib import asynccontextmanager
  ```
- dotenv: load .env configuration (API keys).
  ```python
  from dotenv import load_dotenv
  ```
- logging: structured log output.
  ```python
  import os, time, logging
  ```
-

#### `app=FastAPI()`

- this is a fastAPI application instance
  - Stores global config (title, description, middleware, lifespan).
  - Registers your routes (when you write @app.get("/...") etc.).
  - Manages state (like app.state for DB pools, provider registry).
  - Implements the ASGI protocol (so Uvicorn/Hypercorn can talk to it).
- We need this because ASGI server needs an entrypoint as uvicorn expects an ASGI app object as entry point
- we use the below command to run the fastAPI server
  `uvicorn app.main:app --reload`
- where main:app means
  - **main** → the Python file main.py (without .py)
  - **app** → the FastAPI instance (app = FastAPI()) inside that file

#### `lifespan`

- this project depends on external LLM providers, which means we must do things before the app can start handling request. and things to do when it shuts down, thats why we need **_lifespan_**
  ```python
  @asynccontextmanager
  async def lifespan(app: FastAPI):
      # startup logic
      yield
      # shutdown logic
  ```
- lifespan is **async** because startup and shutdown work often involve input/output from other tasks
- the other tasks are like
  - initalizing a database connection pool
  - running health checks againts external APIs
  - starting stopping background tasks
- if lifespan was **sync**, we couldn't **await** these async operations
- **lifespan** passes to **FastAPI** constructor
- FastAPI calls lifespan(app) function, where it runs the startup block, and if any error comes than app fails to start
- lifespan does not has to be a generator, instead it has to be a context manager specifically async
- @asynccontextmanager lets you write an async context manager as a single async generator function.
  - Everything before yield = **aenter** (startup)
  - Everything after yield = **aexit** (shutdown)
  - The yield marks the precise boundary where FastAPI starts serving requests.
- **asynccontextmanager**:

  - FastAPI's lifespan option expects an async context manager that wraps the whole app lifetime
  - asynccontextmanager solves pronlem of writing async generator, turns that generator into a valid async context manager with **aenter** / **aexit** under the hood
  - it will allow to use async/await for I/O

- alternate to writing **no generator**

  ```python
  class AppLifespan:
      def __init__(self, app):
          self.app = app

      async def __aenter__(self):
          # startup
          self.app.state.providers = {}
          # await async setup...
          return self.app  # (optional)

      async def __aexit__(self, exc_type, exc, tb):
          # shutdown
          # await async cleanup...
          return False  # don’t suppress exceptions

  def lifespan(app):
      return AppLifespan(app)

  app = FastAPI(lifespan=lifespan)
  ```
