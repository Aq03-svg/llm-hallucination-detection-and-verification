from typing import Dict, List, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

class ClaimStatus(str, Enum):
    """Status of a claim after verification."""
    SUPPORTED = "supported"
    CONTRADICTED = "contradicted"
    UNCERTAIN = "uncertain"
    UNKNOWN = "unknown"

class HallucinationType(str, Enum):
    """Types of hallucinations detected."""
    SEMANTIC_INCONSISTENCY = "semantic_inconsistency"
    SELF_CONTRADICTION = "self_contradiction"
    FACTUAL_ERROR = "factual_error"
    FABRICATED_ENTITY = "fabricated_entity"
    INCORRECT_RELATION = "incorrect_relation"
    OUTDATED_INFO = "outdated_info"

@dataclass
class Claim:
    """Represents a factual claim extracted from text."""
    text: str
    sentence_index: int
    start_char: int
    end_char: int
    entities: List[str] = field(default_factory=list)
    confidence: float = 0.0
    domain: str = "general"

@dataclass
class Evidence:
    """Represents evidence for or against a claim."""
    source: str  # e.g., "Wikipedia", "GitHub", "PubMed"
    text: str
    url: Optional[str] = None
    relevance_score: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    credibility_score: float = 0.8  # 0-1, higher is more credible

@dataclass
class VerificationResult:
    """Result of verifying a single claim."""
    claim: Claim
    status: ClaimStatus
    evidence: List[Evidence] = field(default_factory=list)
    confidence: float = 0.0
    reasoning: str = ""
    supporting_count: int = 0
    contradicting_count: int = 0
    uncertainty_reasons: List[str] = field(default_factory=list)

@dataclass
class HallucinationReport:
    """Complete hallucination detection and verification report."""
    original_text: str
    timestamp: datetime = field(default_factory=datetime.now)
    claims: List[Claim] = field(default_factory=list)
    verification_results: List[VerificationResult] = field(default_factory=list)
    detected_hallucinations: List[Dict[str, Any]] = field(default_factory=list)
    overall_confidence: float = 0.0
    overall_reliability_score: float = 0.0
    domain: str = "general"
    summary: str = ""
    
    def get_hallucination_count(self) -> int:
        """Count detected hallucinations."""
        return len(self.detected_hallucinations)
    
    def get_verification_summary(self) -> Dict[str, int]:
        """Get summary of verification results."""
        return {
            'supported': sum(1 for r in self.verification_results if r.status == ClaimStatus.SUPPORTED),
            'contradicted': sum(1 for r in self.verification_results if r.status == ClaimStatus.CONTRADICTED),
            'uncertain': sum(1 for r in self.verification_results if r.status == ClaimStatus.UNCERTAIN),
            'unknown': sum(1 for r in self.verification_results if r.status == ClaimStatus.UNKNOWN),
        }

from typing import Optional
