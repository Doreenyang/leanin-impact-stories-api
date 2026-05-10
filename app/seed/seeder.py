"""Seed database with realistic impact stories for demo purposes."""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.database import SessionLocal, engine, Base
from app.models.impact_story import ImpactStory
from datetime import datetime, timedelta
import uuid
import random

# Realistic, emotionally resonant stories generated with AI assistance
SEED_STORIES = [
    {
        "title": "Negotiated a 30% Raise After Circle Practice",
        "story_text": "I had never negotiated salary before. My Circle created a safe space where I practiced the conversation dozens of times with women who had been through it. When the moment came, I felt prepared and confident. I got the raise and learned I was making 30% less than market rate. The Circle literally paid for itself in one conversation.",
        "industry": "Finance",
        "career_level": "Mid",
        "outcome_tags": ["raise", "confidence", "skill_development"],
        "moderation_status": "approved",
        "ai_summary": "Circle negotiation practice led to 30% salary increase and market rate adjustment.",
        "created_at": datetime.utcnow() - timedelta(days=random.randint(1, 60))
    },
    {
        "title": "Landed My Dream Role After Career Pivot",
        "story_text": "At 38, I wanted to move from accounting to product design but felt I was too late. Two women in my Circle had made similar transitions and created a roadmap for me. They reviewed my portfolio, practiced interviews with me, and one even referred me to her company. I started my new role last month and wake up excited about work for the first time in years.",
        "industry": "Technology",
        "career_level": "Senior",
        "outcome_tags": ["career_pivot", "mentorship", "networking"],
        "moderation_status": "approved",
        "ai_summary": "Women in Circle provided roadmap and referral for accounting to product design transition.",
        "created_at": datetime.utcnow() - timedelta(days=random.randint(1, 60))
    },
    {
        "title": "From Imposter Syndrome to Conference Keynote",
        "story_text": "I was terrified of public speaking and turned down opportunities constantly. My Circle created a judgment-free zone where I practiced presentations monthly. Their specific, kind feedback helped me improve without feeling criticized. Last month, I delivered a keynote at our industry's biggest conference. I never would have volunteered without the confidence my Circle built.",
        "industry": "Healthcare",
        "career_level": "Mid",
        "outcome_tags": ["public_speaking", "confidence", "leadership"],
        "moderation_status": "approved",
        "ai_summary": "Monthly Circle presentation practice led to conference keynote and overcoming public speaking fear.",
        "created_at": datetime.utcnow() - timedelta(days=random.randint(1, 60))
    },
    {
        "title": "Built a Network That Changed My Career",
        "story_text": "As an introverted engineer, I thought networking meant being fake and transactional. My Circle showed me it's about genuine relationships and mutual support. They helped me identify my authentic networking style—one-on-one coffee chats instead of large events. Those coffee chats led to learning about a role that wasn't posted publicly. I've since referred three other women from my Circle to opportunities.",
        "industry": "Technology",
        "career_level": "Early",
        "outcome_tags": ["networking", "confidence", "mentorship"],
        "moderation_status": "approved",
        "ai_summary": "Circle transformed introvert's approach to networking, leading to hidden job opportunities.",
        "created_at": datetime.utcnow() - timedelta(days=random.randint(1, 60))
    },
    {
        "title": "Advocated for All-Woman Interview Panels",
        "story_text": "My Circle discussed research showing diverse interview panels lead to better hiring. Armed with data and role-played conversations from my Circle, I proposed all-woman panels for our department. Leadership agreed, and in six months, we increased female hires by 40%. One conversation in my Circle sparked systemic change in my company.",
        "industry": "Education",
        "career_level": "Mid",
        "outcome_tags": ["leadership", "confidence", "skill_development"],
        "moderation_status": "approved",
        "ai_summary": "Circle discussion and practice led to implementing all-woman interview panels and 40% more female hires.",
        "created_at": datetime.utcnow() - timedelta(days=random.randint(1, 60))
    },
    {
        "title": "Motherhood Didn't End My Career—My Circle Made Sure",
        "story_text": "After maternity leave, I felt invisible and considered stepping back. My Circle, which included three other working mothers, shared strategies for staying visible during leave and returning with confidence. They reviewed my talking points for the return conversation and helped me articulate my value. I returned to a promotion, not a demotion.",
        "industry": "Marketing",
        "career_level": "Mid",
        "outcome_tags": ["promotion", "work_life_balance", "confidence"],
        "moderation_status": "approved",
        "ai_summary": "Circle of working mothers provided visibility strategies for return from maternity leave, resulting in promotion.",
        "created_at": datetime.utcnow() - timedelta(days=random.randint(1, 60))
    },
    {
        "title": "Took a Seat at the Table—Literally",
        "story_text": "I always sat at the back in meetings and rarely spoke. My Circle challenged me: sit at the table and contribute at least once. We practiced this in our sessions. The first time I sat at the front, my [Team Member] noticed I was there and asked my opinion directly. That moment changed how I saw myself and how others saw me. I'm now leading teams, not just supporting them.",
        "industry": "Financial Services",
        "career_level": "Early",
        "outcome_tags": ["confidence", "leadership", "skill_development"],
        "moderation_status": "approved",
        "ai_summary": "Circle practice in visibility led to speaking up in meetings and eventually leading teams.",
        "created_at": datetime.utcnow() - timedelta(days=random.randint(1, 60))
    }
]

def seed_database():
    """Seed the database with realistic impact stories."""
    db = SessionLocal()
    
    try:
        # Clear existing stories
        db.query(ImpactStory).delete()
        
        for story_data in SEED_STORIES:
            story = ImpactStory(
                id=uuid.uuid4(),
                **story_data
            )
            db.add(story)
        
        db.commit()
        print(f"✅ Seeded {len(SEED_STORIES)} impact stories successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("🌱 Seeding Lean In Impact Stories database...")
    seed_database()
