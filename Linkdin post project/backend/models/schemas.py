from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class PostTone(str, Enum):
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    INSPIRATIONAL = "inspirational"
    EDUCATIONAL = "educational"
    PROMOTIONAL = "promotional"

class PostLength(str, Enum):
    SHORT = "short"  # 1-2 sentences
    MEDIUM = "medium"  # 1-2 paragraphs
    LONG = "long"  # 3+ paragraphs

class PostRequest(BaseModel):
    topic: Optional[str] = Field(None, description="Topic or theme for the post")
    content: Optional[str] = Field(None, description="Pre-written content (optional)")
    tone: PostTone = Field(PostTone.PROFESSIONAL, description="Tone of the post")
    length: PostLength = Field(PostLength.MEDIUM, description="Length of the post")
    include_hashtags: bool = Field(True, description="Include relevant hashtags")
    schedule_time: Optional[str] = Field(None, description="Schedule time (ISO format)")
    target_audience: Optional[str] = Field(None, description="Target audience description")
    call_to_action: Optional[str] = Field(None, description="Specific call to action")

class PostResponse(BaseModel):
    success: bool
    post_id: Optional[str] = None
    content: str
    message: str
    created_at: Optional[datetime] = None
    url: Optional[str] = None

class UserInfo(BaseModel):
    id: str
    first_name: str
    last_name: str
    headline: Optional[str] = None
    profile_picture: Optional[str] = None
    num_connections: Optional[int] = None