"""
Base Agent — Abstract base class for all AI agents.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class Finding:
    """A finding from an agent scan."""
    type: str
    severity: str  # critical, high, medium, low, info
    file: str
    line: int
    description: str
    cwe_id: Optional[str] = None
    recommendation: Optional[str] = None


@dataclass
class AgentResult:
    """Result from an agent execution."""
    agent_name: str
    model_used: str
    findings: list[Finding]
    tokens_used: int
    duration_ms: int
    status: str  # completed, failed, timeout
    error: Optional[str] = None


class BaseAgent(ABC):
    """Abstract base class for AI agents."""
    
    def __init__(self, name: str, model: str):
        self.name = name
        self.model = model
        self.findings: list[Finding] = []
        self.tokens_used = 0
    
    @abstractmethod
    async def analyze(self, code: str, context: dict) -> list[Finding]:
        """Analyze code and return findings."""
        pass
    
    @abstractmethod
    def get_prompt(self, code: str, context: dict) -> str:
        """Generate the prompt for the AI model."""
        pass
    
    def add_finding(self, finding: Finding):
        """Add a finding to the results."""
        self.findings.append(finding)
    
    def get_results(self) -> AgentResult:
        """Get the agent results."""
        return AgentResult(
            agent_name=self.name,
            model_used=self.model,
            findings=self.findings,
            tokens_used=self.tokens_used,
            duration_ms=0,  # Will be set by orchestrator
            status="completed"
        )
