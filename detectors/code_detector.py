from typing import List, Dict, Any, Optional
from core.detector import BaseDetector
from core.models import HallucinationType
from utils.logger import logger
import re
import ast

class CodeSyntaxDetector(BaseDetector):
    """Detects syntax errors and invalid code patterns."""
    
    def __init__(self):
        super().__init__("CodeSyntaxDetector")
    
    def detect(self, text: str, domain: str = "code") -> List[Dict[str, Any]]:
        """Detect code syntax issues."""
        issues = []
        
        # Extract code blocks
        code_blocks = self._extract_code_blocks(text)
        
        for idx, code_block in enumerate(code_blocks):
            syntax_errors = self._check_python_syntax(code_block['code'])
            if syntax_errors:
                for error in syntax_errors:
                    issues.append({
                        'type': HallucinationType.FACTUAL_ERROR,
                        'code_block': idx,
                        'error': error,
                        'line': code_block['start_line'] + error.get('line', 0),
                        'severity': 'high'
                    })
        
        logger.info(f"Code syntax check: {len(issues)} issues found")
        return issues
    
    def _extract_code_blocks(self, text: str) -> List[Dict[str, Any]]:
        """Extract code blocks from text."""
        code_blocks = []
        
        # Pattern for markdown code blocks
        pattern = r'```(?:python|java|js|typescript|cpp|c\+\+)?\n([\s\S]*?)```'
        matches = re.finditer(pattern, text)
        
        for match in matches:
            code_blocks.append({
                'code': match.group(1),
                'start_line': text[:match.start()].count('\n'),
                'language': 'python'  # Default to Python
            })
        
        return code_blocks
    
    def _check_python_syntax(self, code: str) -> List[Dict[str, Any]]:
        """Check Python syntax validity."""
        errors = []
        try:
            ast.parse(code)
        except SyntaxError as e:
            errors.append({
                'line': e.lineno,
                'message': str(e),
                'text': e.text
            })
        except Exception as e:
            errors.append({
                'message': str(e),
                'type': 'unknown'
            })
        
        return errors

class LibraryExistenceChecker(BaseDetector):
    """Checks if referenced libraries/packages exist."""
    
    def __init__(self):
        super().__init__("LibraryExistenceChecker")
    
    def detect(self, text: str, domain: str = "code") -> List[Dict[str, Any]]:
        """Check for non-existent libraries."""
        issues = []
        
        # Common fake/misspelled libraries
        common_mistakes = {
            'numpy': ['numpyy', 'np', 'numpy-ml'],
            'pandas': ['panda', 'pandas-ml'],
            'tensorflow': ['tensorflw', 'tensor-flow'],
            'pytorch': ['pytorch-nightly'],
            'requests': ['request', 'urllib3-requests'],
            'flask': ['flask', 'flask-app']
        }
        
        # Extract imports
        import_patterns = [
            r'(?:from|import)\s+([\w_][\w\d_.]*)',
            r'pip\s+install\s+([\w_-][\w\d\-.]*)',
            r'npm\s+install\s+([\w_-][\w\d\-.]*)',
        ]
        
        for pattern in import_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for library in matches:
                if library in common_mistakes:
                    issues.append({
                        'type': HallucinationType.FABRICATED_ENTITY,
                        'library': library,
                        'message': f"Possible misspelling of '{library}'",
                        'severity': 'medium'
                    })
        
        logger.info(f"Library existence check: {len(issues)} issues found")
        return issues

class APICorrectnessChecker(BaseDetector):
    """Checks if referenced APIs and methods are correct."""
    
    def __init__(self):
        super().__init__("APICorrectnessChecker")
    
    def detect(self, text: str, domain: str = "code") -> List[Dict[str, Any]]:
        """Check API correctness."""
        issues = []
        
        # Common API mistakes
        api_mistakes = {
            'DataFrame.apply': ['DataFrame.map', 'DataFrame.apply_map'],
            'requests.get': ['requests.fetch', 'requests.load'],
            'json.loads': ['json.load', 'json.parse'],
            'os.path.join': ['os.path.combine', 'os.combine_path'],
        }
        
        # Extract method calls
        method_pattern = r'([\w_][\w\d_.]*)\.([\w_][\w\d_]*)\s*\('
        matches = re.findall(method_pattern, text)
        
        for obj, method in matches:
            full_method = f"{obj}.{method}"
            
            # Check against common mistakes
            for correct_api, wrong_apis in api_mistakes.items():
                if full_method in wrong_apis:
                    issues.append({
                        'type': HallucinationType.FACTUAL_ERROR,
                        'wrong_api': full_method,
                        'suggested_api': correct_api,
                        'message': f"API '{full_method}' does not exist. Did you mean '{correct_api}'?",
                        'severity': 'high'
                    })
        
        logger.info(f"API correctness check: {len(issues)} issues found")
        return issues
