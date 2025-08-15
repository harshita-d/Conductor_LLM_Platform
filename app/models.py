from pydantic import BaseModel, Field
from enum import Enum


class MessageRole(str, Enum):
    """Message roles for chat conservation"""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessage(BaseModel):
    """Individual message in a chat conversation"""

    role: MessageRole = Field(..., description="Role of the message")
    content: str = Field(..., description="content of the message", min_length=1)

    class config:
        json_schema_extra = {
            "example": {"role": "user", "content": "Hello, how are you?"}
        }
