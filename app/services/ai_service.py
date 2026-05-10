import logging
from typing import Dict, List
import re

logger = logging.getLogger(__name__)

class AIService:
    """Mock AI service for PII detection, tag suggestion, and summarization.
    
    IMPORTANT: This is a mock implementation demonstrating the pattern.
    In production, this would call OpenAI API or deploy a fine-tuned NLP model.
    
    Trade-offs in this mock:
    - Uses regex (catches ~90% of cases)
    - No context awareness (ML models would be much better)
    - Single-pass (no multi-turn reasoning)
    - But: works locally without API keys, demonstrates architecture
    """
    
    async def detect_pii(self, text: str) -> Dict:
        """Detect personally identifiable information in text.
        
        Returns findings and whether PII was detected.
        
        Current approach: regex patterns + keyword matching
        TODO: Replace with NER (Named Entity Recognition) model
        TODO: Add context filtering (e.g., "Apple pie" vs "Apple Inc")
        """
        findings = []
        
        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if re.search(email_pattern, text):
            findings.append("email_detected")
        
        # Phone number pattern (US format, can extend)
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        if re.search(phone_pattern, text):
            findings.append("phone_detected")
        
        # Common company names (hardcoded for now)
        # TODO: Use company database or ML classifier
        company_indicators = ['Google', 'Apple', 'Microsoft', 'Amazon', 'Meta', 'Netflix']
        for company in company_indicators:
            if company.lower() in text.lower():
                findings.append(f"company_name:{company}")
        
        # Capitalized names (simple heuristic, many false positives)
        # TODO: Replace with proper NER model
        name_pattern = r'\b[A-Z][a-z]+ [A-Z][a-z]+\b'
        potential_names = re.findall(name_pattern, text)
        for name in potential_names:
            # Exclude common words that might be capitalized
            common_words = ['My Circle', 'Lean In', 'Women In']
            if name not in common_words:
                findings.append(f"potential_name:{name}")
        
        logger.debug(f"PII detection found {len(findings)} items")
        return {
            "contains_pii": len(findings) > 0,
            "findings": findings
        }
    
    async def suggest_tags(self, text: str) -> List[str]:
        """Analyze text and suggest relevant outcome tags.
        
        Current approach: keyword matching
        TODO: Use text classification model or GPT for better accuracy
        
        Tags help with:
        - Feed filtering (\"show me stories about promotions\")
        - Analytics (\"how many stories mention leadership?\")
        - Recommendations (\"find stories similar to mine\")
        """
        text_lower = text.lower()
        suggested = []
        
        # Keyword-based tag suggestion
        # These keywords were built from analyzing seed stories
        # TODO: Use ML classifier for better accuracy
        tag_keywords = {
            "promotion": ["promotion", "promoted", "advanced", "senior role"],
            "raise": ["raise", "salary", "compensation", "negotiated pay"],
            "confidence": ["confidence", "imposter", "believed in myself", "found my voice"],
            "career_pivot": ["transitioned", "switched", "new industry", "career change"],
            "leadership": ["leadership", "led a team", "manager", "director", "executive"],
            "networking": ["network", "connection", "introduced", "met people"],
            "skill_development": ["learned", "skill", "training", "certification"],
            "mentorship": ["mentor", "mentored", "guidance", "advice"],
            "work_life_balance": ["balance", "flexibility", "remote work", "family"],
            "public_speaking": ["speaking", "presentation", "spoke at", "keynote"]
        }
        
        for tag, keywords in tag_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                suggested.append(tag)
        
        # Ensure at least one tag (fallback)
        if not suggested:
            suggested.append("career_growth")
        
        # Limit to top 5 (prevents tag explosion)
        return suggested[:5]
    
    async def generate_summary(self, text: str) -> str:
        """Generate a concise summary of the impact story for feed preview.
        
        Current approach: extract first 150 chars
        TODO: Use abstractive summarization (GPT, BART, etc.)
        
        This is shown in the feed list before user clicks full story.
        """
        # Simple extractive summary: first meaningful sentence
        summary = text[:150].rsplit('.', 1)[0] + "."
        return summary
