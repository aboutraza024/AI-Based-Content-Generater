from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from app.schemas.enums import ContentType, Tone, RegionVariant

class OutlineRequest(BaseModel):
    language: str = Field(default="English", description="Target language")
    region: RegionVariant = Field(default=RegionVariant.USA, description="Regional English variant")
    content_type: ContentType = Field(..., description="Informational, Commercial, or Transactional")
    product_name: str = Field(..., description="Product, service, or blog topic name")
    target_audience: Optional[str] = Field(default="General Audience", description="Target audience for the content")
    tone: Tone = Field(default=Tone.PROFESSIONAL, description="Writing tone")
    sense: Optional[str] = Field(default="High quality comprehensive coverage", description="Overall intent and angle")
    word_count: int = Field(default=1000, ge=100, le=10000, description="Target word count")
    include_meta: bool = Field(default=True, description="Whether to auto-generate meta description & tags")

class CompetitorAnalysis(BaseModel):
    topics_covered: List[str] = Field(default_factory=list)
    style_structure: str = Field(default="Standard informational structure")
    depth_scope: str = Field(default="Comprehensive coverage")
    summary: str = Field(default="Competitor content analyzed")

class OutlineResponse(BaseModel):
    outline: str = Field(..., description="Editable outline generated for user review")
    competitor_analysis: CompetitorAnalysis
    query_used: str = Field(default="")
    request_params: Dict[str, Any] = Field(default_factory=dict)
    success: bool = True
