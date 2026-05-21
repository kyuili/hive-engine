"""
Agent Orchestrator — Manages and coordinates multiple AI agents.
"""

import asyncio
import time
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field

from .event_bus import EventBus
from .router import ModelRouter


@dataclass
class AgentConfig:
    """Configuration for an AI agent."""
    name: str
    model: str
    task_type: str
    max_tokens: int = 4096
    temperature: float = 0.3
    timeout: int = 60


@dataclass
class ScanResult:
    """Result from a single agent scan."""
    agent: str
    model: str
    findings: list[dict]
    tokens_used: int
    duration_ms: int
    status: str


class AgentOrchestrator:
    """Orchestrates multiple AI agents for parallel task execution."""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.router = ModelRouter()
        self.start_time = time.time()
        self.active_scans: dict[str, dict] = {}
        self.scan_history: list[dict] = []
        
        # Initialize agents
        self.agents = {
            "security": AgentConfig(
                name="SecurityScanner",
                model="mimo-v2.5-pro",
                task_type="vulnerability_detection",
                max_tokens=8192,
                temperature=0.2
            ),
            "quality": AgentConfig(
                name="CodeQualityAgent",
                model="claude-sonnet",
                task_type="code_quality",
                max_tokens=4096,
                temperature=0.3
            ),
            "logic": AgentConfig(
                name="LogicAnalyzer",
                model="gpt-4-turbo",
                task_type="logic_analysis",
                max_tokens=4096,
                temperature=0.2
            ),
            "deps": AgentConfig(
                name="DependencyChecker",
                model="mimo-v2.5-pro",
                task_type="dependency_scan",
                max_tokens=2048,
                temperature=0.1
            ),
            "secrets": AgentConfig(
                name="SecretsHunter",
                model="claude-haiku",
                task_type="secrets_detection",
                max_tokens=2048,
                temperature=0.1
            ),
            "fixer": AgentConfig(
                name="FixSuggester",
                model="gpt-4-turbo",
                task_type="fix_suggestions",
                max_tokens=4096,
                temperature=0.4
            ),
            "tests": AgentConfig(
                name="TestWriter",
                model="claude-sonnet",
                task_type="test_generation",
                max_tokens=4096,
                temperature=0.5
            ),
            "docs": AgentConfig(
                name="DocGenerator",
                model="mimo-v2.5-pro",
                task_type="documentation",
                max_tokens=4096,
                temperature=0.3
            ),
            "report": AgentConfig(
                name="ReportGenerator",
                model="mimo-v2.5-pro",
                task_type="report_generation",
                max_tokens=2048,
                temperature=0.2
            ),
            "optimizer": AgentConfig(
                name="CostOptimizer",
                model="local-llama",
                task_type="routing_optimization",
                max_tokens=1024,
                temperature=0.1
            )
        }
        
        # Usage tracking per agent
        self.usage_stats = {name: {"tokens": 0, "scans": 0, "findings": 0} 
                           for name in self.agents}
    
    def uptime(self) -> str:
        """Get uptime as human-readable string."""
        elapsed = int(time.time() - self.start_time)
        hours = elapsed // 3600
        minutes = (elapsed % 3600) // 60
        return f"{hours}h {minutes}m"
    
    async def run_scan(self, scan_id: str, repo: str, agents: list[str], depth: str):
        """Run a scan with multiple agents in parallel."""
        self.active_scans[scan_id] = {
            "status": "running",
            "started_at": datetime.now().isoformat(),
            "repo": repo,
            "agents": agents
        }
        
        await self.event_bus.emit("scan_started", {
            "scan_id": scan_id,
            "repo": repo,
            "agents": agents
        })
        
        # Run agents in parallel
        tasks = []
        for agent_name in agents:
            if agent_name in self.agents:
                task = self._run_agent(scan_id, agent_name, repo, depth)
                tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Aggregate results
        all_findings = []
        total_tokens = 0
        
        for result in results:
            if isinstance(result, ScanResult):
                all_findings.extend(result.findings)
                total_tokens += result.tokens_used
        
        # Calculate security score
        critical = sum(1 for f in all_findings if f.get("severity") == "critical")
        high = sum(1 for f in all_findings if f.get("severity") == "high")
        medium = sum(1 for f in all_findings if f.get("severity") == "medium")
        low = sum(1 for f in all_findings if f.get("severity") == "low")
        
        # Score: 100 - (critical*10 + high*5 + medium*2 + low*0.5)
        score = max(0, 100 - (critical*10 + high*5 + medium*2 + low*0.5))
        
        # Update scan result
        self.active_scans[scan_id].update({
            "status": "completed",
            "completed_at": datetime.now().isoformat(),
            "findings": all_findings,
            "metrics": {
                "total_findings": len(all_findings),
                "critical": critical,
                "high": high,
                "medium": medium,
                "low": low,
                "security_score": round(score, 1),
                "tokens_used": total_tokens
            }
        })
        
        # Move to history
        self.scan_history.append(self.active_scans[scan_id])
        del self.active_scans[scan_id]
        
        await self.event_bus.emit("scan_completed", {
            "scan_id": scan_id,
            "findings": len(all_findings),
            "score": score
        })
    
    async def _run_agent(self, scan_id: str, agent_name: str, repo: str, depth: str) -> ScanResult:
        """Run a single agent."""
        config = self.agents[agent_name]
        start_time = time.time()
        
        await self.event_bus.emit("agent_started", {
            "scan_id": scan_id,
            "agent": config.name,
            "model": config.model
        })
        
        # Simulate agent work (in production, this calls actual AI APIs)
        await asyncio.sleep(0.5)  # Simulate processing
        
        # Generate mock findings
        findings = self._generate_findings(agent_name, depth)
        tokens_used = self._estimate_tokens(agent_name, depth)
        
        # Update usage stats
        self.usage_stats[agent_name]["tokens"] += tokens_used
        self.usage_stats[agent_name]["scans"] += 1
        self.usage_stats[agent_name]["findings"] += len(findings)
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        await self.event_bus.emit("agent_completed", {
            "scan_id": scan_id,
            "agent": config.name,
            "findings": len(findings),
            "tokens": tokens_used,
            "duration_ms": duration_ms
        })
        
        return ScanResult(
            agent=config.name,
            model=config.model,
            findings=findings,
            tokens_used=tokens_used,
            duration_ms=duration_ms,
            status="completed"
        )
    
    def _generate_findings(self, agent_name: str, depth: str) -> list[dict]:
        """Generate mock findings for demo."""
        import random
        
        findings_templates = {
            "security": [
                {"type": "sql_injection", "severity": "critical", "file": "db.py", "line": 45},
                {"type": "xss", "severity": "high", "file": "templates/index.html", "line": 12},
                {"type": "command_injection", "severity": "critical", "file": "utils.py", "line": 78},
                {"type": "path_traversal", "severity": "medium", "file": "file_handler.py", "line": 23},
                {"type": "weak_crypto", "severity": "medium", "file": "auth.py", "line": 56},
            ],
            "quality": [
                {"type": "high_complexity", "severity": "medium", "file": "parser.py", "line": 100},
                {"type": "code_duplication", "severity": "low", "file": "handlers/", "line": 0},
                {"type": "missing_type_hints", "severity": "low", "file": "api.py", "line": 34},
            ],
            "logic": [
                {"type": "race_condition", "severity": "high", "file": "concurrent.py", "line": 67},
                {"type": "null_pointer", "severity": "medium", "file": "processor.py", "line": 89},
            ],
            "deps": [
                {"type": "cve_2024_1234", "severity": "critical", "file": "requirements.txt", "line": 5},
                {"type": "outdated_package", "severity": "low", "file": "package.json", "line": 12},
            ],
            "secrets": [
                {"type": "hardcoded_key", "severity": "critical", "file": "config.py", "line": 8},
                {"type": "exposed_token", "severity": "high", "file": ".env.example", "line": 3},
            ]
        }
        
        base_findings = findings_templates.get(agent_name, [])
        
        # Scale by depth
        multiplier = {"quick": 0.5, "targeted": 0.8, "full": 1.0}.get(depth, 1.0)
        count = max(1, int(len(base_findings) * multiplier))
        
        return random.sample(base_findings, min(count, len(base_findings)))
    
    def _estimate_tokens(self, agent_name: str, depth: str) -> int:
        """Estimate token usage for agent."""
        base_tokens = {
            "security": 2100,
            "quality": 1800,
            "logic": 1200,
            "deps": 890,
            "secrets": 650,
            "fixer": 1100,
            "tests": 1500,
            "docs": 780,
            "report": 420,
            "optimizer": 120
        }
        
        multiplier = {"quick": 0.3, "targeted": 0.6, "full": 1.0}.get(depth, 1.0)
        return int(base_tokens.get(agent_name, 500) * multiplier)
    
    def get_scan(self, scan_id: str) -> Optional[dict]:
        """Get scan result by ID."""
        # Check active scans
        if scan_id in self.active_scans:
            return self.active_scans[scan_id]
        
        # Check history
        for scan in self.scan_history:
            if scan.get("scan_id") == scan_id:
                return scan
        
        return None
    
    def get_agent_status(self) -> list[dict]:
        """Get status of all agents."""
        status = []
        for name, config in self.agents.items():
            stats = self.usage_stats[name]
            status.append({
                "name": config.name,
                "model": config.model,
                "task_type": config.task_type,
                "status": "active",
                "total_tokens": stats["tokens"],
                "total_scans": stats["scans"],
                "total_findings": stats["findings"]
            })
        return status
    
    async def shutdown(self):
        """Graceful shutdown."""
        # Cancel active scans
        for scan_id in list(self.active_scans.keys()):
            self.active_scans[scan_id]["status"] = "cancelled"
        
        await self.event_bus.emit("orchestrator_shutdown", {})
