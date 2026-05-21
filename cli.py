#!/usr/bin/env python3
"""
HiveEngine CLI — Command-line interface for running security scans.
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from core.orchestrator import AgentOrchestrator
from core.event_bus import EventBus
from core.analytics import UsageAnalytics


console = Console()


def display_banner():
    """Display the HiveEngine banner."""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║   🐝 HiveEngine — Multi-Agent Security Scanner           ║
    ║                                                           ║
    ║   10+ AI agents • Parallel execution • Real-time results  ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    console.print(Panel(banner, style="bold green"))


def display_stats(analytics: UsageAnalytics):
    """Display usage statistics."""
    stats = analytics.get_stats()
    
    table = Table(title="📊 Usage Statistics")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Total Scans", f"{stats['total_scans']:,}")
    table.add_row("Vulnerabilities Found", f"{stats['vulnerabilities_found']:,}")
    table.add_row("Lines Scanned", f"{stats['lines_scanned']:,}")
    table.add_row("Avg Security Score", f"{stats['avg_security_score']}%")
    table.add_row("Vulns Fixed", f"{stats['vulns_fixed']:,}")
    table.add_row("Total Tokens", f"{stats['total_tokens']:,}")
    table.add_row("Total Cost", f"${stats['total_cost_usd']:.2f}")
    
    console.print(table)


def display_findings(findings: list):
    """Display scan findings."""
    if not findings:
        console.print("[green]✅ No vulnerabilities found![/green]")
        return
    
    table = Table(title="🔍 Findings")
    table.add_column("Severity", style="bold")
    table.add_column("Type")
    table.add_column("File")
    table.add_column("Line")
    table.add_column("Description")
    
    severity_styles = {
        "critical": "red",
        "high": "yellow",
        "medium": "blue",
        "low": "green"
    }
    
    for finding in findings:
        severity = finding.get("severity", "unknown")
        style = severity_styles.get(severity, "white")
        
        table.add_row(
            f"[{style}]{severity.upper()}[/{style}]",
            finding.get("type", ""),
            finding.get("file", ""),
            str(finding.get("line", "")),
            finding.get("description", "")[:50]
        )
    
    console.print(table)


async def run_scan(repo: str, agents: list, depth: str):
    """Run a security scan."""
    event_bus = EventBus()
    orchestrator = AgentOrchestrator(event_bus)
    analytics = UsageAnalytics()
    
    console.print(f"\n[bold]🔍 Scanning: {repo}[/bold]")
    console.print(f"[dim]Agents: {', '.join(agents)}[/dim]")
    console.print(f"[dim]Depth: {depth}[/dim]\n")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Running agents...", total=None)
        
        # Run scan
        scan_id = f"cli_{int(asyncio.get_event_loop().time())}"
        await orchestrator.run_scan(scan_id, repo, agents, depth)
        
        progress.update(task, description="✅ Scan complete!")
    
    # Get results
    result = orchestrator.get_scan(scan_id)
    if result:
        display_findings(result.get("findings", []))
        
        # Record in analytics
        analytics.record_scan({
            "scan_id": scan_id,
            "repo": repo,
            "findings_count": len(result.get("findings", [])),
            "security_score": result.get("metrics", {}).get("security_score", 0),
            "tokens_used": result.get("metrics", {}).get("tokens_used", 0)
        })


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="HiveEngine — Multi-Agent Security Scanner"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Scan command
    scan_parser = subparsers.add_parser("scan", help="Run a security scan")
    scan_parser.add_argument("repo", help="Repository path or URL")
    scan_parser.add_argument(
        "--agents", 
        nargs="+",
        default=["security", "quality", "logic", "deps", "secrets"],
        help="Agents to run"
    )
    scan_parser.add_argument(
        "--depth",
        choices=["quick", "targeted", "full"],
        default="full",
        help="Scan depth"
    )
    scan_parser.add_argument(
        "--output",
        help="Output file for results (JSON)"
    )
    
    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show usage statistics")
    
    # History command
    history_parser = subparsers.add_parser("history", help="Show scan history")
    history_parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Number of scans to show"
    )
    
    # Export command
    export_parser = subparsers.add_parser("export", help="Export usage report")
    export_parser.add_argument(
        "--format",
        choices=["json", "csv"],
        default="json",
        help="Export format"
    )
    export_parser.add_argument(
        "--output",
        default="report.json",
        help="Output file"
    )
    
    args = parser.parse_args()
    
    display_banner()
    
    if args.command == "scan":
        asyncio.run(run_scan(args.repo, args.agents, args.depth))
    elif args.command == "stats":
        analytics = UsageAnalytics()
        display_stats(analytics)
    elif args.command == "history":
        analytics = UsageAnalytics()
        history = analytics.get_history(args.limit)
        
        table = Table(title="📜 Scan History")
        table.add_column("Scan ID")
        table.add_column("Timestamp")
        table.add_column("Findings")
        table.add_column("Score")
        
        for scan in history:
            table.add_row(
                scan.get("scan_id", ""),
                scan.get("timestamp", "")[:19],
                str(scan.get("findings", 0)),
                f"{scan.get('score', 0)}%"
            )
        
        console.print(table)
    elif args.command == "export":
        analytics = UsageAnalytics()
        report = analytics.export_report(args.format)
        
        with open(args.output, 'w') as f:
            f.write(report)
        
        console.print(f"[green]✅ Report exported to {args.output}[/green]")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
