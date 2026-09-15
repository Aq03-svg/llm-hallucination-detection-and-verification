import pytest
from core.detector import (
    HallucinationDetector,
    ClaimExtractor,
    SemanticConsistencyDetector,
    SelfContradictionDetector
)
from core.models import Claim, HallucinationType

class TestClaimExtractor:
    """Test claim extraction functionality."""
    
    def test_extract_simple_claims(self):
        """Test extraction of simple factual claims."""
        extractor = ClaimExtractor()
        text = "Paris is the capital of France. It has a population of 2 million."
        claims = extractor.detect(text)
        
        assert len(claims) > 0
        assert any('Paris' in claim.text for claim in claims)
        assert any('capital' in claim.text for claim in claims)
    
    def test_extract_entities(self):
        """Test entity extraction from claims."""
        extractor = ClaimExtractor()
        text = "Albert Einstein was born on March 14, 1879 in Germany."
        claims = extractor.detect(text)
        
        assert len(claims) > 0
        assert claims[0].entities  # Should have entities
    
    def test_filter_questions(self):
        """Test that questions are not extracted as factual claims."""
        extractor = ClaimExtractor()
        text = "What is the capital of France? Paris is the answer."
        claims = extractor.detect(text)
        
        # Should extract the factual claim but not the question
        claim_texts = [c.text for c in claims]
        assert not any('?' in text for text in claim_texts)

class TestSemanticConsistencyDetector:
    """Test semantic consistency detection."""
    
    def test_detect_contradiction(self):
        """Test detection of semantic contradictions."""
        detector = SemanticConsistencyDetector()
        text = "Paris is in France. Paris is not in France."
        inconsistencies = detector.detect(text)
        
        assert len(inconsistencies) > 0
        assert any(inc['type'] == HallucinationType.SEMANTIC_INCONSISTENCY for inc in inconsistencies)
    
    def test_similar_non_contradictory_sentences(self):
        """Test that similar but non-contradictory sentences are not flagged."""
        detector = SemanticConsistencyDetector()
        text = "Paris is beautiful. Paris is a great city."
        inconsistencies = detector.detect(text)
        
        # Should not detect contradiction for synonymous statements
        contradictions = [i for i in inconsistencies if 'contradiction' in str(i.get('type', '')).lower()]
        assert len(contradictions) == 0 or len(contradictions) < 1

class TestSelfContradictionDetector:
    """Test self-contradiction detection."""
    
    def test_detect_self_contradiction(self):
        """Test detection of self-contradictions."""
        detector = SelfContradictionDetector()
        text = "France is not in Europe. France is located in Europe."
        contradictions = detector.detect(text)
        
        assert len(contradictions) > 0
        assert contradictions[0]['type'] == HallucinationType.SELF_CONTRADICTION
    
    def test_consistent_statements(self):
        """Test that consistent statements are not flagged."""
        detector = SelfContradictionDetector()
        text = "France is in Europe. France is a European country. The capital of France is Paris."
        contradictions = detector.detect(text)
        
        assert len(contradictions) == 0

class TestHallucinationDetector:
    """Test main hallucination detector."""
    
    def test_detect_hallucinations(self):
        """Test detection of hallucinations."""
        detector = HallucinationDetector(domain="general")
        text = "The capital of France is Paris. Paris is located in Germany. The Eiffel Tower is in France."
        report = detector.detect(text)
        
        assert report.claims
        assert len(report.detected_hallucinations) > 0
    
    def test_domain_setting(self):
        """Test that domain is correctly set."""
        detector = HallucinationDetector(domain="medical")
        text = "Aspirin is used to treat headaches."
        report = detector.detect(text)
        
        assert report.domain == "medical"
    
    def test_report_generation(self):
        """Test that report is generated correctly."""
        detector = HallucinationDetector()
        text = "Test text with claims."
        report = detector.detect(text)
        
        assert report.original_text == text
        assert report.claims is not None
        assert report.detected_hallucinations is not None
