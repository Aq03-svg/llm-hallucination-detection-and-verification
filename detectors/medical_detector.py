from typing import List, Dict, Any
from core.detector import BaseDetector
from core.models import HallucinationType
from utils.logger import logger
import re

class MedicalTerminologyChecker(BaseDetector):
    """Checks validity of medical terminology."""
    
    def __init__(self):
        super().__init__("MedicalTerminologyChecker")
        self._valid_terms = self._load_medical_terms()
    
    def detect(self, text: str, domain: str = "medical") -> List[Dict[str, Any]]:
        """Check medical terminology validity."""
        issues = []
        
        # Extract medical terms and concepts
        medical_patterns = [
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:syndrome|disease|disorder)\b',
            r'\b(?:type|stage)\s+([0-9IVX]+)\b',
            r'\b([A-Z]{2,})\b(?:\s+deficiency|\s+disorder)',
        ]
        
        for pattern in medical_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                term = match.group(1) if match.lastindex else match.group(0)
                # Verify term exists in medical knowledge base
                if not self._is_valid_medical_term(term):
                    issues.append({
                        'type': HallucinationType.FABRICATED_ENTITY,
                        'term': term,
                        'message': f"Potentially non-existent medical term: '{term}'",
                        'severity': 'high'
                    })
        
        logger.info(f"Medical terminology check: {len(issues)} issues found")
        return issues
    
    def _load_medical_terms(self) -> set:
        """Load valid medical terms."""
        # Simplified set of common medical terms
        return {
            'diabetes', 'hypertension', 'pneumonia', 'influenza',
            'alzheimers', 'parkinsons', 'schizophrenia', 'depression',
            'cancer', 'cardiovascular', 'pulmonary', 'hepatic',
            'stroke', 'myocardial infarction', 'heart failure'
        }
    
    def _is_valid_medical_term(self, term: str) -> bool:
        """Check if term is valid medical terminology."""
        term_lower = term.lower()
        return term_lower in self._valid_terms or len(term_lower) > 3

class DrugInteractionChecker(BaseDetector):
    """Checks for drug interaction validity."""
    
    def __init__(self):
        super().__init__("DrugInteractionChecker")
        self._known_drugs = self._load_known_drugs()
    
    def detect(self, text: str, domain: str = "medical") -> List[Dict[str, Any]]:
        """Check for drug interactions."""
        issues = []
        
        # Extract drug names
        drug_pattern = r'(?:taking|using|administering|prescribing)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        matches = re.findall(drug_pattern, text)
        
        for drug in matches:
            if drug.lower() not in self._known_drugs:
                issues.append({
                    'type': HallucinationType.FACTUAL_ERROR,
                    'drug': drug,
                    'message': f"Drug '{drug}' not found in known drugs database",
                    'severity': 'high'
                })
        
        # Check for impossible combinations
        if 'contraindicated' in text.lower() or 'never combine' in text.lower():
            # These statements are risky - require verification
            issues.append({
                'type': HallucinationType.UNCERTAIN,
                'message': "Drug interaction claims require medical verification",
                'severity': 'critical'
            })
        
        logger.info(f"Drug interaction check: {len(issues)} issues found")
        return issues
    
    def _load_known_drugs(self) -> set:
        """Load known drug names."""
        # Simplified set of common drugs
        return {
            'aspirin', 'ibuprofen', 'acetaminophen', 'metformin',
            'lisinopril', 'atorvastatin', 'amoxicillin', 'omeprazole',
            'sertraline', 'fluoxetine', 'loratadine', 'diphenhydramine'
        }

class ProcedureAccuracyChecker(BaseDetector):
    """Checks accuracy of medical procedures described."""
    
    def __init__(self):
        super().__init__("ProcedureAccuracyChecker")
    
    def detect(self, text: str, domain: str = "medical") -> List[Dict[str, Any]]:
        """Check medical procedure accuracy."""
        issues = []
        
        # Check for impossible procedures
        impossible_procedures = [
            (r'remove.*brain', 'Cannot remove entire brain'),
            (r'transplant.*heart.*without.*blood', 'Heart transplant requires blood circulation'),
            (r'surgery.*without.*anesthesia.*patient.*awake', 'Most surgeries require anesthesia'),
        ]
        
        for pattern, message in impossible_procedures:
            if re.search(pattern, text, re.IGNORECASE):
                issues.append({
                    'type': HallucinationType.FACTUAL_ERROR,
                    'message': message,
                    'severity': 'critical'
                })
        
        # Check for outdated procedures
        outdated_patterns = [
            (r'bloodletting.*cure', 'Bloodletting is no longer standard medical practice'),
            (r'lobotomy.*standard.*treatment', 'Lobotomy is not standard treatment'),
        ]
        
        for pattern, message in outdated_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                issues.append({
                    'type': HallucinationType.OUTDATED_INFO,
                    'message': message,
                    'severity': 'high'
                })
        
        logger.info(f"Procedure accuracy check: {len(issues)} issues found")
        return issues
