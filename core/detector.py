from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
from core.models import Claim, HallucinationReport, HallucinationType
from utils.text_processing import TextProcessor
from utils.embeddings import EmbeddingManager
from utils.logger import logger
from config.settings import settings
import re

class BaseDetector(ABC):
    """Abstract base class for hallucination detectors."""
    
    def __init__(self, name: str):
        self.name = name
        self.text_processor = TextProcessor()
        self.embedding_manager = EmbeddingManager()
    
    @abstractmethod
    def detect(self, text: str, domain: str = "general") -> List[Dict[str, Any]]:
        """Detect hallucinations in text."""
        pass

class ClaimExtractor(BaseDetector):
    """Extracts factual claims from text."""
    
    def __init__(self):
        super().__init__("ClaimExtractor")
    
    def detect(self, text: str, domain: str = "general") -> List[Claim]:
        """Extract claims from text."""
        claims = []
        sentences = self.text_processor.tokenize_sentences(text)
        
        char_offset = 0
        for sent_idx, sentence in enumerate(sentences):
            # Find sentence start position in original text
            start_pos = text.find(sentence, char_offset)
            if start_pos == -1:
                start_pos = char_offset
            
            end_pos = start_pos + len(sentence)
            
            # Extract entities and create claims
            entities = self.text_processor.extract_entities(sentence)
            all_entities = []
            for entity_list in entities.values():
                all_entities.extend(entity_list)
            
            if all_entities or self._is_factual_sentence(sentence):
                claim = Claim(
                    text=sentence.strip(),
                    sentence_index=sent_idx,
                    start_char=start_pos,
                    end_char=end_pos,
                    entities=all_entities,
                    domain=domain
                )
                claims.append(claim)
            
            char_offset = end_pos
        
        logger.info(f"Extracted {len(claims)} claims from text")
        return claims
    
    def _is_factual_sentence(self, sentence: str) -> bool:
        """Determine if sentence contains factual content."""
        # Filter out questions and imperative sentences
        if sentence.strip().endswith('?'):
            return False
        if sentence.strip().endswith('!'):
            return True  # Emphatic statements are often factual
        
        # Filter out very short sentences
        if len(sentence.split()) < 3:
            return False
        
        # Check for typical factual indicators
        factual_indicators = [
            r'\b(is|are|was|were|been)\b',
            r'\b(found|discovered|showed|proved)\b',
            r'\b(in \d{4}|on \w+ \d+)\b',  # Dates
            r'\b(\d+)\s*(million|billion|percent|%|km|miles)\b'  # Quantities
        ]
        
        return any(re.search(pattern, sentence, re.IGNORECASE) for pattern in factual_indicators)

class SemanticConsistencyDetector(BaseDetector):
    """Detects semantic inconsistencies and contradictions."""
    
    def __init__(self):
        super().__init__("SemanticConsistencyDetector")
    
    def detect(self, text: str, domain: str = "general") -> List[Dict[str, Any]]:
        """Detect semantic inconsistencies."""
        inconsistencies = []
        sentences = self.text_processor.tokenize_sentences(text)
        
        # Compare each sentence with others
        for i, sent1 in enumerate(sentences):
            for j, sent2 in enumerate(sentences[i+1:], start=i+1):
                contradiction = self._find_contradiction(sent1, sent2)
                if contradiction:
                    inconsistencies.append({
                        'type': HallucinationType.SEMANTIC_INCONSISTENCY,
                        'sentence1': sent1,
                        'sentence2': sent2,
                        'sentence1_index': i,
                        'sentence2_index': j,
                        'contradiction_score': contradiction['score'],
                        'reasoning': contradiction['reasoning']
                    })
        
        logger.info(f"Detected {len(inconsistencies)} semantic inconsistencies")
        return inconsistencies
    
    def _find_contradiction(self, sent1: str, sent2: str) -> Optional[Dict[str, Any]]:
        """Find contradictions between two sentences."""
        # Negate patterns
        negation_patterns = [
            (r'\b(is|are)\s+', r'is not '),
            (r'\b(was|were)\s+', r'was not '),
            (r'\b(can)\s+', r'cannot '),
            (r'\b(will)\s+', r'will not '),
        ]
        
        # Calculate similarity
        similarity = self.embedding_manager.similarity(sent1, sent2)
        
        # If very similar, check for negation contradictions
        if similarity > 0.8:
            for pattern, negation in negation_patterns:
                if re.search(pattern, sent1) and re.search(negation, sent2):
                    return {
                        'score': 0.95,
                        'reasoning': 'Direct negation contradiction detected'
                    }
        
        # Check for opposite entities
        entities1 = self.text_processor.extract_entities(sent1)
        entities2 = self.text_processor.extract_entities(sent2)
        
        opposites = [
            (['yes', 'true', 'positive'], ['no', 'false', 'negative']),
            (['increase', 'growth', 'rise'], ['decrease', 'decline', 'fall']),
            (['support', 'agree'], ['oppose', 'disagree'])
        ]
        
        sent1_lower = sent1.lower()
        sent2_lower = sent2.lower()
        
        for set1, set2 in opposites:
            if any(word in sent1_lower for word in set1) and any(word in sent2_lower for word in set2):
                if similarity > 0.7:  # Similar content but opposite conclusions
                    return {
                        'score': 0.85,
                        'reasoning': 'Opposite conclusions in similar statements'
                    }
        
        return None

class SelfContradictionDetector(BaseDetector):
    """Detects self-contradictions within the same text."""
    
    def __init__(self):
        super().__init__("SelfContradictionDetector")
    
    def detect(self, text: str, domain: str = "general") -> List[Dict[str, Any]]:
        """Detect self-contradictions."""
        contradictions = []
        sentences = self.text_processor.tokenize_sentences(text)
        
        # Extract claims for each sentence
        claim_extractor = ClaimExtractor()
        claims = claim_extractor.detect(text, domain)
        
        # Check for contradictory claims
        for i, claim1 in enumerate(claims):
            for claim2 in claims[i+1:]:
                if self._are_contradictory(claim1, claim2):
                    contradictions.append({
                        'type': HallucinationType.SELF_CONTRADICTION,
                        'claim1': claim1.text,
                        'claim2': claim2.text,
                        'contradiction_confidence': self._calculate_contradiction_confidence(claim1, claim2),
                        'domain': domain
                    })
        
        logger.info(f"Detected {len(contradictions)} self-contradictions")
        return contradictions
    
    def _are_contradictory(self, claim1: Claim, claim2: Claim) -> bool:
        """Check if two claims are contradictory."""
        # Check for common entities with opposite properties
        common_entities = set(claim1.entities) & set(claim2.entities)
        if not common_entities:
            return False
        
        # Check semantic similarity
        similarity = self.embedding_manager.similarity(claim1.text, claim2.text)
        if similarity < 0.6:  # Not similar enough to be contradictory
            return False
        
        # Check for negation patterns
        negation_keywords = ['not', 'no', 'never', 'neither', 'none']
        has_negation1 = any(keyword in claim1.text.lower() for keyword in negation_keywords)
        has_negation2 = any(keyword in claim2.text.lower() for keyword in negation_keywords)
        
        # One should have negation for contradiction
        return has_negation1 != has_negation2
    
    def _calculate_contradiction_confidence(self, claim1: Claim, claim2: Claim) -> float:
        """Calculate confidence that claims are contradictory."""
        # Base on similarity and entity overlap
        similarity = self.embedding_manager.similarity(claim1.text, claim2.text)
        entity_overlap = len(set(claim1.entities) & set(claim2.entities)) / max(len(claim1.entities), len(claim2.entities), 1)
        
        return (similarity * 0.6 + entity_overlap * 0.4)

class HallucinationDetector:
    """Main hallucination detector that orchestrates multiple detectors."""
    
    def __init__(self, domain: str = "general"):
        self.domain = domain
        self.claim_extractor = ClaimExtractor()
        self.semantic_detector = SemanticConsistencyDetector()
        self.contradiction_detector = SelfContradictionDetector()
        self.logger = logger
    
    def detect(self, text: str) -> HallucinationReport:
        """Detect hallucinations in text."""
        self.logger.info(f"Starting hallucination detection for domain: {self.domain}")
        
        # Extract claims
        claims = self.claim_extractor.detect(text, self.domain)
        
        # Run detectors
        semantic_issues = self.semantic_detector.detect(text, self.domain)
        contradiction_issues = self.contradiction_detector.detect(text, self.domain)
        
        # Combine results
        detected_hallucinations = semantic_issues + contradiction_issues
        
        # Create report
        report = HallucinationReport(
            original_text=text,
            claims=claims,
            detected_hallucinations=detected_hallucinations,
            domain=self.domain,
            summary=f"Detected {len(detected_hallucinations)} potential hallucinations across {len(claims)} claims"
        )
        
        self.logger.info(f"Detection complete: {report.summary}")
        return report
