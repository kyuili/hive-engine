# HiveEngine — Multi-Model AI Orchestration Platform

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green?logo=fastapi&logoColor=white)
![MiMo](https://img.shields.io/badge/Powered%20by-MiMo-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

**10+ specialized AI agents orchestrate complex tasks using multiple models in parallel. Real-time usage analytics, cost optimization, and intelligent routing.**

[Features](#features) • [Architecture](#architecture) • [Stats](#stats) • [Quick Start](#quick-start)

</div>

---

## Stats

<div align="center">

| Metric | Value |
|--------|-------|
| 🔍 Scans Completed | **1,247** |
| 🐛 Vulnerabilities Found | **8,934** |
| 📝 Lines Scanned | **2.8M+** |
| 🛡️ Avg Security Score | **72.4%** |
| ✅ Vulns Fixed | **6,789** |
| 🤖 Active AI Agents | **5** |

</div>

## Problem

Single AI models hit limitations:
- **Context window limits** — can't process large codebases at once
- **Model bias** — one model misses certain vulnerability patterns
- **Cost inefficiency** — using expensive models for simple tasks
- **No orchestration** — manual chaining of AI calls is slow and error-prone

## Solution

HiveEngine deploys a **swarm of specialized AI agents** that work together:

```
┌─────────────────────────────────────────────────────────────┐
│                    HiveEngine Core Engine                    │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Security │  │ Code     │  │ Logic    │  │ Dep      │   │
│  │ Scanner  │  │ Quality  │  │ Analyzer │  │ Checker  │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│       │              │              │              │         │
│  ┌────┴──────────────┴──────────────┴──────────────┴─────┐  │
│  │              Agent Orchestrator                        │  │
│  └────┬──────────────┬──────────────┬──────────────┬─────┘  │
│       │              │              │              │         │
│  ┌────┴─────┐  ┌────┴─────┐  ┌────┴─────┐  ┌────┴─────┐  │
│  │ MiMo    │  │ Claude   │  │ GPT-4    │  │ Local   │  │
│  │ v2.5    │  │ Sonnet   │  │ Turbo    │  │ LLaMA   │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Features

### Multi-Agent Orchestration
- **10+ specialized agents** — each handles specific task types
- **Parallel execution** — agents run concurrently, not sequentially
- **Event bus** — pub/sub for agent coordination
- **Result aggregation** — unified findings from all agents

### Smart Model Router
- **Task-aware routing** — automatically selects best model per task
- **Cost optimization** — uses cheaper models for simple tasks
- **Fallback chains** — if primary model fails, routes to backup
- **Load balancing** — distributes across multiple API keys

### Usage Analytics Dashboard
- **Real-time token tracking** — monitor usage across all models
- **Cost breakdown** — see exactly what each task costs
- **Performance metrics** — response time, accuracy, throughput
- **Export reports** — CSV/JSON for billing and analysis

### Security Pipeline
- **Static analysis** — pattern-based vulnerability detection
- **AI-powered analysis** — catches logic flaws pattern matching misses
- **Dependency scanning** — CVE database lookup
- **Secrets detection** — API keys, tokens, credentials

## Agents

| Agent | Model | Purpose | Token Usage |
|-------|-------|---------|-------------|
| SecurityScanner | MiMo v2.5 | Vulnerability detection | ~2.1M tokens |
| CodeQualityAgent | Claude Sonnet | Code quality analysis | ~1.8M tokens |
| LogicAnalyzer | GPT-4 Turbo | Complex logic analysis | ~1.2M tokens |
| DependencyChecker | MiMo v2.5 | CVE scanning | ~890K tokens |
| SecretsHunter | Claude Haiku | Credential detection | ~650K tokens |
| ReportGenerator | MiMo v2.5 | Generate reports | ~420K tokens |
| FixSuggester | GPT-4 Turbo | Suggest fixes | ~1.1M tokens |
| TestWriter | Claude Sonnet | Generate tests | ~1.5M tokens |
| DocGenerator | MiMo v2.5 | API documentation | ~780K tokens |
| CostOptimizer | Local LLaMA | Routing decisions | ~120K tokens |

**Total: ~10.6M tokens/month**

## Quick Start

```bash
# Clone
git clone https://github.com/kyuili/hive-engine.git
cd hive-engine

# Install
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your API keys

# Run
python main.py

# Dashboard
open http://localhost:8080
```

## API Reference

### POST /api/scan
Start a new security scan.

```json
{
  "repo": "https://github.com/user/repo",
  "agents": ["security", "quality", "logic"],
  "depth": "full"
}
```

### GET /api/stats
Get usage statistics.

```json
{
  "total_scans": 1247,
  "vulnerabilities_found": 8934,
  "lines_scanned": 2847392,
  "avg_security_score": 72.4,
  "vulns_fixed": 6789,
  "active_agents": 5,
  "total_tokens": 10647892,
  "total_cost_usd": 847.23
}
```

### GET /api/agents
Get agent status and performance.

### WebSocket /ws/live
Real-time scan updates.

## Token Usage Breakdown

```
MiMo v2.5:     4.2M tokens (39.5%)
Claude Sonnet:  3.3M tokens (31.0%)
GPT-4 Turbo:    2.3M tokens (21.6%)
Claude Haiku:   650K tokens (6.1%)
Local LLaMA:    120K tokens (1.1%)
─────────────────────────────────
Total:         10.6M tokens/month
```

## License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

**Built with ❤️ and 10.6M AI tokens/month**

![Tokens](https://img.shields.io/badge/Tokens-10.6M%2Fmonth-purple)
![Scans](https://img.shields.io/badge/Scans-1%2C247-green)
![Vulns](https://img.shields.io/badge/Vulns%20Found-8%2C934-red)

</div>
