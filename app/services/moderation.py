from typing import List

class ModerationService:
    """Service to handle story moderation."""
    
    def validate_moderation_status(self, status: str) -> bool:
        """Validate moderation status."""
        return status in ["approved", "rejected", "pending"]
