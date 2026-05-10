# Design Document: Lean In Impact Stories API

## Problem Statement

Lean In's website effectively communicates the *existence* of Circles, but struggles to communicate their *impact*. Women visiting leanin.org face a conversion challenge: they need to see relatable, concrete evidence that participating in a Circle leads to real career outcomes before they invest their time.

This API solves that by creating a living, breathing portfolio of anonymized impact stories that can be filtered by industry, career level, and outcome—making the value proposition tangible and personal.

## Architecture

```
Client (future frontend)
↓
FastAPI Server
↓
AI Processing Layer (PII detection, tagging, summarization)
↓
PostgreSQL (primary storage)
```

**Key Components:**
- **Story Ingestion**: Accepts submissions, runs AI processing, stores raw and sanitized versions
- **Moderation Pipeline**: Simple status-based flow (pending → approved/rejected) with audit logging
- **Query Engine**: Optimized for filtered, paginated reads with GIN indexes for array operations

## Database Design Rationale

**impact_stories table**: The single source of truth for all public-facing story data. I chose a denormalized design (storing tags and summary directly) over a normalized tag table because:
- Stories are read-heavy, write-light (typical content platform pattern)
- Array columns with GIN indexes provide excellent query performance
- Simpler data model = fewer joins = faster feed queries

**story_submissions table**: Separate from the main table to preserve the original, unprocessed text. This is critical for:
- Auditing AI decisions (was redaction too aggressive?)
- Training better AI models on real-world PII patterns
- Legal compliance if privacy concerns arise

**Indexing Strategy**: The composite index on `(moderation_status, created_at)` is optimized for the most common query: "show me approved stories, newest first." The GIN index on `outcome_tags` enables efficient array containment queries.

## Key Tradeoffs

**Anonymity vs. Authenticity**: Stories are more powerful when specific, but must protect privacy. The solution: aggressive AI-powered PII detection that redacts names and companies while preserving the emotional truth of the story. "My mentor Sarah at Google" becomes "My mentor at a tech company"—less specific, but still authentic.

**Moderation Complexity**: Full content moderation is expensive. I chose a lightweight model with optional AI flagging as a screening step, trusting Circle members to submit appropriate content while providing admin override capability.

**Real AI vs. Mock AI**: For this demo, I implemented a mock AI service with regex-based PII detection and keyword-based tagging. This demonstrates the *pattern* without requiring API keys. In production, this would be replaced with OpenAI API calls or a fine-tuned model.

## Scaling Considerations

At Lean In's scale (150,000+ Circles in 183 countries):

1. **Async Processing**: Move AI operations to a task queue (Celery/Redis) to keep API responses fast
2. **Read Replicas**: The story feed is read-heavy; PostgreSQL read replicas would handle traffic from millions of users
3. **Caching**: Frequently-accessed feeds (top stories, analytics) cached with short TTLs
4. **Vector Search**: For semantic similarity ("show me stories like this one"), add pgvector embeddings
5. **Multi-language Support**: Extend AI processing to support the 183 countries Lean In serves

## Why This Over Alternatives

I considered a Circle Health Tracker (valuable for internal ops) but chose Impact Stories because:
- **Directly serves end-users**, not just administrators
- **Mission-aligned**: Prove Circles work rather than just measure them  
- **Demo-ready**: The value is immediately visible in the API responses
- **Extensible**: Can evolve into a machine learning-powered recommendation engine
