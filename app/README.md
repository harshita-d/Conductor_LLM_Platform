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
  - ***BaseModel***:
    - Base class for all our data models
  - ***Field***:
    - Adds validation rules and documentation
  - ***List***, ***Optional***, ***Dict***:
    - Type hints for complex data
  - ***datetime***:
    - For timestamps
  - ***Enum***:
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
  - ***provider***: 
    - Must be valid provider
    - Default is Auto
    - Purpose is Which AI service to use
  
  - ***messages***:
    - List of ChatMessage
    - Required
    - At least 1 message
    - Purpose Conversation history

  - ***model***:
    - Optional string
    - Default None
    - Any string or null
    - Purpose Specific model (e.g., "gpt-4")

  - ***temperature***:
    - float
    - default 0.7
    - must be between 0.0 to 2.0
    - Purpose Response creativity

  - ***max_tokens***
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