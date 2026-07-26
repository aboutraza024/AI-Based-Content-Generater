from typing import Optional
from pydantic import BaseModel, Field

from app.schemas.enums import ContentType, Tone


class HumanizeRequest(BaseModel):
    content_type: ContentType = Field(..., description="What kind of text this is, e.g. blog or email")
    target_audience: Optional[str] = Field(default="General Audience")
    tone: Tone = Field(..., description="How the final text should sound")
    text: str = Field(..., description="The text you want rewritten")


class HumanizeResponse(BaseModel):
    humanized_content: str = Field(..., description="The rewritten, natural-sounding text")
    word_count_actual: int = Field(default=0)
    success: bool = True
