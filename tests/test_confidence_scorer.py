import pytest
from core.confidence_scorer import ConfidenceScorer
from core.models import (
    Claim, HallucinationReport, VerificationResult, ClaimStatus,
    Evidence, HallucinationType
)

class TestConfidenceScorer:
    """Test confidence scoring functionality."""
    
    def test_score_claim_confidence(self):
        """Test claim confidence scoring."""
        scorer = ConfidenceScorer()
        
        claim = Claim(
            text="Paris, the capital of France, is located in Europe.",
            sentence_index=0,
            start_char=0,
            end_char=54,
            entities=["Paris", "France", "Europe"],
            domain="general"
        )
        
        confidence = scorer._score_claim_confidence(claim)
        assert 0 <= confidence <= 1
        assert confidence > 0.5  # Should be reasonably confident
    
    def test_score_short_claim(self):
        """Test scoring of short claims with low confidence."""
        scorer = ConfidenceScorer()
        
        short_claim = Claim(
            text="Paris is big.",
            sentence_index=0,
            start_char=0,
            end_char=13,
            entities=[],
            domain="general"
        )
        
        confidence = scorer._score_claim_confidence(short_claim)
        assert confidence < 0.5  # Short claims should have lower confidence
    
    def test_score_verification_confidence(self):
        """Test verification result confidence scoring."""
        scorer = ConfidenceScorer()
        
        claim = Claim(
            text="Test claim",
            sentence_index=0,
            start_char=0,
            end_char=10,
            domain="general"
        )
        
        evidence = Evidence(
            source="Wikipedia",
            text="Supporting evidence",
            relevance_score=0.9,
            credibility_score=0.95
        )
        
        verification = VerificationResult(
            claim=claim,
            status=ClaimStatus.SUPPORTED,
            evidence=[evidence],
            confidence=0.85
        )
        
        score = scorer._score_verification_confidence(verification)
        assert 0 <= score <= 1
        assert score > 0.7  # Should be confident with good evidence
    
    def test_score_no_evidence(self):
        """Test confidence scoring with no evidence."""
        scorer = ConfidenceScorer()
        
        claim = Claim(
            text="Test claim",
            sentence_index=0,
            start_char=0,
            end_char=10,
            domain="general"
        )
        
        verification = VerificationResult(
            claim=claim,
            status=ClaimStatus.UNKNOWN,
            evidence=[],
            confidence=0
        )
        
        score = scorer._score_verification_confidence(verification)
        assert score < 0.5  # Low confidence with no evidence
    
    def test_score_hallucination_severity(self):
        """Test hallucination severity scoring."""
        scorer = ConfidenceScorer()
        
        hallucination = {
            'type': HallucinationType.SELF_CONTRADICTION,
            'message': 'Contradictory statement detected'
        }
        
        report = HallucinationReport(original_text="Test")
        severity = scorer._score_hallucination_severity(hallucination, report)
        
        assert 0 <= severity <= 1
        assert severity > 0.5  # Self-contradictions should be moderate to high severity
    
    def test_calculate_overall_confidence(self):
        """Test overall confidence calculation."""
        scorer = ConfidenceScorer()
        
        claim = Claim(
            text="Test claim",
            sentence_index=0,
            start_char=0,
            end_char=10,
            domain="general"
        )
        
        report = HallucinationReport(
            original_text="Test",
            claims=[claim],
            verification_results=[
                VerificationResult(
                    claim=claim,
                    status=ClaimStatus.SUPPORTED,
                    confidence=0.9
                )
            ]
        )
        
        overall = scorer._calculate_overall_confidence(report)
        assert 0 <= overall <= 1
    
    def test_score_report(self):
        """Test complete report scoring."""
        scorer = ConfidenceScorer()
        
        claim = Claim(
            text="Paris is the capital of France.",
            sentence_index=0,
            start_char=0,
            end_char=31,
            entities=["Paris", "France"],
            domain="general"
        )
        
        report = HallucinationReport(
            original_text="Paris is the capital of France.",
            claims=[claim]
        )
        
        scored_report = scorer.score(report)
        assert scored_report.overall_confidence is not None
        assert 0 <= scored_report.overall_confidence <= 1
    
    def test_get_score_report(self):
        """Test score report generation."""
        scorer = ConfidenceScorer()
        
        claim = Claim(
            text="Test",
            sentence_index=0,
            start_char=0,
            end_char=4,
            domain="general"
        )
        
        report = HallucinationReport(
            original_text="Test",
            claims=[claim],
            verification_results=[]
        )
        
        score_report = scorer.get_score_report(report)
        assert 'overall_confidence' in score_report
        assert 'overall_reliability' in score_report
        assert 'total_claims' in score_report
        assert 'total_hallucinations' in score_report
