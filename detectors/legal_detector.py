from typing import List, Dict, Any
from core.detector import BaseDetector
from core.models import HallucinationType
from utils.logger import logger
import re

class CitationValidator(BaseDetector):
    """Validates legal citations and references."""
    
    def __init__(self):
        super().__init__("CitationValidator")
        self._known_courts = self._load_known_courts()
    
    def detect(self, text: str, domain: str = "legal") -> List[Dict[str, Any]]:
        """Validate legal citations."""
        issues = []
        
        # Pattern for legal citations
        citation_patterns = [
            r'(?:U\.S\.|Supreme Court)\s+v\.\s+([A-Za-z\s]+)',
            r'(\d+)\s+U\.S\.C\.\s+(?:§)?([0-9]+)',
            r'Rule\s+(\d+(?:\.\d+)*)',
        ]
        
        for pattern in citation_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                # Validate the citation format
                if isinstance(match, tuple):
                    case_name = match[0] if match else ""
                    if case_name and not self._is_valid_case(case_name):
                        issues.append({
                            'type': HallucinationType.FACTUAL_ERROR,
                            'citation': case_name,
                            'message': f"Case '{case_name}' not found in legal database",
                            'severity': 'high'
                        })
        
        logger.info(f"Citation validation: {len(issues)} issues found")
        return issues
    
    def _is_valid_case(self, case_name: str) -> bool:
        """Check if case name is valid."""
        # Simplified validation - in practice, check against legal database
        return len(case_name.split()) >= 2
    
    def _load_known_courts(self) -> set:
        """Load known court identifiers."""
        return {
            'Supreme Court', 'Court of Appeals', 'District Court',
            'Circuit Court', 'Federal Court', 'State Court'
        }

class JurisdictionChecker(BaseDetector):
    """Checks jurisdiction accuracy in legal claims."""
    
    def __init__(self):
        super().__init__("JurisdictionChecker")
    
    def detect(self, text: str, domain: str = "legal") -> List[Dict[str, Any]]:
        """Check jurisdiction accuracy."""
        issues = []
        
        # Check for jurisdiction mismatches
        jurisdiction_errors = [
            (r'UK law.*applies.*in.*US', 'UK law does not apply in US courts'),
            (r'federal.*law.*all states', 'Not all federal laws apply uniformly in all states'),
            (r'state.*law.*international', 'State law does not have international jurisdiction'),
        ]
        
        for pattern, message in jurisdiction_errors:
            if re.search(pattern, text, re.IGNORECASE):
                issues.append({
                    'type': HallucinationType.FACTUAL_ERROR,
                    'message': message,
                    'severity': 'high'
                })
        
        logger.info(f"Jurisdiction check: {len(issues)} issues found")
        return issues

class PrecedentAccuracyChecker(BaseDetector):
    """Checks accuracy of legal precedents."""
    
    def __init__(self):
        super().__init__("PrecedentAccuracyChecker")
    
    def detect(self, text: str, domain: str = "legal") -> List[Dict[str, Any]]:
        """Check precedent accuracy."""
        issues = []
        
        # Extract precedent references
        precedent_pattern = r'(?:in|per)\s+([A-Za-z\s]+)(?:\s+case|\s+ruling|\s+decision)'
        matches = re.findall(precedent_pattern, text, re.IGNORECASE)
        
        for precedent in matches:
            # Check for common precedent misstatements
            if not self._is_valid_precedent(precedent):
                issues.append({
                    'type': HallucinationType.FACTUAL_ERROR,
                    'precedent': precedent,
                    'message': f"Precedent '{precedent}' may be incorrectly cited",
                    'severity': 'high'
                })
        
        logger.info(f"Precedent accuracy check: {len(issues)} issues found")
        return issues
    
    def _is_valid_precedent(self, precedent: str) -> bool:
        """Validate precedent reference."""
        # Simplified validation
        return len(precedent.strip()) > 2
