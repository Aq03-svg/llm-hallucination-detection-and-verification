import pytest
from core.detector import HallucinationDetector
from core.verifier import HallucinationVerifier
from core.confidence_scorer import ConfidenceScorer
from core.models import ClaimStatus

class TestEndToEndPipeline:
    """Integration tests for the complete pipeline."""
    
    def test_simple_detection_verification_pipeline(self):
        """Test complete pipeline from detection to scoring."""
        text = "Paris is the capital of France and is located in Germany."
        
        # Detection
        detector = HallucinationDetector(domain="general")
        report = detector.detect(text)
        assert report.claims
        
        # Verification
        verifier = HallucinationVerifier()
        report = verifier.verify(report)
        assert report.verification_results is not None
        
        # Scoring
        scorer = ConfidenceScorer()
        report = scorer.score(report)
        assert report.overall_confidence is not None
    
    def test_pipeline_with_medical_domain(self):
        """Test pipeline with medical domain."""
        text = "Type 2 diabetes can be treated with metformin. Hypertension is managed with ACE inhibitors."
        
        detector = HallucinationDetector(domain="medical")
        report = detector.detect(text)
        assert report.domain == "medical"
        assert report.claims
        
        verifier = HallucinationVerifier()
        report = verifier.verify(report)
        
        scorer = ConfidenceScorer()
        report = scorer.score(report)
        assert 0 <= report.overall_confidence <= 1
    
    def test_pipeline_with_code_domain(self):
        """Test pipeline with code domain."""
        text = """Here's Python code:
        ```python
        import pandas as pd
        df = pd.DataFrame(data)
        result = df.apply(lambda x: x*2)
        ```
        """
        
        detector = HallucinationDetector(domain="code")
        report = detector.detect(text)
        assert report.domain == "code"
        
        verifier = HallucinationVerifier()
        report = verifier.verify(report)
        
        scorer = ConfidenceScorer()
        report = scorer.score(report)
        assert report.overall_reliability_score is not None
    
    def test_pipeline_with_multiple_hallucinations(self):
        """Test pipeline with text containing multiple hallucinations."""
        text = """
        Einstein invented the light bulb in 2010.
        The Earth is flat and located in space.
        Water boils at 200 degrees Celsius.
        Gravity pulls objects downward and upward simultaneously.
        """
        
        detector = HallucinationDetector(domain="general")
        report = detector.detect(text)
        
        assert len(report.claims) > 0
        assert len(report.detected_hallucinations) > 0
        
        verifier = HallucinationVerifier()
        report = verifier.verify(report)
        
        scorer = ConfidenceScorer()
        report = scorer.score(report)
        
        # Should have low overall confidence
        assert report.overall_confidence < 0.7
    
    def test_pipeline_with_reliable_text(self):
        """Test pipeline with mostly reliable text."""
        text = """
        The Earth orbits the Sun.
        Water freezes at 0 degrees Celsius.
        Photosynthesis is the process by which plants convert sunlight into chemical energy.
        The human heart pumps blood throughout the body.
        """
        
        detector = HallucinationDetector(domain="general")
        report = detector.detect(text)
        
        verifier = HallucinationVerifier()
        report = verifier.verify(report)
        
        scorer = ConfidenceScorer()
        report = scorer.score(report)
        
        # Should have higher overall confidence
        assert report.overall_confidence > 0.5
    
    def test_report_completeness(self):
        """Test that final report contains all required information."""
        text = "Paris is the capital of France."
        
        detector = HallucinationDetector(domain="general")
        report = detector.detect(text)
        
        verifier = HallucinationVerifier()
        report = verifier.verify(report)
        
        scorer = ConfidenceScorer()
        report = scorer.score(report)
        
        # Verify report structure
        assert report.original_text == text
        assert report.claims is not None
        assert report.verification_results is not None
        assert report.detected_hallucinations is not None
        assert report.overall_confidence is not None
        assert report.overall_reliability_score is not None
        assert report.domain == "general"
