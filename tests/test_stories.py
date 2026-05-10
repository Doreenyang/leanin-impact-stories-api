import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_submit_story():
    """Test story submission endpoint."""
    story_data = {
        "title": "Test Career Growth Story",
        "story_text": "My Circle helped me prepare for a big presentation that led to my promotion. The feedback from women who had been through similar situations was invaluable.",
        "industry": "Technology",
        "career_level": "Mid",
        "outcome_tags": ["promotion", "public_speaking"],
        "is_anonymous": True
    }
    
    response = client.post("/api/v1/impact-stories", json=story_data)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == story_data["title"]
    assert data["moderation_status"] == "pending"
    assert "ai_summary" in data
    assert "id" in data

def test_submit_story_validation():
    """Test that invalid stories are rejected."""
    # Missing required field
    invalid_story = {
        "title": "Too short",
        "story_text": "x" * 40  # Too short (min 50)
        # Missing industry, career_level
    }
    
    response = client.post("/api/v1/impact-stories", json=invalid_story)
    assert response.status_code == 422  # Validation error

def test_get_stories_feed():
    """Test story feed retrieval."""
    response = client.get("/api/v1/impact-stories")
    assert response.status_code == 200
    data = response.json()
    assert "stories" in data
    assert "pagination" in data
    assert data["pagination"]["page"] == 1
    assert data["pagination"]["page_size"] == 10

def test_get_stories_pagination():
    """Test pagination works correctly."""
    response = client.get("/api/v1/impact-stories?page=1&page_size=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data["stories"]) <= 5
    assert data["pagination"]["page_size"] == 5

def test_get_filtered_stories():
    """Test filtering stories by industry and outcomes."""
    response = client.get("/api/v1/impact-stories?industry=Tech&outcomes=promotion")
    assert response.status_code == 200
    data = response.json()
    # All returned stories should have been moderated and match filters
    for story in data["stories"]:
        assert story["moderation_status"] == "approved"

def test_get_filtered_stories_multiple_outcomes():
    """Test filtering with multiple outcome tags."""
    response = client.get("/api/v1/impact-stories?outcomes=leadership,confidence")
    assert response.status_code == 200
    data = response.json()
    for story in data["stories"]:
        assert story["moderation_status"] == "approved"
        # At least one matching outcome tag
        assert any(tag in story["outcome_tags"] for tag in ["leadership", "confidence"])

def test_moderate_story():
    """Test story moderation."""
    # First, submit a story
    story_data = {
        "title": "Story to Moderate",
        "story_text": "My Circle provided amazing support during my career transition. I learned to advocate for myself and found a role that aligns with my values.",
        "industry": "Marketing",
        "career_level": "Mid"
    }
    
    create_response = client.post("/api/v1/impact-stories", json=story_data)
    assert create_response.status_code == 201
    story_id = create_response.json()["id"]
    
    # Moderate it
    mod_response = client.patch(
        f"/api/v1/impact-stories/{story_id}/moderate",
        json={"status": "approved", "notes": "Great story, well-written"}
    )
    assert mod_response.status_code == 200
    assert mod_response.json()["moderation_status"] == "approved"

def test_moderate_story_invalid_status():
    """Test that invalid moderation status is rejected."""
    story_data = {
        "title": "Test Story",
        "story_text": "Test text that is long enough to pass validation requirements.",
        "industry": "Tech",
        "career_level": "Senior"
    }
    
    create_response = client.post("/api/v1/impact-stories", json=story_data)
    story_id = create_response.json()["id"]
    
    # Try invalid status
    mod_response = client.patch(
        f"/api/v1/impact-stories/{story_id}/moderate",
        json={"status": "invalid_status"}
    )
    assert mod_response.status_code == 422  # Validation error

def test_moderate_nonexistent_story():
    """Test moderating a story that doesn't exist."""
    import uuid
    fake_id = str(uuid.uuid4())
    
    response = client.patch(
        f"/api/v1/impact-stories/{fake_id}/moderate",
        json={"status": "approved"}
    )
    assert response.status_code == 404

def test_analytics():
    """Test analytics endpoint."""
    response = client.get("/api/v1/impact-stories/analytics")
    assert response.status_code == 200
    data = response.json()
    assert "total_stories" in data
    assert "pending_moderation" in data
    assert "common_outcomes" in data
    assert "industry_distribution" in data
    assert "career_levels" in data
    assert isinstance(data["total_stories"], int)
    assert isinstance(data["common_outcomes"], list)

def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data

def test_ai_pii_detection():
    """Test that PII is detected and anonymized."""
    story_with_pii = {
        "title": "My Mentorship Journey",
        "story_text": "John Smith at Microsoft helped me grow. You can reach me at john@example.com or call 555-123-4567. Sarah recommended I apply.",
        "industry": "Technology",
        "career_level": "Mid"
    }
    
    response = client.post("/api/v1/impact-stories", json=story_with_pii)
    assert response.status_code == 201
    data = response.json()
    
    # Check that story text was processed
    assert data["ai_summary"] is not None
    # AI should have flagged the PII
    assert data["ai_flagged"] == True or "email redacted" in data["story_text"] or "[" in data["story_text"]

def test_ai_tag_suggestion():
    """Test that tags are auto-suggested by AI."""
    story = {
        "title": "I Got a Promotion",
        "story_text": "Thanks to my Circle's mentorship and guidance, I was promoted to senior manager. The leadership training helped me develop the confidence I needed.",
        "industry": "Technology",
        "career_level": "Senior"
    }
    
    response = client.post("/api/v1/impact-stories", json=story)
    assert response.status_code == 201
    data = response.json()
    
    # Should have auto-suggested tags
    assert isinstance(data["outcome_tags"], list)
    assert len(data["outcome_tags"]) > 0
    # Should contain relevant tags like promotion, leadership, confidence, mentorship
    relevant_tags = ["promotion", "leadership", "confidence", "mentorship", "skill_development"]
    assert any(tag in data["outcome_tags"] for tag in relevant_tags)

