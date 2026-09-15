#!/usr/bin/env python3
"""
Full pipeline hallucination detection and verification example.
Demonstrates the complete workflow from detection to verification to scoring.
"""

from core.detector import HallucinationDetector
from core.verifier import HallucinationVerifier
from core.confidence_scorer import ConfidenceScorer
from utils.logger import logger
import json
from datetime import datetime

def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(title.center(80))
    print("=" * 80 + "\n")

def main():
    # Comprehensive example text with various types of content
    text = """
    Natural Language Processing (NLP) is a field of artificial intelligence that focuses
    on the interaction between computers and human language. NLP was invented in 2020 and
    has already revolutionized the industry.
    
    Python is a programming language created by Guido van Rossum and released in 1991.
    To work with data in Python, you can use the pandas library, which can be installed
    using: pip install pandas. The numpy library, also known as numpyy, provides numerical
    computing capabilities.
    
    Machine learning models use neural networks with 1 billion layers. Deep learning is
    considered a subset of machine learning. Both fields have the same goals and methods,
    yet they are completely different approaches.
    
    Paris is the capital of both France and Germany. The city has a population of exactly
    100 million people and is located on the Moon. The Eiffel Tower was built in 1889 and
    will be demolished next year.
    """
    
    print_section("LLM HALLUCINATION DETECTION & VERIFICATION PIPELINE")
    print(f"Analysis Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Text Length: {len(text)} characters, {len(text.split())} words")
    
    # Step 1: Detection
    print_section("STEP 1: HALLUCINATION DETECTION")
    print("Initializing detector for general domain...")
    detector = HallucinationDetector(domain="general")
    
    print("Running detection algorithms...")
    report = detector.detect(text)
    
    print(f"\nDetection Results:")
    print(f"  - Claims Extracted: {len(report.claims)}")
    print(f"  - Hallucinations Detected: {len(report.detected_hallucinations)}")
    print(f"  - Detection Summary: {report.summary}")
    
    print("\nTop Claims Identified:")
    for i, claim in enumerate(report.claims[:5], 1):
        print(f"  {i}. \"{claim.text[:60]}...\"")
        print(f"     Entities: {', '.join(claim.entities[:3]) if claim.entities else 'None'}")
    
    if report.detected_hallucinations:
        print("\nHallucinations Detected:")
        for i, hallucination in enumerate(report.detected_hallucinations[:5], 1):
            htype = hallucination.get('type')
            print(f"  {i}. Type: {htype}")
            if 'message' in hallucination:
                print(f"     {hallucination['message']}")
    
    # Step 2: Verification
    print_section("STEP 2: CLAIM VERIFICATION")
    print("Initializing verifier with multiple verification sources...")
    verifier = HallucinationVerifier()
    
    print("Running verification against multiple sources...")
    report = verifier.verify(report)
    
    print(f"\nVerification Results:")
    verification_summary = report.get_verification_summary()
    print(f"  - Total Verifications: {len(report.verification_results)}")
    print(f"  - Supported Claims: {verification_summary['supported']}")
    print(f"  - Contradicted Claims: {verification_summary['contradicted']}")
    print(f"  - Uncertain Claims: {verification_summary['uncertain']}")
    print(f"  - Unknown Claims: {verification_summary['unknown']}")
    print(f"  - Overall Reliability: {report.overall_reliability_score:.2%}")
    
    print("\nSample Verification Details:")
    for i, verification in enumerate(report.verification_results[:3], 1):
        print(f"  {i}. Claim: \"{verification.claim.text[:50]}...\"")
        print(f"     Status: {verification.status.value}")
        print(f"     Confidence: {verification.confidence:.2%}")
        print(f"     Evidence Sources: {len(verification.evidence)}")
    
    # Step 3: Confidence Scoring
    print_section("STEP 3: CONFIDENCE SCORING")
    print("Calculating confidence and reliability scores...")
    scorer = ConfidenceScorer()
    report = scorer.score(report)
    
    score_report = scorer.get_score_report(report)
    
    print(f"\nConfidence Scores:")
    print(f"  - Overall Confidence: {score_report['overall_confidence']:.2%}")
    print(f"  - Overall Reliability: {score_report['overall_reliability']:.2%}")
    print(f"  - Average Hallucination Severity: {score_report['average_hallucination_severity']:.2f}")
    
    # Step 4: Risk Assessment
    print_section("STEP 4: RISK ASSESSMENT")
    
    hallucination_count = report.get_hallucination_count()
    hallucination_rate = hallucination_count / max(len(report.claims), 1)
    
    print(f"Risk Metrics:")
    print(f"  - Total Hallucinations: {hallucination_count}")
    print(f"  - Hallucination Rate: {hallucination_rate:.2%}")
    print(f"  - Unreliable Claims: {verification_summary['contradicted']}")
    
    if hallucination_rate > 0.3:
        risk_level = "HIGH"
    elif hallucination_rate > 0.1:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"
    
    print(f"  - Overall Risk Level: {risk_level}")
    
    # Step 5: Recommendations
    print_section("STEP 5: RECOMMENDATIONS")
    
    recommendations = []
    
    if hallucination_count > 0:
        recommendations.append(f"Review and verify {hallucination_count} detected hallucinations")
    
    if verification_summary['contradicted'] > 0:
        recommendations.append(f"Investigate {verification_summary['contradicted']} contradicted claims")
    
    if score_report['overall_confidence'] < 0.6:
        recommendations.append("Consider fact-checking with authoritative sources")
    
    if score_report['average_hallucination_severity'] > 0.7:
        recommendations.append("Address high-severity hallucinations immediately")
    
    if not recommendations:
        recommendations.append("Content appears reliable - minimal issues detected")
    
    print("\nRecommendations:")
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec}")
    
    # Final Summary
    print_section("FINAL REPORT SUMMARY")
    
    print(f"Report Summary:")
    print(f"  - Domain: {report.domain}")
    print(f"  - Timestamp: {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  - Total Claims: {len(report.claims)}")
    print(f"  - Hallucinations Detected: {hallucination_count}")
    print(f"  - Verification Coverage: {len(report.verification_results)}/{len(report.claims)}")
    print(f"  - Overall Confidence: {score_report['overall_confidence']:.2%}")
    print(f"  - Overall Reliability: {score_report['overall_reliability']:.2%}")
    print(f"  - Risk Level: {risk_level}")
    
    # Export detailed report
    print("\n" + "=" * 80)
    print("Detailed JSON Report (first 500 chars):")
    print("=" * 80 + "\n")
    print(json.dumps(score_report, indent=2)[:500] + "...")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        raise
