from typing import List, Dict, Any, Optional
from core.verifier import BaseVerifier
from core.models import Claim, VerificationResult, Evidence, ClaimStatus
from utils.logger import logger
import re

class MedicalKnowledgeBaseVerifier(BaseVerifier):
    """Verifies medical claims against medical knowledge base."""
    
    def __init__(self):
        super().__init__("MedicalKnowledgeBaseVerifier")
        self._medical_kb = self._load_medical_kb()
    
    def verify(self, claim: Claim) -> Optional[VerificationResult]:
        """Verify medical claim."""
        result = VerificationResult(
            claim=claim,
            status=ClaimStatus.UNKNOWN,
            reasoning="Medical verification in progress"
        )
        
        # Extract medical terms from claim
        medical_terms = self._extract_medical_terms(claim.text)
        
        # Check against knowledge base
        for term in medical_terms:
            if term.lower() in self._medical_kb:
                kb_entry = self._medical_kb[term.lower()]
                evidence = Evidence(
                    source="Medical Knowledge Base",
                    text=kb_entry['description'],
                    relevance_score=0.9,
                    credibility_score=0.95
                )
                result.evidence.append(evidence)
                result.supporting_count += 1
                result.status = ClaimStatus.SUPPORTED
        
        if not result.evidence:
            result.status = ClaimStatus.UNCERTAIN
            result.uncertainty_reasons.append("No matching medical knowledge base entries")
        
        result.confidence = 0.8 if result.evidence else 0.3
        return result
    
    def _extract_medical_terms(self, text: str) -> List[str]:
        """Extract medical terms from text."""
        # Simple extraction - in practice use NER
        medical_keywords = [
            'diabetes', 'hypertension', 'cancer', 'influenza', 'pneumonia',
            'syndrome', 'disease', 'disorder', 'treatment', 'therapy'
        ]
        
        terms = []
        for keyword in medical_keywords:
            if keyword.lower() in text.lower():
                terms.append(keyword)
        
        return terms
    
    def _load_medical_kb(self) -> Dict[str, Any]:
        """Load medical knowledge base."""
        return {
            'diabetes': {
                'description': 'A metabolic disorder affecting blood sugar regulation',
                'types': ['type1', 'type2', 'gestational'],
                'treatments': ['insulin', 'metformin', 'lifestyle_changes']
            },
            'hypertension': {
                'description': 'High blood pressure condition',
                'normal_bp': '120/80 mmHg',
                'treatments': ['medications', 'diet', 'exercise']
            },
            'influenza': {
                'description': 'Viral respiratory infection',
                'incubation_period': '1-4 days',
                'treatments': ['antivirals', 'rest', 'fluids']
            }
        }

class LegalDatabaseVerifier(BaseVerifier):
    """Verifies legal claims against legal database."""
    
    def __init__(self):
        super().__init__("LegalDatabaseVerifier")
        self._legal_db = self._load_legal_db()
    
    def verify(self, claim: Claim) -> Optional[VerificationResult]:
        """Verify legal claim."""
        result = VerificationResult(
            claim=claim,
            status=ClaimStatus.UNKNOWN,
            reasoning="Legal verification in progress"
        )
        
        # Extract case names and legal references
        legal_refs = self._extract_legal_references(claim.text)
        
        for ref in legal_refs:
            if ref.lower() in self._legal_db:
                db_entry = self._legal_db[ref.lower()]
                evidence = Evidence(
                    source="Legal Database",
                    text=db_entry['summary'],
                    url=db_entry.get('url'),
                    relevance_score=0.9,
                    credibility_score=0.98
                )
                result.evidence.append(evidence)
                result.supporting_count += 1
                result.status = ClaimStatus.SUPPORTED
        
        if not result.evidence:
            result.status = ClaimStatus.UNCERTAIN
            result.uncertainty_reasons.append("No legal database entries found")
        
        result.confidence = 0.85 if result.evidence else 0.2
        return result
    
    def _extract_legal_references(self, text: str) -> List[str]:
        """Extract legal case references from text."""
        # Pattern for case names
        case_pattern = r'([A-Za-z\s]+)\s+(?:v\.|v)\s+([A-Za-z\s]+)'
        matches = re.findall(case_pattern, text)
        
        return [f"{match[0]} v {match[1]}" for match in matches]
    
    def _load_legal_db(self) -> Dict[str, Any]:
        """Load legal database."""
        return {
            'brown v board': {
                'summary': 'Landmark case ending school segregation',
                'year': 1954,
                'url': 'https://en.wikipedia.org/wiki/Brown_v._Board_of_Education'
            },
            'roe v wade': {
                'summary': 'Case regarding abortion rights',
                'year': 1973,
                'url': 'https://en.wikipedia.org/wiki/Roe_v._Wade'
            }
        }

class TechnicalKnowledgeBaseVerifier(BaseVerifier):
    """Verifies technical claims against technical knowledge base."""
    
    def __init__(self):
        super().__init__("TechnicalKnowledgeBaseVerifier")
        self._tech_kb = self._load_tech_kb()
    
    def verify(self, claim: Claim) -> Optional[VerificationResult]:
        """Verify technical claim."""
        result = VerificationResult(
            claim=claim,
            status=ClaimStatus.UNKNOWN,
            reasoning="Technical verification in progress"
        )
        
        # Extract technical terms
        tech_terms = self._extract_tech_terms(claim.text)
        
        for term in tech_terms:
            if term.lower() in self._tech_kb:
                kb_entry = self._tech_kb[term.lower()]
                evidence = Evidence(
                    source="Technical Knowledge Base",
                    text=kb_entry['description'],
                    relevance_score=0.85,
                    credibility_score=0.9
                )
                result.evidence.append(evidence)
                result.supporting_count += 1
                result.status = ClaimStatus.SUPPORTED
        
        if not result.evidence:
            result.status = ClaimStatus.UNCERTAIN
            result.uncertainty_reasons.append("No technical knowledge base entries found")
        
        result.confidence = 0.75 if result.evidence else 0.3
        return result
    
    def _extract_tech_terms(self, text: str) -> List[str]:
        """Extract technical terms from text."""
        tech_keywords = [
            'api', 'rest', 'http', 'ssl', 'encryption', 'database',
            'server', 'client', 'protocol', 'algorithm', 'data structure'
        ]
        
        terms = []
        for keyword in tech_keywords:
            if keyword.lower() in text.lower():
                terms.append(keyword)
        
        return terms
    
    def _load_tech_kb(self) -> Dict[str, Any]:
        """Load technical knowledge base."""
        return {
            'rest': {
                'description': 'Representational State Transfer - architectural style for APIs',
                'principles': ['stateless', 'cacheable', 'client-server']
            },
            'ssl': {
                'description': 'Secure Sockets Layer - cryptographic protocol',
                'uses': ['https', 'tls', 'encryption']
            },
            'database': {
                'description': 'Organized collection of structured data',
                'types': ['relational', 'nosql', 'graph']
            }
        }
