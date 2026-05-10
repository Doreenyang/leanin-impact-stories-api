from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime
import uuid

class StoryCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=255)
    story_text: str = Field(..., min_length=50, max_length=5000)
    industry: str = Field(..., description="e.g., Tech, Healthcare, Finance")
    career_level: str = Field(..., description="e.g., Early, Mid, Senior, Executive")
    outcome_tags: Optional[List[str]] = Field(default_factory=list)
    is_anonymous: Optional[bool] = True
    circle_id: Optional[uuid.UUID] = None

class StoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    title: str
    story_text: str
    industry: Optional[str]
    career_level: Optional[str]
    outcome_tags: List[str]
    is_anonymous: bool
    moderation_status: str
    ai_summary: Optional[str]
    ai_flagged: bool
    created_at: datetime

class StoryModerate(BaseModel):
    status: str = Field(..., pattern="^(approved|rejected)$")
    notes: Optional[str] = None

class PaginationInfo(BaseModel):
    page: int
    page_size: int
    total: int
    total_pages: int

class StoryFeedResponse(BaseModel):
    stories: List[StoryResponse]
    pagination: PaginationInfo

class AnalyticsResponse(BaseModel):
    total_stories: int
    pending_moderation: int
    common_outcomes: List[dict]
    industry_distribution: List[dict]
    career_levels: List[dict]
