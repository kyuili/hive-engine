"""
HiveEngine — Multi-Model AI Orchestration Platform
Main entry point for the API server.
"""

import asyncio
import time
from datetime import datetime
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn

from core.orchestrator import AgentOrchestrator
from core.router import ModelRouter
from core.analytics import UsageAnalytics
from core.event_bus import EventBus


# === Data Models ===

class ScanRequest(BaseModel):
    repo: str
    agents: list[str] = ["security", "quality", "logic", "deps", "secrets"]
    depth: str = "full"  # full, quick, targeted

class ScanResult(BaseModel):
    scan_id: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime]
    vulnerabilities: list[dict]
    metrics: dict

class UsageStats(BaseModel):
    total_scans: int
    vulnerabilities_found: int
    lines_scanned: int
    avg_security_score: float
    vulns_fixed: int
    active_agents: int
    total_tokens: int
    total_cost_usd: float


# === Core Components ===

event_bus = EventBus()
orchestrator = AgentOrchestrator(event_bus)
router = ModelRouter()
analytics = UsageAnalytics()

# Live WebSocket connections
live_connections: list[WebSocket] = []


# === Lifespan ===

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup
    print("🐝 HiveEngine starting...")
    print(f"📊 Loaded {len(orchestrator.agents)} agents")
    print(f"📈 Historical stats: {analytics.get_summary()}")
    
    yield
    
    # Shutdown
    print("🛑 HiveEngine shutting down...")
    await orchestrator.shutdown()


# === FastAPI App ===

app = FastAPI(
    title="HiveEngine",
    description="Multi-Model AI Orchestration Platform",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# === API Routes ===

@app.get("/")
async def root():
    """Health check."""
    return {
        "name": "HiveEngine",
        "status": "running",
        "agents": len(orchestrator.agents),
        "uptime": orchestrator.uptime()
    }


@app.post("/api/scan")
async def start_scan(request: ScanRequest):
    """Start a new security scan."""
    scan_id = f"scan_{int(time.time())}"
    
    # Select model for each agent based on task
    model_assignments = {}
    for agent_name in request.agents:
        model_assignments[agent_name] = router.select_model(
            task_type=agent_name,
            complexity=request.depth
        )
    
    # Start scan in background
    asyncio.create_task(
        orchestrator.run_scan(
            scan_id=scan_id,
            repo=request.repo,
            agents=request.agents,
            depth=request.depth
        )
    )
    
    return {
        "scan_id": scan_id,
        "status": "started",
        "agents": request.agents,
        "models": model_assignments
    }


@app.get("/api/scan/{scan_id}")
async def get_scan(scan_id: str):
    """Get scan results."""
    result = orchestrator.get_scan(scan_id)
    if not result:
        raise HTTPException(status_code=404, detail="Scan not found")
    return result


@app.get("/api/stats", response_model=UsageStats)
async def get_stats():
    """Get usage statistics."""
    return analytics.get_stats()


@app.get("/api/agents")
async def get_agents():
    """Get agent status."""
    return orchestrator.get_agent_status()


@app.get("/api/models")
async def get_models():
    """Get model usage breakdown."""
    return router.get_usage_breakdown()


@app.get("/api/costs")
async def get_costs():
    """Get cost breakdown."""
    return analytics.get_cost_breakdown()


@app.get("/api/history")
async def get_history(limit: int = 50):
    """Get scan history."""
    return analytics.get_history(limit)


# === Dashboard ===

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Serve the analytics dashboard."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>HiveEngine Dashboard</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0a0a0a; color: #e0e0e0; }
            .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
            h1 { color: #00ff88; margin-bottom: 30px; }
            .stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 30px; }
            .stat-card { background: #1a1a1a; border-radius: 12px; padding: 24px; border: 1px solid #333; }
            .stat-value { font-size: 36px; font-weight: bold; color: #00ff88; }
            .stat-label { color: #888; margin-top: 8px; }
            .chart-container { background: #1a1a1a; border-radius: 12px; padding: 24px; border: 1px solid #333; margin-bottom: 20px; }
            .agent-list { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; }
            .agent-card { background: #1a1a1a; border-radius: 8px; padding: 16px; border: 1px solid #333; }
            .agent-name { font-weight: bold; color: #00ff88; }
            .agent-model { color: #888; font-size: 14px; }
            .agent-tokens { color: #ffaa00; }
            .status-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 8px; }
            .status-active { background: #00ff88; }
            .status-idle { background: #666; }
            #live-feed { background: #111; border-radius: 8px; padding: 16px; height: 300px; overflow-y: auto; font-family: monospace; font-size: 14px; }
            .feed-entry { margin-bottom: 8px; padding: 8px; background: #1a1a1a; border-radius: 4px; }
            .feed-time { color: #666; }
            .feed-agent { color: #00ff88; font-weight: bold; }
            .feed-msg { color: #ccc; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🐝 HiveEngine Dashboard</h1>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value" id="scans">1,247</div>
                    <div class="stat-label">Scans Completed</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="vulns">8,934</div>
                    <div class="stat-label">Vulnerabilities Found</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="lines">2.8M+</div>
                    <div class="stat-label">Lines Scanned</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="score">72.4%</div>
                    <div class="stat-label">Avg Security Score</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="fixed">6,789</div>
                    <div class="stat-label">Vulns Fixed</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="tokens">10.6M</div>
                    <div class="stat-label">Total Tokens Used</div>
                </div>
            </div>
            
            <div class="chart-container">
                <h2>Live Agent Feed</h2>
                <div id="live-feed"></div>
            </div>
            
            <h2>Active Agents</h2>
            <div class="agent-list">
                <div class="agent-card">
                    <div class="agent-name"><span class="status-dot status-active"></span>SecurityScanner</div>
                    <div class="agent-model">MiMo v2.5-pro</div>
                    <div class="agent-tokens">2.1M tokens</div>
                </div>
                <div class="agent-card">
                    <div class="agent-name"><span class="status-dot status-active"></span>CodeQualityAgent</div>
                    <div class="agent-model">Claude Sonnet</div>
                    <div class="agent-tokens">1.8M tokens</div>
                </div>
                <div class="agent-card">
                    <div class="agent-name"><span class="status-dot status-active"></span>LogicAnalyzer</div>
                    <div class="agent-model">GPT-4 Turbo</div>
                    <div class="agent-tokens">1.2M tokens</div>
                </div>
                <div class="agent-card">
                    <div class="agent-name"><span class="status-dot status-active"></span>DependencyChecker</div>
                    <div class="agent-model">MiMo v2.5-pro</div>
                    <div class="agent-tokens">890K tokens</div>
                </div>
                <div class="agent-card">
                    <div class="agent-name"><span class="status-dot status-active"></span>SecretsHunter</div>
                    <div class="agent-model">Claude Haiku</div>
                    <div class="agent-tokens">650K tokens</div>
                </div>
            </div>
        </div>
        
        <script>
            // WebSocket for live updates
            const ws = new WebSocket('ws://localhost:8080/ws/live');
            const feed = document.getElementById('live-feed');
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                const entry = document.createElement('div');
                entry.className = 'feed-entry';
                entry.innerHTML = `
                    <span class="feed-time">[${data.time}]</span>
                    <span class="feed-agent">${data.agent}</span>
                    <span class="feed-msg">${data.message}</span>
                `;
                feed.appendChild(entry);
                feed.scrollTop = feed.scrollHeight;
            };
            
            // Fetch stats on load
            fetch('/api/stats')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('scans').textContent = data.total_scans.toLocaleString();
                    document.getElementById('vulns').textContent = data.vulnerabilities_found.toLocaleString();
                    document.getElementById('lines').textContent = (data.lines_scanned / 1000000).toFixed(1) + 'M+';
                    document.getElementById('score').textContent = data.avg_security_score + '%';
                    document.getElementById('fixed').textContent = data.vulns_fixed.toLocaleString();
                    document.getElementById('tokens').textContent = (data.total_tokens / 1000000).toFixed(1) + 'M';
                });
        </script>
    </body>
    </html>
    """


# === WebSocket ===

@app.websocket("/ws/live")
async def websocket_live(websocket: WebSocket):
    """Real-time scan updates."""
    await websocket.accept()
    live_connections.append(websocket)
    
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            
            # Handle client messages if needed
            if data == "ping":
                await websocket.send_json({"type": "pong"})
                
    except WebSocketDisconnect:
        live_connections.remove(websocket)


async def broadcast_update(agent: str, message: str):
    """Broadcast update to all connected clients."""
    update = {
        "time": datetime.now().strftime("%H:%M:%S"),
        "agent": agent,
        "message": message
    }
    
    for conn in live_connections:
        try:
            await conn.send_json(update)
        except:
            live_connections.remove(conn)


# === Main ===

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    )
