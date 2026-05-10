from sqlalchemy import Column, String, Text, Boolean, DateTime, ARRAY, UUID, Index
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from app.database import Base
import uuid
from datetime import datetime

class ImpactStory(Base):
    """Primary table for published impact stories.
    
    Design notes:
    - Denormalized (stores tags directly, not normalized table) for faster reads
    - Stories are read-heavy (feed queries), write-light - denormalization worth it
    - GIN index on outcome_tags enables fast filtering
    - Composite index on (moderation_status, created_at) for feed queries
    """
    __tablename__ = "impact_stories"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    story_text = Column(Text, nullable=False)  # Anonymized content
    industry = Column(String(100))
    career_level = Column(String(50))
    outcome_tags = Column(ARRAY(String))  # Auto-suggested tags
    is_anonymous = Column(Boolean, default=True)
    moderation_status = Column(String(20), default="pending")  # pending, approved, rejected
    circle_id = Column(PGUUID(as_uuid=True), nullable=True)
    ai_summary = Column(Text)  # Quick preview for feed
    ai_flagged = Column(Boolean, default=False)  # PII was detected
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        # Optimized for most common query: "show me approved stories, newest first"
        Index('idx_moderation_created', 'moderation_status', 'created_at'),
        # GIN index for filtering by outcome tags
        Index('idx_outcome_tags', 'outcome_tags', postgresql_using='gin'),
    )

class StorySubmission(Base):
    """Audit table: preserves original, unprocessed text.
    
    Why separate table?
    1. Track what was actually submitted (vs. what we published)
    2. Validate PII detection accuracy over time
    3. Train better models with real-world examples
    4. Legal compliance if privacy issues arise
    """
    __tablename__ = "story_submissions"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    raw_text = Column(Text, nullable=False)  # Original, unmodified
    processed_text = Column(Text)  # After anonymization
    contains_pii = Column(Boolean, default=False)  # Detection result
    submitted_at = Column(DateTime, default=datetime.utcnow)

class ModerationLog(Base):
    """Complete audit trail of all moderation decisions.
    
    Enables:
    - Tracking moderator actions
    - Reviewing decisions later
    - Building moderation patterns
    - Accountability
    """
    __tablename__ = "moderation_logs"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    story_id = Column(PGUUID(as_uuid=True), nullable=False)
    action = Column(String(50), nullable=False)  # submitted, approved, rejected, etc.
    notes = Column(Text)  # Reason, moderator notes
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        # Fast lookup: "show me all moderation for this story"
        Index('idx_modlog_story', 'story_id', 'created_at'),
    )
