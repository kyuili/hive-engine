"""
Model Router — Intelligent routing of tasks to optimal AI models.
"""

import random
from dataclasses import dataclass
from typing import Optional


@dataclass
class ModelConfig:
    """Configuration for an AI model."""
    name: str
    provider: str
    cost_per_1k_tokens: float  # USD
    max_tokens: int
    strengths: list[str]
    latency_ms: int


class ModelRouter:
    """Routes tasks to the optimal AI model based on task type, cost, and availability."""
    
    def __init__(self):
        self.models = {
            "mimo-v2.5-pro": ModelConfig(
                name="MiMo v2.5-pro",
                provider="Xiaomi",
                cost_per_1k_tokens=0.002,
                max_tokens=32768,
                strengths=["code_analysis", "security", "documentation", "general"],
                latency_ms=150
            ),
            "claude-sonnet": ModelConfig(
                name="Claude 3.5 Sonnet",
                provider="Anthropic",
                cost_per_1k_tokens=0.003,
                max_tokens=200000,
                strengths=["code_quality", "test_generation", "complex_reasoning"],
                latency_ms=200
            ),
            "gpt-4-turbo": ModelConfig(
                name="GPT-4 Turbo",
                provider="OpenAI",
                cost_per_1k_tokens=0.01,
                max_tokens=128000,
                strengths=["logic_analysis", "fix_suggestions", "architecture"],
                latency_ms=250
            ),
            "claude-haiku": ModelConfig(
                name="Claude 3 Haiku",
                provider="Anthropic",
                cost_per_1k_tokens=0.00025,
                max_tokens=200000,
                strengths=["secrets_detection", "quick_analysis", "classification"],
                latency_ms=80
            ),
            "local-llama": ModelConfig(
                name="LLaMA 3 70B",
                provider="Local",
                cost_per_1k_tokens=0.0,
                max_tokens=8192,
                strengths=["routing_optimization", "simple_tasks"],
                latency_ms=50
            )
        }
        
        # Task to model mapping
        self.task_model_map = {
            "vulnerability_detection": "mimo-v2.5-pro",
            "code_quality": "claude-sonnet",
            "logic_analysis": "gpt-4-turbo",
            "dependency_scan": "mimo-v2.5-pro",
            "secrets_detection": "claude-haiku",
            "fix_suggestions": "gpt-4-turbo",
            "test_generation": "claude-sonnet",
            "documentation": "mimo-v2.5-pro",
            "report_generation": "mimo-v2.5-pro",
            "routing_optimization": "local-llama"
        }
        
        # Usage tracking
        self.usage = {model: {"calls": 0, "tokens": 0, "cost": 0.0} 
                     for model in self.models}
        
        # Fallback chains
        self.fallback_chains = {
            "mimo-v2.5-pro": ["claude-sonnet", "gpt-4-turbo"],
            "claude-sonnet": ["mimo-v2.5-pro", "gpt-4-turbo"],
            "gpt-4-turbo": ["claude-sonnet", "mimo-v2.5-pro"],
            "claude-haiku": ["mimo-v2.5-pro"],
            "local-llama": ["mimo-v2.5-pro"]
        }
    
    def select_model(self, task_type: str, complexity: str = "full") -> str:
        """Select the optimal model for a task."""
        # Get primary model for task
        primary = self.task_model_map.get(task_type, "mimo-v2.5-pro")
        
        # Check if we should use a cheaper model based on complexity
        if complexity == "quick":
            # Use cheaper model for quick scans
            if primary == "gpt-4-turbo":
                return "mimo-v2.5-pro"
            elif primary == "claude-sonnet":
                return "claude-haiku"
        
        return primary
    
    def get_model_config(self, model_name: str) -> Optional[ModelConfig]:
        """Get configuration for a model."""
        return self.models.get(model_name)
    
    def record_usage(self, model_name: str, tokens: int):
        """Record token usage for a model."""
        if model_name in self.usage:
            config = self.models[model_name]
            cost = (tokens / 1000) * config.cost_per_1k_tokens
            
            self.usage[model_name]["calls"] += 1
            self.usage[model_name]["tokens"] += tokens
            self.usage[model_name]["cost"] += cost
    
    def get_usage_breakdown(self) -> dict:
        """Get usage breakdown by model."""
        breakdown = {}
        total_tokens = sum(u["tokens"] for u in self.usage.values())
        total_cost = sum(u["cost"] for u in self.usage.values())
        
        for model_name, usage in self.usage.items():
            config = self.models[model_name]
            percentage = (usage["tokens"] / total_tokens * 100) if total_tokens > 0 else 0
            
            breakdown[model_name] = {
                "name": config.name,
                "provider": config.provider,
                "calls": usage["calls"],
                "tokens": usage["tokens"],
                "cost_usd": round(usage["cost"], 2),
                "percentage": round(percentage, 1)
            }
        
        return {
            "models": breakdown,
            "totals": {
                "tokens": total_tokens,
                "cost_usd": round(total_cost, 2),
                "calls": sum(u["calls"] for u in self.usage.values())
            }
        }
    
    def get_fallback(self, model_name: str) -> Optional[str]:
        """Get fallback model if primary is unavailable."""
        chain = self.fallback_chains.get(model_name, [])
        return chain[0] if chain else None
