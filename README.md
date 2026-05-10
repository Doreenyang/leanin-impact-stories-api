# Lean In Impact Stories API

A backend service that powers a public-facing feed of anonymized career growth stories from Lean In Circle members.

## Why This Feature Matters

Women considering joining Lean In often need to see themselves in the success of others before taking the leap. This API transforms the abstract promise of "peer support" into concrete, relatable evidence of career impact. It answers the question every potential member asks: "Will this actually work for someone like me?"

## Quick Start (3 minutes)

### Prerequisites
- **Docker Desktop** (download from https://www.docker.com/products/docker-desktop) - Must be running
- **Python 3.10+** (optional, for local testing without Docker)

### Setup

**Step 1: Start Docker containers** (includes PostgreSQL database automatically)
```bash
cd leanin-impact-stories-api
docker-compose up -d
```

Expected output:
```
api     INFO:     Started server process [10]
db      LOG:  database system is ready to accept connections
```

**Step 2: Access the API**

Open your browser:
- **Interactive API Docs** (Swagger): http://localhost:8000/docs ← **Start here!**
- **Alternative Docs** (ReDoc): http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

The 7 seed stories are automatically loaded when the database initializes.

### Run Tests Locally (Optional)

```bash
# Install Python dependencies
pip install -r requirements.txt

# Run all tests
pytest tests/test_stories.py -v
```

Expected: 13/13 tests pass 

## API Examples

### Submit an Impact Story

```bash
curl -X POST http://localhost:8000/api/v1/impact-stories \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Negotiating my first raise",
    "story_text": "My Circle helped me practice negotiation conversations...",
    "industry": "Tech",
    "career_level": "Mid",
    "outcome_tags": ["raise", "confidence"]
  }'
```

### Get Filtered Stories

```bash
# Get stories about promotions in tech
curl "http://localhost:8000/api/v1/impact-stories?industry=tech&outcomes=promotion&page=1"

# Get analytics
curl "http://localhost:8000/api/v1/impact-stories/analytics"
```

## AI Integration

I used AI tools for this project:

- **Claude**: Generated realistic seed stories that emotionally align with Lean In's mission
- **Claude**: Helped design the moderation flow and PII detection logic
- **AI Feature Design**: The mock AI service demonstrates how real AI (like GPT-5) would do automated PII detection, tag suggestion, and story summarization

## What I'd Build Next

- **Real AI Integration**: Connect OpenAI API for sophisticated PII detection and abstractive summarization
- **Authentication**: Add proper admin JWT auth for the moderation endpoint
- **Caching**: Redis cache for the most-queried story feeds
- **Admin Dashboard**: Simple UI for moderators to review and approve stories
- **User Upvoting**: Let community members signal which stories resonate most
