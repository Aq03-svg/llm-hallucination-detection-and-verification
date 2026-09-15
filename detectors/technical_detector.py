from typing import List, Dict, Any
from core.detector import BaseDetector
from core.models import HallucinationType
from utils.logger import logger
import re

class TechnicalAccuracyChecker(BaseDetector):
    """Checks technical accuracy of statements."""
    
    def __init__(self):
        super().__init__("TechnicalAccuracyChecker")
    
    def detect(self, text: str, domain: str = "technical") -> List[Dict[str, Any]]:
        """Check technical accuracy."""
        issues = []
        
        # Technical inaccuracies
        technical_errors = [
            (r'Internet.*runs on.*TCP/HTTP', 'Internet uses multiple protocols, not just TCP/HTTP'),
            (r'GPU.*cannot.*process.*CPU.*tasks', 'GPUs can process CPU tasks but may be inefficient'),
            (r'binary.*only.*0.*1', 'Binary uses 0 and 1, but this is an oversimplification'),
            (r'database.*unlimited.*capacity', 'Databases have capacity constraints'),
        ]
        
        for pattern, message in technical_errors:
            if re.search(pattern, text, re.IGNORECASE):
                issues.append({
                    'type': HallucinationType.FACTUAL_ERROR,
                    'message': message,
                    'severity': 'medium'
                })
        
        logger.info(f"Technical accuracy check: {len(issues)} issues found")
        return issues

class StandardComplianceChecker(BaseDetector):
    """Checks compliance with technical standards."""
    
    def __init__(self):
        super().__init__("StandardComplianceChecker")
    
    def detect(self, text: str, domain: str = "technical") -> List[Dict[str, Any]]:
        """Check standard compliance."""
        issues = []
        
        # Standard violations
        standard_violations = [
            (r'ignore.*certificate.*validation', 'Certificate validation should never be ignored'),
            (r'store.*password.*in.*plaintext', 'Passwords must never be stored in plaintext'),
            (r'disable.*SSL.*for.*API', 'SSL should not be disabled for APIs'),
            (r'execute.*arbitrary.*code.*from.*user', 'Never execute arbitrary user code'),
        ]
        
        for pattern, message in standard_violations:
            if re.search(pattern, text, re.IGNORECASE):
                issues.append({
                    'type': HallucinationType.FACTUAL_ERROR,
                    'message': message,
                    'severity': 'critical'
                })
        
        logger.info(f"Standard compliance check: {len(issues)} issues found")
        return issues

class ToolVersionChecker(BaseDetector):
    """Checks if tool/library versions are correct."""
    
    def __init__(self):
        super().__init__("ToolVersionChecker")
        self._version_info = self._load_version_info()
    
    def detect(self, text: str, domain: str = "technical") -> List[Dict[str, Any]]:
        """Check tool/library version accuracy."""
        issues = []
        
        # Extract version references
        version_pattern = r'([\w-]+)\s+(?:version|v|ver\.)?\s*([0-9]+(?:\.[0-9]+)*)'
        matches = re.findall(version_pattern, text, re.IGNORECASE)
        
        for tool, version in matches:
            # Check if version exists for tool
            if tool.lower() in self._version_info:
                valid_versions = self._version_info[tool.lower()]
                if version not in valid_versions:
                    issues.append({
                        'type': HallucinationType.FACTUAL_ERROR,
                        'tool': tool,
                        'version': version,
                        'message': f"Version {version} may not exist for {tool}",
                        'severity': 'medium'
                    })
        
        logger.info(f"Tool version check: {len(issues)} issues found")
        return issues
    
    def _load_version_info(self) -> Dict[str, List[str]]:
        """Load version information for common tools."""
        return {
            'python': ['2.7', '3.6', '3.7', '3.8', '3.9', '3.10', '3.11'],
            'nodejs': ['14.0', '16.0', '18.0', '20.0'],
            'java': ['8', '11', '17', '21'],
            'gcc': ['9.0', '10.0', '11.0', '12.0'],
        }
