from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.enums import ContentType, Tone, RegionVariant
from app.schemas.generate import LintReport

class ReviseRequest(BaseModel):
    language: str = Field(default="English")
    region: RegionVariant = Field(default=RegionVariant.USA)
    content_type: ContentType
    product_name: str
    target_audience: Optional[str] = Field(default="General Audience")
    tone: Tone
    sense: Optional[str] = Field(default="High quality comprehensive coverage")
    confirmed_outline: str
    previous_content: str = Field(..., description="Previous generated content to be revised")
    revision_feedback: str = Field(..., description="User's feedback or instructions for revision")
    include_meta: bool = Field(default=True)

class ReviseResponse(BaseModel):
    revised_content: str = Field(..., description="Revised, humanized, and linted content")
    lint_report: LintReport
    meta_description: Optional[str] = Field(default=None)
    meta_tags: List[str] = Field(default_factory=list)
    word_count_actual: int = Field(default=0)
    success: bool = True
