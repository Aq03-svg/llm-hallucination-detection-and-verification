#!/usr/bin/env python3
"""
Medical domain hallucination detection example.
"""

from core.detector import HallucinationDetector
from core.verifier import HallucinationVerifier
from detectors.medical_detector import (
    MedicalTerminologyChecker,
    DrugInteractionChecker,
    ProcedureAccuracyChecker
)
from verifiers.knowledge_base_verifier import MedicalKnowledgeBaseVerifier
from core.confidence_scorer import ConfidenceScorer

def main():
    # Example medical text
    text = """
    Type 2 diabetes can be managed with metformin and lifestyle modifications.
    Patients should never combine insulin with grapefruit juice as it causes severe reactions.
    Hypertension is typically treated with ACE inhibitors or beta-blockers.
    A complete brain removal surgery has shown positive outcomes in clinical trials.
    """
    
    print("=" * 80)
    print("MEDICAL HALLUCINATION DETECTION EXAMPLE")
    print("=" * 80)
    print(f"\nAnalyzing medical text:\n{text}\n")
    
    # Initialize medical-specific detectors
    print("Step 1: Running medical-specific detectors...")
    terminology_checker = MedicalTerminologyChecker()
    drug_checker = DrugInteractionChecker()
    procedure_checker = ProcedureAccuracyChecker()
    
    terminology_issues = terminology_checker.detect(text, domain="medical")
    drug_issues = drug_checker.detect(text, domain="medical")
    procedure_issues = procedure_checker.detect(text, domain="medical")
    
    print(f"  - Terminology issues: {len(terminology_issues)}")
    print(f"  - Drug interaction issues: {len(drug_issues)}")
    print(f"  - Procedure accuracy issues: {len(procedure_issues)}")
    
    # Run general detection
    print("\nStep 2: Running general hallucination detection...")
    detector = HallucinationDetector(domain="medical")
    report = detector.detect(text)
    print(f"  - Found {len(report.claims)} claims")
    print(f"  - Detected {len(report.detected_hallucinations)} potential hallucinations")
    
    # Verify with medical knowledge base
    print("\nStep 3: Verifying against medical knowledge base...")
    medical_verifier = MedicalKnowledgeBaseVerifier()
    for claim in report.claims:
        result = medical_verifier.verify(claim)
        if result:
            report.verification_results.append(result)
    
    print(f"  - Verified {len(report.verification_results)} claims")
    
    # Score confidence
    print("\nStep 4: Scoring confidence...")
    scorer = ConfidenceScorer()
    report = scorer.score(report)
    
    # Display results
    print("\n" + "=" * 80)
    print("RESULTS")
    print("=" * 80)
    
    print("\nCritical Issues Found:")
    for issues, label in [
        (terminology_issues, "Terminology"),
        (drug_issues, "Drug Interactions"),
        (procedure_issues, "Procedure Accuracy")
    ]:
        if issues:
            print(f"\n  {label}:")
            for issue in issues:
                print(f"    - {issue.get('message', issue)}")
                print(f"      Severity: {issue.get('severity', 'unknown')}")
    
    print(f"\nOverall Reliability Score: {report.overall_reliability_score:.2%}")
    print(f"Overall Confidence Score: {report.overall_confidence:.2%}")

if __name__ == "__main__":
    main()
