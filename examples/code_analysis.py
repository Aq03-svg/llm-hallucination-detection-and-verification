#!/usr/bin/env python3
"""
Code hallucination detection example.
"""

from core.detector import HallucinationDetector
from detectors.code_detector import (
    CodeSyntaxDetector,
    LibraryExistenceChecker,
    APICorrectnessChecker
)
from core.confidence_scorer import ConfidenceScorer

def main():
    # Example code with issues
    code_text = """
    Here's how to use pandas:
    
    ```python
    import pandas as pd
    import numpyy  # This library doesn't exist
    
    df = pd.DataFrame(data)
    result = df.map()  # This method doesn't exist
    
    import requests
    response = requests.fetch('http://api.example.com')  # Wrong method name
    ```
    
    The popular numpy library can be installed with:
    ```
    pip install numpyy
    ```
    """
    
    print("=" * 80)
    print("CODE HALLUCINATION DETECTION EXAMPLE")
    print("=" * 80)
    print(f"\nAnalyzing code:\n{code_text}\n")
    
    # Initialize code-specific detectors
    print("Step 1: Running code-specific detectors...")
    syntax_detector = CodeSyntaxDetector()
    library_checker = LibraryExistenceChecker()
    api_checker = APICorrectnessChecker()
    
    syntax_issues = syntax_detector.detect(code_text, domain="code")
    library_issues = library_checker.detect(code_text, domain="code")
    api_issues = api_checker.detect(code_text, domain="code")
    
    print(f"  - Syntax errors: {len(syntax_issues)}")
    print(f"  - Library issues: {len(library_issues)}")
    print(f"  - API issues: {len(api_issues)}")
    
    # Run general detection
    print("\nStep 2: Running general hallucination detection...")
    detector = HallucinationDetector(domain="code")
    report = detector.detect(code_text)
    print(f"  - Found {len(report.claims)} claims")
    print(f"  - Detected {len(report.detected_hallucinations)} potential hallucinations")
    
    # Score confidence
    print("\nStep 3: Scoring confidence...")
    scorer = ConfidenceScorer()
    report = scorer.score(report)
    
    # Display results
    print("\n" + "=" * 80)
    print("RESULTS")
    print("=" * 80)
    
    print("\nCode Issues Found:")
    
    if syntax_issues:
        print("\n  Syntax Errors:")
        for issue in syntax_issues:
            print(f"    - Line {issue.get('line')}: {issue.get('message')}")
    
    if library_issues:
        print("\n  Library Issues:")
        for issue in library_issues:
            print(f"    - {issue.get('library')}: {issue.get('message')}")
    
    if api_issues:
        print("\n  API Issues:")
        for issue in api_issues:
            print(f"    - {issue.get('wrong_api')} -> {issue.get('suggested_api')}")
            print(f"      {issue.get('message')}")
    
    print(f"\nOverall Reliability Score: {report.overall_reliability_score:.2%}")
    print(f"Total Issues Found: {len(syntax_issues) + len(library_issues) + len(api_issues)}")

if __name__ == "__main__":
    main()
