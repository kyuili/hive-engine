"""
Security Scanner Agent — Detects security vulnerabilities in code.
"""

import re
from typing import Optional
from .base import BaseAgent, Finding


class SecurityScanner(BaseAgent):
    """AI agent for detecting security vulnerabilities."""
    
    # Common vulnerability patterns
    PATTERNS = {
        "sql_injection": {
            "regex": r"(?:execute|cursor\.execute|query)\s*\(\s*[\"'].*(?:\%s|\%d|\{|\+)",
            "severity": "critical",
            "cwe": "CWE-89",
            "description": "Potential SQL injection via string formatting"
        },
        "xss": {
            "regex": r"(?:innerHTML|outerHTML|document\.write)\s*=",
            "severity": "high",
            "cwe": "CWE-79",
            "description": "Potential XSS via unsafe DOM manipulation"
        },
        "command_injection": {
            "regex": r"(?:os\.system|subprocess\.call|subprocess\.Popen)\s*\(",
            "severity": "critical",
            "cwe": "CWE-78",
            "description": "Potential command injection"
        },
        "path_traversal": {
            "regex": r"open\s*\(\s*(?:.*\+|.*\%|f\"|.*\.format)",
            "severity": "high",
            "cwe": "CWE-22",
            "description": "Potential path traversal"
        },
        "weak_crypto": {
            "regex": r"(?:md5|sha1)\s*\(",
            "severity": "medium",
            "cwe": "CWE-327",
            "description": "Weak cryptographic algorithm"
        },
        "hardcoded_password": {
            "regex": r"(?:password|passwd|pwd)\s*=\s*[\"'][^\"']+[\"']",
            "severity": "critical",
            "cwe": "CWE-798",
            "description": "Hardcoded password detected"
        },
        "eval_usage": {
            "regex": r"eval\s*\(",
            "severity": "high",
            "cwe": "CWE-95",
            "description": "Use of eval() can lead to code injection"
        },
        "pickle_load": {
            "regex": r"pickle\.load\s*\(",
            "severity": "high",
            "cwe": "CWE-502",
            "description": "Unsafe deserialization with pickle"
        }
    }
    
    def __init__(self):
        super().__init__(
            name="SecurityScanner",
            model="mimo-v2.5-pro"
        )
    
    def get_prompt(self, code: str, context: dict) -> str:
        """Generate prompt for AI analysis."""
        return f"""Analyze the following code for security vulnerabilities.

Focus on:
1. SQL Injection (CWE-89)
2. Cross-Site Scripting (CWE-79)
3. Command Injection (CWE-78)
4. Path Traversal (CWE-22)
5. Weak Cryptography (CWE-327)
6. Hardcoded Credentials (CWE-798)
7. Unsafe Deserialization (CWE-502)
8. Code Injection (CWE-95)

For each vulnerability found, provide:
- type: vulnerability type
- severity: critical/high/medium/low
- file: filename
- line: line number
- description: detailed description
- cwe_id: CWE identifier
- recommendation: how to fix

Code to analyze:
```
{code}
```

Context: {context}

Respond with a JSON array of findings."""
    
    async def analyze(self, code: str, context: dict) -> list[Finding]:
        """Analyze code for security vulnerabilities."""
        findings = []
        
        # Pattern-based detection
        for vuln_type, pattern_info in self.PATTERNS.items():
            matches = re.finditer(pattern_info["regex"], code, re.IGNORECASE)
            
            for match in matches:
                # Calculate line number
                line_num = code[:match.start()].count('\n') + 1
                
                finding = Finding(
                    type=vuln_type,
                    severity=pattern_info["severity"],
                    file=context.get("file", "unknown"),
                    line=line_num,
                    description=pattern_info["description"],
                    cwe_id=pattern_info["cwe"],
                    recommendation=self._get_recommendation(vuln_type)
                )
                findings.append(finding)
        
        # Estimate tokens used
        self.tokens_used = len(code) // 4  # Rough estimate
        
        return findings
    
    def _get_recommendation(self, vuln_type: str) -> str:
        """Get remediation recommendation."""
        recommendations = {
            "sql_injection": "Use parameterized queries or ORM instead of string formatting",
            "xss": "Use textContent instead of innerHTML, or sanitize input",
            "command_injection": "Use subprocess with shell=False and validate inputs",
            "path_traversal": "Validate and sanitize file paths, use os.path.join()",
            "weak_crypto": "Use SHA-256 or stronger algorithms",
            "hardcoded_password": "Use environment variables or secrets manager",
            "eval_usage": "Avoid eval(), use ast.literal_eval() for safe evaluation",
            "pickle_load": "Use JSON or other safe serialization formats"
        }
        return recommendations.get(vuln_type, "Review and fix the vulnerability")
