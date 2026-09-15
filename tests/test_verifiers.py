import pytest
from core.verifier import HallucinationVerifier, WikipediaVerifier
from core.models import Claim, VerificationResult, ClaimStatus, HallucinationReport

class TestWikipediaVerifier:
    """Test Wikipedia verification."""
    
    def test_verify_claim(self):
        """Test verification of a factual claim."""
        verifier = WikipediaVerifier()
        claim = Claim(
            text="Paris is the capital of France",
            sentence_index=0,
            start_char=0,
            end_char=29,
            entities=["Paris", "France"],
            domain="general"
        )
        
        result = verifier.verify(claim)
        assert result is not None
        assert result.status in [ClaimStatus.SUPPORTED, ClaimStatus.UNCERTAIN]
    
    def test_generate_search_query(self):
        """Test search query generation."""
        verifier = WikipediaVerifier()
        claim = Claim(
            text="Einstein discovered relativity",
            sentence_index=0,
            start_char=0,
            end_char=29,
            entities=["Einstein"],
            domain="general"
        )
        
        query = verifier._generate_search_query(claim)
        assert query is not None
        assert len(query) > 0
    
    def test_verify_unknown_claim(self):
        """Test verification of unknown claim."""
        verifier = WikipediaVerifier()
        claim = Claim(
            text="Xyzzy is a fictional place",
            sentence_index=0,
            start_char=0,
            end_char=27,
            entities=["Xyzzy"],
            domain="general"
        )
        
        result = verifier.verify(claim)
        assert result is not None
        # Unknown places should result in uncertain status
        assert result.status in [ClaimStatus.UNCERTAIN, ClaimStatus.UNKNOWN]

class TestHallucinationVerifier:
    """Test main verification orchestration."""
    
    def test_verify_report(self):
        """Test verification of hallucination report."""
        verifier = HallucinationVerifier()
        
        claims = [
            Claim(
                text="Paris is the capital of France",
                sentence_index=0,
                start_char=0,
                end_char=31,
                entities=["Paris"],
                domain="general"
            )
        ]
        
        report = HallucinationReport(
            original_text="Paris is the capital of France.",
            claims=claims,
            domain="general"
        )
        
        verified_report = verifier.verify(report)
        assert verified_report.verification_results is not None
    
    def test_aggregate_results(self):
        """Test aggregation of verification results."""
        verifier = HallucinationVerifier()
        
        claim = Claim(
            text="Test claim",
            sentence_index=0,
            start_char=0,
            end_char=10,
            domain="general"
        )
        
        results = [
            VerificationResult(claim=claim, status=ClaimStatus.SUPPORTED, confidence=0.9),
            VerificationResult(claim=claim, status=ClaimStatus.SUPPORTED, confidence=0.85),
        ]
        
        aggregated = verifier._aggregate_results(results)
        assert aggregated is not None
        assert aggregated.status == ClaimStatus.SUPPORTED
        assert aggregated.confidence > 0.8
    
    def test_calculate_overall_reliability(self):
        """Test overall reliability calculation."""
        verifier = HallucinationVerifier()
        
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
                VerificationResult(claim=claim, status=ClaimStatus.SUPPORTED, confidence=0.9)
            ]
        )
        
        reliability = verifier._calculate_overall_reliability(report)
        assert 0 <= reliability <= 1
