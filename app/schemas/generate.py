from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from app.schemas.enums import ContentType, Tone, RegionVariant

class GenerateRequest(BaseModel):
    language: str = Field(default="English")
    region: RegionVariant = Field(default=RegionVariant.USA)
    content_type: ContentType
    product_name: str
    target_audience: Optional[str] = Field(default="General Audience")
    tone: Tone
    sense: Optional[str] = Field(default="High quality comprehensive coverage")
    word_count: int = Field(default=1000)
    confirmed_outline: str = Field(..., description="Confirmed and edited outline from step 4")
    competitor_summary: Optional[str] = Field(default="")
    include_meta: bool = Field(default=True)

class LintReport(BaseModel):
    semicolons_removed: int = 0
    hyphens_removed: int = 0
    oxford_commas_removed: int = 0
    repetitive_starts_fixed: int = 0
    violations_found: List[str] = Field(default_factory=list)
    is_clean: bool = True

class GenerateResponse(BaseModel):
    final_content: str = Field(..., description="Humanized and linted final content")
    raw_draft: Optional[str] = Field(default=None, description="Initial draft before humanization")
    lint_report: LintReport
    meta_description: Optional[str] = Field(default=None)
    meta_tags: List[str] = Field(default_factory=list)
    word_count_actual: int = Field(default=0)
    success: bool = True
