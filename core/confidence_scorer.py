from typing import List, Dict, Any
from core.models import HallucinationReport, VerificationResult, ClaimStatus
from utils.logger import logger
import numpy as np

class ConfidenceScorer:
    """Calculates confidence and reliability scores for hallucination detection."""
    
    def __init__(self):
        self.logger = logger
    
    def score(self, report: HallucinationReport) -> HallucinationReport:
        """Score the hallucination detection report."""
        self.logger.info("Starting confidence scoring")
        
        # Calculate claim-level confidence
        for claim in report.claims:
            claim.confidence = self._score_claim_confidence(claim)
        
        # Calculate verification-level confidence
        for verification in report.verification_results:
            verification.confidence = self._score_verification_confidence(verification)
        
        # Calculate overall confidence
        report.overall_confidence = self._calculate_overall_confidence(report)
        
        # Calculate hallucination severity scores
        for hallucination in report.detected_hallucinations:
            hallucination['severity_score'] = self._score_hallucination_severity(hallucination, report)
        
        self.logger.info(f"Confidence scoring complete: {report.overall_confidence:.2f}")
        return report
    
    def _score_claim_confidence(self, claim) -> float:
        """Score confidence for a single claim."""
        # Factors: specificity, entity count, clarity
        words = claim.text.split()
        word_count = len(words)
        entity_count = len(claim.entities)
        
        # Base confidence from specificity
        specificity = entity_count / max(word_count, 1)
        specificity_confidence = min(specificity * 1.5, 1.0)  # Scale and cap
        
        # Confidence from word count (avoid very short claims)
        if word_count < 3:
            length_confidence = 0.3
        elif word_count > 30:
            length_confidence = 0.6  # Long claims are less clear
        else:
            length_confidence = 0.8
        
        # Combined confidence
        confidence = (specificity_confidence * 0.6 + length_confidence * 0.4)
        return min(1.0, max(0.0, confidence))
    
    def _score_verification_confidence(self, verification: VerificationResult) -> float:
        """Score confidence for verification result."""
        # Factors: evidence count, evidence quality, status agreement
        if not verification.evidence:
            return 0.3  # Low confidence with no evidence
        
        # Evidence quality score
        evidence_quality = np.mean([e.relevance_score * e.credibility_score for e in verification.evidence])
        
        # Evidence count factor
        evidence_factor = min(len(verification.evidence) / 3.0, 1.0)  # Up to 3 sources gives full score
        
        # Status-based adjustment
        status_multiplier = {
            ClaimStatus.SUPPORTED: 1.0,
            ClaimStatus.CONTRADICTED: 0.9,
            ClaimStatus.UNCERTAIN: 0.6,
            ClaimStatus.UNKNOWN: 0.4
        }.get(verification.status, 0.5)
        
        confidence = (evidence_quality * 0.5 + evidence_factor * 0.3 + status_multiplier * 0.2)
        return min(1.0, max(0.0, confidence))
    
    def _calculate_overall_confidence(self, report: HallucinationReport) -> float:
        """Calculate overall confidence in the report."""
        if not report.verification_results:
            return 0.5
        
        # Average of all verification confidences
        avg_verification_confidence = np.mean([v.confidence for v in report.verification_results])
        
        # Factor in hallucination count (fewer hallucinations = more confident)
        hallucination_factor = 1.0 - (len(report.detected_hallucinations) / max(len(report.claims), 1) * 0.5)
        hallucination_factor = max(0.3, hallucination_factor)
        
        overall = (avg_verification_confidence * 0.7 + hallucination_factor * 0.3)
        return min(1.0, max(0.0, overall))
    
    def _score_hallucination_severity(self, hallucination: Dict[str, Any], report: HallucinationReport) -> float:
        """Score the severity of a detected hallucination."""
        severity = 0.5  # Base severity
        
        # Type-based severity
        type_severity = {
            'self_contradiction': 0.8,
            'semantic_inconsistency': 0.6,
            'factual_error': 0.9,
            'fabricated_entity': 0.95,
            'incorrect_relation': 0.7,
            'outdated_info': 0.5
        }
        
        hallucination_type = hallucination.get('type', 'unknown')
        severity = type_severity.get(hallucination_type.value if hasattr(hallucination_type, 'value') else hallucination_type, 0.5)
        
        # Adjust by contradiction score if available
        if 'contradiction_score' in hallucination:
            severity = (severity * 0.6 + hallucination['contradiction_score'] * 0.4)
        
        return min(1.0, max(0.0, severity))
    
    def get_score_report(self, report: HallucinationReport) -> Dict[str, Any]:
        """Generate a comprehensive score report."""
        return {
            'overall_confidence': report.overall_confidence,
            'overall_reliability': report.overall_reliability_score,
            'total_claims': len(report.claims),
            'total_hallucinations': len(report.detected_hallucinations),
            'verification_summary': report.get_verification_summary(),
            'hallucination_severity_scores': [
                h.get('severity_score', 0.0) for h in report.detected_hallucinations
            ],
            'average_hallucination_severity': np.mean([h.get('severity_score', 0.0) for h in report.detected_hallucinations]) if report.detected_hallucinations else 0.0
        }
