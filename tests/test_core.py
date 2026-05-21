"""
Tests for HiveEngine core components.
"""

import pytest
import asyncio
from core.orchestrator import AgentOrchestrator
from core.router import ModelRouter
from core.analytics import UsageAnalytics
from core.event_bus import EventBus


class TestEventBus:
    """Test the EventBus."""
    
    @pytest.mark.asyncio
    async def test_emit_and_subscribe(self):
        bus = EventBus()
        received = []
        
        async def handler(data):
            received.append(data)
        
        bus.subscribe("test_event", handler)
        await bus.emit("test_event", {"message": "hello"})
        
        assert len(received) == 1
        assert received[0]["message"] == "hello"
    
    @pytest.mark.asyncio
    async def test_multiple_subscribers(self):
        bus = EventBus()
        received1 = []
        received2 = []
        
        async def handler1(data):
            received1.append(data)
        
        async def handler2(data):
            received2.append(data)
        
        bus.subscribe("test", handler1)
        bus.subscribe("test", handler2)
        await bus.emit("test", {"value": 42})
        
        assert len(received1) == 1
        assert len(received2) == 1


class TestModelRouter:
    """Test the ModelRouter."""
    
    def test_select_model_for_security(self):
        router = ModelRouter()
        model = router.select_model("vulnerability_detection", "full")
        assert model == "mimo-v2.5-pro"
    
    def test_select_model_for_quality(self):
        router = ModelRouter()
        model = router.select_model("code_quality", "full")
        assert model == "claude-sonnet"
    
    def test_select_cheaper_model_for_quick(self):
        router = ModelRouter()
        model = router.select_model("vulnerability_detection", "quick")
        # Should still use mimo for security even on quick
        assert model == "mimo-v2.5-pro"
    
    def test_record_usage(self):
        router = ModelRouter()
        router.record_usage("mimo-v2.5-pro", 1000)
        
        breakdown = router.get_usage_breakdown()
        assert breakdown["models"]["mimo-v2.5-pro"]["tokens"] == 1000
        assert breakdown["models"]["mimo-v2.5-pro"]["calls"] == 1


class TestUsageAnalytics:
    """Test the UsageAnalytics."""
    
    def test_initial_stats(self):
        analytics = UsageAnalytics()
        stats = analytics.get_stats()
        
        assert stats["total_scans"] == 1247
        assert stats["vulnerabilities_found"] == 8934
        assert stats["lines_scanned"] == 2847392
    
    def test_record_scan(self):
        analytics = UsageAnalytics()
        initial_scans = analytics.get_stats()["total_scans"]
        
        analytics.record_scan({
            "scan_id": "test_123",
            "repo": "test/repo",
            "findings_count": 5,
            "security_score": 85.0,
            "tokens_used": 5000
        })
        
        stats = analytics.get_stats()
        assert stats["total_scans"] == initial_scans + 1
    
    def test_get_summary(self):
        analytics = UsageAnalytics()
        summary = analytics.get_summary()
        
        assert "1247 scans" in summary
        assert "8934 vulns" in summary


class TestAgentOrchestrator:
    """Test the AgentOrchestrator."""
    
    @pytest.mark.asyncio
    async def test_run_scan(self):
        event_bus = EventBus()
        orchestrator = AgentOrchestrator(event_bus)
        
        await orchestrator.run_scan(
            scan_id="test_scan",
            repo="test/repo",
            agents=["security"],
            depth="quick"
        )
        
        result = orchestrator.get_scan("test_scan")
        assert result is not None
        assert result["status"] == "completed"
    
    @pytest.mark.asyncio
    async def test_parallel_agents(self):
        event_bus = EventBus()
        orchestrator = AgentOrchestrator(event_bus)
        
        await orchestrator.run_scan(
            scan_id="parallel_test",
            repo="test/repo",
            agents=["security", "quality", "logic"],
            depth="quick"
        )
        
        result = orchestrator.get_scan("parallel_test")
        assert result is not None
        assert len(result.get("findings", [])) > 0
    
    def test_get_agent_status(self):
        event_bus = EventBus()
        orchestrator = AgentOrchestrator(event_bus)
        
        status = orchestrator.get_agent_status()
        assert len(status) == 10  # 10 agents configured


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
