from typing import List
import re

class AnonymizerService:
    """Service to sanitize personally identifiable information from stories."""
    
    def sanitize(self, text: str, pii_findings: List[str]) -> str:
        """
        Replace identified PII with generic placeholders.
        """
        sanitized = text
        
        for finding in pii_findings:
            if finding.startswith("potential_name:"):
                name = finding.split(":")[1]
                sanitized = sanitized.replace(name, "[Team Member]")
            elif finding.startswith("company_name:"):
                company = finding.split(":")[1]
                sanitized = sanitized.replace(company, "a tech company")
            elif finding == "email_detected":
                # Replace email pattern
                sanitized = re.sub(
                    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                    '[email redacted]',
                    sanitized
                )
            elif finding == "phone_detected":
                sanitized = re.sub(
                    r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
                    '[phone redacted]',
                    sanitized
                )
        
        return sanitized
