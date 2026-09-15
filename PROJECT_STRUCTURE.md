# Project Structure Overview

```
llm-hallucination-detection-and-verification/
│
├── README.md                          # Main project documentation
├── QUICKSTART.md                      # Quick start guide
├── DETAILED_DOCUMENTATION.md          # Comprehensive documentation
├── CONTRIBUTING.md                    # Contributing guidelines
├── LICENSE                            # MIT License
├── requirements.txt                   # Python dependencies
├── setup.py                           # Package setup
├── .gitignore                         # Git ignore rules
│
├── config/                            # Configuration modules
│   ├── __init__.py
│   ├── settings.py                    # Application settings
│   └── domain_config.yaml             # Domain-specific config
│
├── core/                              # Core detection & verification
│   ├── __init__.py
│   ├── models.py                      # Data models and classes
│   ├── detector.py                    # Main hallucination detector
│   ├── verifier.py                    # Main claim verifier
│   └── confidence_scorer.py           # Confidence scoring engine
│
├── detectors/                         # Detection modules
│   ├── __init__.py
│   ├── code_detector.py               # Code-specific detectors
│   │   ├── CodeSyntaxDetector
│   │   ├── LibraryExistenceChecker
│   │   └── APICorrectnessChecker
│   ├── medical_detector.py            # Medical-specific detectors
│   │   ├── MedicalTerminologyChecker
│   │   ├── DrugInteractionChecker
│   │   └── ProcedureAccuracyChecker
│   ├── legal_detector.py              # Legal-specific detectors
│   │   ├── CitationValidator
│   │   ├── JurisdictionChecker
│   │   └── PrecedentAccuracyChecker
│   └── technical_detector.py          # Technical-specific detectors
│       ├── TechnicalAccuracyChecker
│       ├── StandardComplianceChecker
│       └── ToolVersionChecker
│
├── verifiers/                         # Verification modules
│   ├── __init__.py
│   └── knowledge_base_verifier.py     # Knowledge base verifiers
│       ├── MedicalKnowledgeBaseVerifier
│       ├── LegalDatabaseVerifier
│       └── TechnicalKnowledgeBaseVerifier
│
├── utils/                             # Utility modules
│   ├── __init__.py
│   ├── logger.py                      # Logging setup
│   ├── text_processing.py             # Text processing utilities
│   ├── embeddings.py                  # Embedding management
│   └── api_utils.py                   # API utilities
│
├── examples/                          # Example scripts
│   ├── basic_detection.py             # Simple usage example
│   ├── medical_verification.py        # Medical domain example
│   ├── code_analysis.py               # Code domain example
│   └── full_pipeline.py               # Complete pipeline example
│
├── tests/                             # Test suite
│   ├── __init__.py
│   ├── test_detectors.py              # Detector tests
│   ├── test_verifiers.py              # Verifier tests
│   ├── test_confidence_scorer.py      # Scorer tests
│   └── integration_tests.py           # End-to-end tests
│
├── data/                              # Data directory
│   ├── knowledge_bases/               # Local knowledge bases
│   ├── examples/                      # Example datasets
│   └── test_cases/                    # Test case data
│
├── notebooks/                         # Jupyter notebooks
│   └── analysis.ipynb                 # Analysis notebook
│
└── logs/                              # Log files (generated)
    └── hallucination_detector.log
```

## Component Descriptions

### Core Components

**models.py**
- `Claim`: Represents extracted factual claims
- `Evidence`: Represents supporting/contradicting evidence
- `VerificationResult`: Result of claim verification
- `HallucinationReport`: Complete analysis report

**detector.py**
- `ClaimExtractor`: Extracts factual claims from text
- `SemanticConsistencyDetector`: Detects logical inconsistencies
- `SelfContradictionDetector`: Detects conflicting claims
- `HallucinationDetector`: Main orchestration class

**verifier.py**
- `BaseVerifier`: Abstract base for all verifiers
- `SemanticVerifier`: Semantic analysis verification
- `WikipediaVerifier`: Wikipedia-based verification
- `GitHubVerifier`: GitHub API-based verification
- `HallucinationVerifier`: Main verification orchestrator

**confidence_scorer.py**
- `ConfidenceScorer`: Calculates confidence and reliability scores
- Implements multiple scoring factors
- Generates comprehensive score reports

### Domain Detectors

**code_detector.py**
- Syntax validation (Python AST)
- Library existence checking
- API correctness verification
- Method call validation

**medical_detector.py**
- Medical terminology validation
- Drug interaction checking
- Procedure accuracy verification
- Outdated practice detection

**legal_detector.py**
- Legal citation validation
- Jurisdiction accuracy checking
- Precedent verification
- Legal reference validation

**technical_detector.py**
- Technical accuracy checking
- Standard compliance verification
- Tool/library version validation
- Architecture correctness checking

### Utility Modules

**text_processing.py**
- Sentence and word tokenization
- Entity extraction
- Text cleaning and normalization
- Clause extraction
- Text statistics

**embeddings.py**
- Semantic embedding generation
- Similarity calculation
- Batch embedding processing
- Embedding caching

**api_utils.py**
- Wikipedia API wrapper
- GitHub API wrapper
- Async API calls
- Error handling and retries

**logger.py**
- Centralized logging setup
- Console and file logging
- Structured logging

## Data Flow

```
Input Text
    ↓
[Claim Extraction]
    ↓
[Parallel Detection]
├─→ Semantic Consistency
├─→ Self-Contradiction
└─→ Fact Checking
    ↓
[Domain-Specific Detection]
├─→ Code Detector
├─→ Medical Detector
├─→ Legal Detector
└─→ Technical Detector
    ↓
[Verification]
├─→ Wikipedia Verifier
├─→ GitHub Verifier
├─→ Knowledge Bases
└─→ Semantic Verifier
    ↓
[Confidence Scoring]
├─→ Claim Confidence
├─→ Verification Confidence
└─→ Overall Scores
    ↓
HallucinationReport
```

## File Dependencies

```
core/detector.py
├── depends on: models, text_processing, embeddings, logger
└── used by: examples, tests, detector orchestration

core/verifier.py
├── depends on: models, embeddings, text_processing, api_utils
└── used by: examples, tests, verification pipeline

core/confidence_scorer.py
├── depends on: models, logger
└── used by: examples, tests, scoring pipeline

detectors/*_detector.py
├── depends on: BaseDetector, text_processing, logger
└── used by: examples, tests, domain detection

verifiers/*_verifier.py
├── depends on: BaseVerifier, embeddings, api_utils
└── used by: examples, tests, verification

utilities/*
├── depended on by: all core and detector modules
└── provide: shared functionality
```

## Testing Structure

```
tests/
├── test_detectors.py
│   ├── TestClaimExtractor
│   ├── TestSemanticConsistencyDetector
│   ├── TestSelfContradictionDetector
│   └── TestHallucinationDetector
│
├── test_verifiers.py
│   ├── TestWikipediaVerifier
│   └── TestHallucinationVerifier
│
├── test_confidence_scorer.py
│   └── TestConfidenceScorer
│
└── integration_tests.py
    └── TestEndToEndPipeline
```

## Extension Points

### Adding a New Detector

1. Create `detectors/new_domain_detector.py`
2. Extend `BaseDetector` class
3. Implement `detect()` method
4. Register in main detector

### Adding a New Verifier

1. Create `verifiers/new_verifier.py`
2. Extend `BaseVerifier` class
3. Implement `verify()` method
4. Register in `HallucinationVerifier`

### Adding a New Data Source

1. Add API wrapper in `utils/api_utils.py`
2. Create corresponding verifier
3. Register in verification pipeline

---

For more details, see DETAILED_DOCUMENTATION.md
