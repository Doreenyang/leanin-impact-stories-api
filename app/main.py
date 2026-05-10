import logging
from datetime import datetime
from typing import List, Optional
import uuid

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import and_, text
from sqlalchemy.orm import Session

from app.database import engine, get_db, Base
from app.models.impact_story import ImpactStory, StorySubmission, ModerationLog
from app.schemas.story import (
    StoryCreate, StoryResponse, StoryModerate, 
    StoryFeedResponse, AnalyticsResponse
)
from app.services.ai_service import AIService
from app.services.moderation import ModerationService
from app.services.anonymizer import AnonymizerService

# Configure logging
logger = logging.getLogger(__name__)

# Create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Lean In Impact Stories API",
    description="Backend service for anonymized career growth stories from Lean In Circles",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ai_service = AIService()
moderation_service = ModerationService()
anonymizer_service = AnonymizerService()

@app.post("/api/v1/impact-stories", response_model=StoryResponse, status_code=201)
async def submit_story(story: StoryCreate, db: Session = Depends(get_db)):
    """Submit a new impact story with AI processing and moderation workflow.
    
    Process:
    1. Save raw submission for audit trail
    2. Detect PII (emails, names, companies)  
    3. Anonymize sensitive data to protect privacy
    4. Auto-suggest outcome tags for discoverability
    5. Generate AI summary for feed preview
    6. Create story in pending status for moderation
    """
    try:
        story_id = uuid.uuid4()
        
        # Preserve original text for audit trail and future model training
        raw_submission = StorySubmission(
            id=uuid.uuid4(),
            raw_text=story.story_text,
            submitted_at=datetime.utcnow()
        )
        
        # Detect PII before publishing (security-first)
        pii_findings = await ai_service.detect_pii(story.story_text)
        raw_submission.contains_pii = pii_findings["contains_pii"]
        
        # Sanitize PII if found (trade-off: lose detail for privacy)
        story_text_final = story.story_text
        if pii_findings["contains_pii"]:
            story_text_final = anonymizer_service.sanitize(
                story.story_text, 
                pii_findings["findings"]
            )
            logger.info(f"Story {story_id}: PII detected and anonymized")
        
        raw_submission.processed_text = story_text_final
        
        # Auto-tag for better feed filtering and discoverability
        outcome_tags = await ai_service.suggest_tags(story_text_final)
        
        # Generate summary for feed preview (quick read)
        summary = await ai_service.generate_summary(story_text_final)
        
        # Create story in pending state (requires manual moderation)
        impact_story = ImpactStory(
            id=story_id,
            title=story.title,
            story_text=story_text_final,
            industry=story.industry,
            career_level=story.career_level,
            outcome_tags=outcome_tags,
            is_anonymous=story.is_anonymous if story.is_anonymous is not None else True,
            moderation_status="pending",  # Must be approved before showing publicly
            circle_id=story.circle_id,
            ai_summary=summary,
            ai_flagged=pii_findings["contains_pii"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Audit trail: complete record of all processing decisions
        moderation_record = ModerationLog(
            id=uuid.uuid4(),
            story_id=story_id,
            action="submitted",
            notes=f"PII found: {pii_findings['contains_pii']}. Auto-tags: {outcome_tags}",
            created_at=datetime.utcnow()
        )
        
        # Atomic transaction: all succeed or all rollback
        db.add(raw_submission)
        db.add(impact_story)
        db.add(moderation_record)
        db.commit()
        db.refresh(impact_story)
        
        logger.info(f"Story {story_id} submitted and queued for moderation")
        return impact_story
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error submitting story: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to submit story")

@app.get("/api/v1/impact-stories", response_model=StoryFeedResponse)
async def get_stories(
    industry: Optional[str] = None,
    career_level: Optional[str] = None,
    outcomes: Optional[str] = Query(None, description="Comma-separated outcome tags"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get filtered, moderated impact stories feed."""
    
    query = db.query(ImpactStory).filter(
        ImpactStory.moderation_status == "approved"
    )
    
    # Apply filters
    if industry:
        query = query.filter(ImpactStory.industry.ilike(f"%{industry}%"))
    
    if career_level:
        query = query.filter(ImpactStory.career_level == career_level)
    
    if outcomes:
        outcome_list = [o.strip() for o in outcomes.split(",")]
        # Filter stories that have at least one matching outcome tag
        # Fetch all and filter in Python for database-agnostic approach
        all_stories = query.all()
        filtered_stories = [
            s for s in all_stories 
            if s.outcome_tags and any(tag in outcome_list for tag in s.outcome_tags)
        ]
        total = len(filtered_stories)
        # Apply pagination to filtered results
        stories = filtered_stories[(page - 1) * page_size : page * page_size]
        
        return {
            "stories": stories,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": (total + page_size - 1) // page_size
            }
        }
    
    # Get total count
    total = query.count()
    
    # Get paginated results
    stories = query.order_by(
        ImpactStory.created_at.desc()
    ).offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "stories": stories,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": (total + page_size - 1) // page_size
        }
    }

@app.patch("/api/v1/impact-stories/{story_id}/moderate", response_model=StoryResponse)
async def moderate_story(
    story_id: uuid.UUID,
    moderation: StoryModerate,
    db: Session = Depends(get_db)
):
    """Moderate a story (approve/reject). In production, this would have admin auth."""
    
    story = db.query(ImpactStory).filter(ImpactStory.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    story.moderation_status = moderation.status
    story.updated_at = datetime.utcnow()
    
    # Log moderation action
    mod_log = ModerationLog(
        id=uuid.uuid4(),
        story_id=story_id,
        action=moderation.status,
        notes=moderation.notes or f"Moderator {moderation.status} story",
        created_at=datetime.utcnow()
    )
    
    db.add(mod_log)
    db.commit()
    db.refresh(story)
    
    return story

@app.get("/api/v1/impact-stories/analytics", response_model=AnalyticsResponse)
async def get_analytics(db: Session = Depends(get_db)):
    """Get aggregated analytics about impact stories."""
    
    from sqlalchemy import func
    
    # Most common outcome tags
    common_outcomes = db.query(
        func.unnest(ImpactStory.outcome_tags).label('tag'),
        func.count('*').label('count')
    ).filter(
        ImpactStory.moderation_status == 'approved'
    ).group_by('tag').order_by(func.count('*').desc()).limit(10).all()
    
    # Industry distribution
    industry_dist = db.query(
        ImpactStory.industry,
        func.count(ImpactStory.id)
    ).filter(
        ImpactStory.moderation_status == 'approved'
    ).group_by(ImpactStory.industry).order_by(func.count(ImpactStory.id).desc()).all()
    
    # Career level distribution
    career_dist = db.query(
        ImpactStory.career_level,
        func.count(ImpactStory.id)
    ).filter(
        ImpactStory.moderation_status == 'approved'
    ).group_by(ImpactStory.career_level).all()
    
    # Moderation queue stats
    pending_count = db.query(ImpactStory).filter(
        ImpactStory.moderation_status == 'pending'
    ).count()
    
    return {
        "total_stories": db.query(ImpactStory).filter(ImpactStory.moderation_status == 'approved').count(),
        "pending_moderation": pending_count,
        "common_outcomes": [{"tag": tag, "count": count} for tag, count in common_outcomes],
        "industry_distribution": [{"industry": ind, "count": count} for ind, count in industry_dist],
        "career_levels": [{"level": level, "count": count} for level, count in career_dist]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
