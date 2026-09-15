#!/usr/bin/env python3
"""
Basic hallucination detection example.
"""

from core.detector import HallucinationDetector
from core.verifier import HallucinationVerifier
from core.confidence_scorer import ConfidenceScorer
import json

def main():
    # Example text with potential hallucinations
    text = """
    Paris is the capital of France and is located in Germany.
    The Eiffel Tower was built in 1889 and is the most visited monument in the world.
    France has a population of approximately 67 million people.
    The capital of France was founded in the year 2000.
    """
    
    print("=" * 80)
    print("BASIC HALLUCINATION DETECTION EXAMPLE")
    print("=" * 80)
    print(f"\nAnalyzing text:\n{text}\n")
    
    # Initialize components
    detector = HallucinationDetector(domain="general")
    verifier = HallucinationVerifier()
    scorer = ConfidenceScorer()
    
    # Detect hallucinations
    print("Step 1: Detecting hallucinations...")
    report = detector.detect(text)
    print(f"  - Found {len(report.claims)} claims")
    print(f"  - Detected {len(report.detected_hallucinations)} potential hallucinations")
    
    # Verify claims
    print("\nStep 2: Verifying claims...")
    report = verifier.verify(report)
    print(f"  - Verified {len(report.verification_results)} claims")
    verification_summary = report.get_verification_summary()
    print(f"  - Summary: {verification_summary}")
    
    # Score confidence
    print("\nStep 3: Scoring confidence...")
    report = scorer.score(report)
    score_report = scorer.get_score_report(report)
    print(f"  - Overall confidence: {score_report['overall_confidence']:.2f}")
    print(f"  - Overall reliability: {score_report['overall_reliability']:.2f}")
    
    # Display results
    print("\n" + "=" * 80)
    print("RESULTS")
    print("=" * 80)
    
    print("\nDetected Hallucinations:")
    for i, hallucination in enumerate(report.detected_hallucinations, 1):
        print(f"  {i}. {hallucination.get('type')}")
        if 'message' in hallucination:
            print(f"     Message: {hallucination['message']}")
        if 'severity' in hallucination:
            print(f"     Severity: {hallucination['severity']}")
    
    print("\nVerification Summary:")
    for status, count in verification_summary.items():
        print(f"  {status.capitalize()}: {count}")
    
    print("\nConfidence Scores:")
    print(json.dumps(score_report, indent=2))

if __name__ == "__main__":
    main()
