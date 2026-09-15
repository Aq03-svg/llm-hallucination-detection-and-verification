# Quick Start Guide

## Installation

```bash
# Clone the repository
git clone https://github.com/Aq03-svg/llm-hallucination-detection-and-verification.git
cd llm-hallucination-detection-and-verification

# Install dependencies
pip install -r requirements.txt
```

## Basic Usage

### 1. Simple Detection

```python
from core.detector import HallucinationDetector

text = "Paris is the capital of France."
detector = HallucinationDetector(domain="general")
report = detector.detect(text)

print(f"Claims found: {len(report.claims)}")
print(f"Hallucinations: {len(report.detected_hallucinations)}")
```

### 2. Full Pipeline

```python
from core.detector import HallucinationDetector
from core.verifier import HallucinationVerifier
from core.confidence_scorer import ConfidenceScorer

text = "Your LLM-generated text here"

# Step 1: Detect
detector = HallucinationDetector(domain="general")
report = detector.detect(text)

# Step 2: Verify
verifier = HallucinationVerifier()
report = verifier.verify(report)

# Step 3: Score
scorer = ConfidenceScorer()
report = scorer.score(report)

# Results
print(f"Overall Confidence: {report.overall_confidence:.2%}")
print(f"Overall Reliability: {report.overall_reliability_score:.2%}")
```

### 3. Domain-Specific Detection

**Medical:**
```python
from detectors.medical_detector import MedicalTerminologyChecker

checker = MedicalTerminologyChecker()
issues = checker.detect("Patient has Type 2 diabetes", domain="medical")
```

**Code:**
```python
from detectors.code_detector import APICorrectnessChecker

checker = APICorrectnessChecker()
issues = checker.detect("result = df.apply()  # Correct", domain="code")
```

**Legal:**
```python
from detectors.legal_detector import CitationValidator

validator = CitationValidator()
issues = validator.detect("In Smith v. Jones case...", domain="legal")
```

## Running Examples

```bash
# Basic detection
python examples/basic_detection.py

# Medical analysis
python examples/medical_verification.py

# Code analysis
python examples/code_analysis.py

# Full pipeline
python examples/full_pipeline.py
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=core --cov=detectors --cov=verifiers

# Run specific test file
pytest tests/test_detectors.py -v
```

## Configuration

Edit `config/settings.py` to customize:

```python
# Detection thresholds
SEMANTIC_SIMILARITY_THRESHOLD = 0.75
CONTRADICTION_THRESHOLD = 0.85
CONFIDENCE_THRESHOLD = 0.7

# API settings
WIKIPEDIA_API_TIMEOUT = 10
GITHUB_API_TIMEOUT = 10

# Model settings
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
DEVICE = "cuda"  # or "cpu"
```

## Common Tasks

### Analyze LLM Output

```python
from core.detector import HallucinationDetector
from core.verifier import HallucinationVerifier
from core.confidence_scorer import ConfidenceScorer

llm_output = """..your LLM response..."""

detector = HallucinationDetector(domain="general")
verifier = HallucinationVerifier()
scorer = ConfidenceScorer()

report = detector.detect(llm_output)
report = verifier.verify(report)
report = scorer.score(report)

# Check if reliable
if report.overall_confidence > 0.8:
    print("High confidence - likely reliable")
else:
    print(f"Low confidence - review needed")
    for h in report.detected_hallucinations:
        print(f"  - {h}")
```

### Batch Processing

```python
import json
from core.detector import HallucinationDetector
from core.verifier import HallucinationVerifier
from core.confidence_scorer import ConfidenceScorer

texts = [
    "Text 1 from LLM",
    "Text 2 from LLM",
    "Text 3 from LLM",
]

detector = HallucinationDetector()
verifier = HallucinationVerifier()
scorer = ConfidenceScorer()

results = []
for text in texts:
    report = detector.detect(text)
    report = verifier.verify(report)
    report = scorer.score(report)
    
    results.append({
        "text": text,
        "confidence": report.overall_confidence,
        "reliability": report.overall_reliability_score,
        "hallucinations": len(report.detected_hallucinations)
    })

print(json.dumps(results, indent=2))
```

### Custom Domain Detection

```python
from core.detector import BaseDetector
from core.models import HallucinationType

class CustomDetector(BaseDetector):
    def __init__(self):
        super().__init__("CustomDetector")
    
    def detect(self, text, domain="custom"):
        issues = []
        # Your detection logic here
        return issues
```

## Troubleshooting

**ImportError: No module named...**
```bash
pip install -r requirements.txt
```

**CUDA out of memory**
```python
import torch
torch.cuda.empty_cache()
```

**Slow API calls**
```python
from config.settings import settings
settings.ENABLE_CACHING = True
```

## Next Steps

1. Read [DETAILED_DOCUMENTATION.md](DETAILED_DOCUMENTATION.md) for comprehensive guide
2. Check [examples/](examples/) for more use cases
3. Explore [tests/](tests/) for implementation details
4. See [CONTRIBUTING.md](CONTRIBUTING.md) to contribute

## Need Help?

- 📖 Check documentation
- 🔍 Search existing issues
- 💬 Open a new issue
- 🤝 See CONTRIBUTING.md

---

**Happy detecting!** 🚀
