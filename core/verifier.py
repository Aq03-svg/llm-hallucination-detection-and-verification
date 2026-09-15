from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
from datetime import datetime
from core.models import (
    Claim, VerificationResult, Evidence, ClaimStatus, HallucinationReport
)
from utils.api_utils import WikipediaAPI, GitHubAPI, APIClient
from utils.embeddings import EmbeddingManager
from utils.text_processing import TextProcessor
from utils.logger import logger
from config.settings import settings
import re

class BaseVerifier(ABC):
    """Abstract base class for claim verifiers."""
    
    def __init__(self, name: str):
        self.name = name
        self.embedding_manager = EmbeddingManager()
        self.text_processor = TextProcessor()
    
    @abstractmethod
    def verify(self, claim: Claim) -> Optional[VerificationResult]:
        """Verify a single claim."""
        pass
    
    def _calculate_credibility_score(self, source: str) -> float:
        """Calculate credibility score based on source."""
        credibility_map = {
            'Wikipedia': 0.85,
            'GitHub': 0.9,
            'PubMed': 0.95,
            'Official Documentation': 0.95,
            'News Article': 0.7,
            'Social Media': 0.3
        }
        return credibility_map.get(source, 0.5)

class SemanticVerifier(BaseVerifier):
    """Verifies claims using semantic analysis."""
    
    def __init__(self):
        super().__init__("SemanticVerifier")
    
    def verify(self, claim: Claim) -> Optional[VerificationResult]:
        """Verify claim semantically."""
        result = VerificationResult(
            claim=claim,
            status=ClaimStatus.UNCERTAIN,
            reasoning="Semantic verification completed"
        )
        
        # Analyze claim complexity and specificity
        words = self.text_processor.tokenize_words(claim.text)
        specificity_score = len(claim.entities) / max(len(words), 1)
        
        if specificity_score > 0.5:
            result.confidence = 0.7
        else:
            result.confidence = 0.5
        
        return result

class WikipediaVerifier(BaseVerifier):
    """Verifies claims against Wikipedia content."""
    
    def __init__(self):
        super().__init__("WikipediaVerifier")
    
    def verify(self, claim: Claim) -> Optional[VerificationResult]:
        """Verify claim using Wikipedia."""
        if not settings.ENABLE_WIKIPEDIA_VERIFICATION:
            return None
        
        result = VerificationResult(
            claim=claim,
            status=ClaimStatus.UNKNOWN,
            reasoning="No Wikipedia sources found"
        )
        
        # Search for relevant Wikipedia articles
        search_query = self._generate_search_query(claim)
        search_results = WikipediaAPI.search(search_query, limit=5)
        
        if not search_results:
            logger.warning(f"No Wikipedia results for: {claim.text}")
            return result
        
        # Get content from top results
        for search_result in search_results[:3]:
            title = search_result.get('title', '')
            content = WikipediaAPI.get_content(title)
            
            if not content:
                continue
            
            # Check if claim is supported by content
            similarity = self.embedding_manager.similarity(claim.text, content[:500])
            
            if similarity > settings.SEMANTIC_SIMILARITY_THRESHOLD:
                evidence = Evidence(
                    source="Wikipedia",
                    text=content[:500],
                    url=f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}",
                    relevance_score=similarity,
                    credibility_score=self._calculate_credibility_score("Wikipedia")
                )
                result.evidence.append(evidence)
                result.supporting_count += 1
                result.status = ClaimStatus.SUPPORTED
                result.confidence = similarity
        
        if not result.evidence:
            result.status = ClaimStatus.UNCERTAIN
            result.uncertainty_reasons.append("No strong Wikipedia evidence found")
        
        return result
    
    def _generate_search_query(self, claim: Claim) -> str:
        """Generate search query from claim."""
        # Use entities or important keywords
        if claim.entities:
            return claim.entities[0]
        
        # Otherwise use first few words
        words = claim.text.split()[:5]
        return ' '.join(words)

class GitHubVerifier(BaseVerifier):
    """Verifies code-related claims using GitHub API."""
    
    def __init__(self):
        super().__init__("GitHubVerifier")
    
    def verify(self, claim: Claim) -> Optional[VerificationResult]:
        """Verify code-related claims."""
        if not settings.ENABLE_API_VERIFICATION or claim.domain != "code":
            return None
        
        result = VerificationResult(
            claim=claim,
            status=ClaimStatus.UNKNOWN,
            reasoning="Code verification completed"
        )
        
        # Extract potential library/repo names
        library_patterns = [
            r'\b([a-zA-Z0-9_-]+)\s+library\b',
            r'\b(pip install|npm install)\s+([a-zA-Z0-9_-]+)\b',
            r'\b(from|import)\s+([a-zA-Z0-9_-]+)\b'
        ]
        
        for pattern in library_patterns:
            matches = re.findall(pattern, claim.text, re.IGNORECASE)
            if matches:
                for match in matches:
                    library_name = match if isinstance(match, str) else match[-1]
                    repos = GitHubAPI.search_repositories(library_name, limit=5)
                    
                    if repos:
                        for repo in repos:
                            evidence = Evidence(
                                source="GitHub",
                                text=repo.get('description', 'No description'),
                                url=repo.get('html_url'),
                                relevance_score=0.8,
                                credibility_score=self._calculate_credibility_score("GitHub")
                            )
                            result.evidence.append(evidence)
                            result.supporting_count += 1
                            result.status = ClaimStatus.SUPPORTED
        
        if not result.evidence:
            result.status = ClaimStatus.UNCERTAIN
            result.uncertainty_reasons.append("No GitHub repositories found")
        
        return result

class HallucinationVerifier:
    """Main verifier that orchestrates multiple verification strategies."""
    
    def __init__(self):
        self.verifiers = [
            WikipediaVerifier(),
            GitHubVerifier(),
            SemanticVerifier()
        ]
        self.logger = logger
    
    def verify(self, report: HallucinationReport) -> HallucinationReport:
        """Verify all claims in a hallucination report."""
        self.logger.info(f"Starting verification for {len(report.claims)} claims")
        
        for claim in report.claims:
            verification_results = []
            
            # Run all verifiers
            for verifier in self.verifiers:
                try:
                    result = verifier.verify(claim)
                    if result:
                        verification_results.append(result)
                except Exception as e:
                    self.logger.error(f"Verifier {verifier.name} failed: {e}")
            
            # Aggregate results
            if verification_results:
                aggregated = self._aggregate_results(verification_results)
                report.verification_results.append(aggregated)
        
        # Calculate overall scores
        report.overall_reliability_score = self._calculate_overall_reliability(report)
        
        self.logger.info(f"Verification complete: {len(report.verification_results)} results")
        return report
    
    def _aggregate_results(self, results: List[VerificationResult]) -> VerificationResult:
        """Aggregate verification results from multiple verifiers."""
        if not results:
            return results[0]
        
        # Use first result as base
        aggregated = results[0]
        
        # Combine evidence
        for result in results[1:]:
            aggregated.evidence.extend(result.evidence)
            aggregated.supporting_count += result.supporting_count
            aggregated.contradicting_count += result.contradicting_count
        
        # Recalculate status and confidence
        if aggregated.supporting_count > aggregated.contradicting_count:
            aggregated.status = ClaimStatus.SUPPORTED
        elif aggregated.contradicting_count > aggregated.supporting_count:
            aggregated.status = ClaimStatus.CONTRADICTED
        else:
            aggregated.status = ClaimStatus.UNCERTAIN
        
        # Calculate average confidence
        aggregated.confidence = sum(r.confidence for r in results) / len(results)
        
        return aggregated
    
    def _calculate_overall_reliability(self, report: HallucinationReport) -> float:
        """Calculate overall reliability score for the text."""
        if not report.verification_results:
            return 0.5  # Default neutral score
        
        supported_count = sum(1 for r in report.verification_results if r.status == ClaimStatus.SUPPORTED)
        contradicted_count = sum(1 for r in report.verification_results if r.status == ClaimStatus.CONTRADICTED)
        total = len(report.verification_results)
        
        # Calculate score: higher for more supported claims, lower for contradictions
        reliability = (supported_count - contradicted_count) / max(total, 1)
        reliability = (reliability + 1) / 2  # Normalize to 0-1 range
        
        return max(0.0, min(1.0, reliability))
