import sys
import json
import argparse
from typing import Optional
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / ".env")
except ImportError:
    pass

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

from src.engine import PromptValidator
from src.models import Severity

console = Console()


def print_banner():
    banner = Text()
    banner.append("🏛️  FAIR HOUSING & LENDING PROMPT VALIDATOR\n", style="bold cyan")
    banner.append("Audits prompts against FHA, ECOA, CRA, HMDA, HUD rules & landmark precedents", style="italic dim")
    console.print(Panel(banner, border_style="cyan", box=box.ROUNDED))


def format_audit_result(result, verbose: bool = True):
    if result.is_compliant:
        status_panel = Panel(
            Text(f"✅ PASSED COMPLIANCE AUDIT\nRisk Score: 0.00 / 1.00\n{result.summary}", style="bold green"),
            border_style="green",
            box=box.ROUNDED
        )
        console.print(status_panel)
        return

    # Non-compliant result
    sev_style = "bold red" if result.overall_severity == Severity.CRITICAL else "bold yellow"
    status_text = (
        f"❌ NON-COMPLIANT / VIOLATIONS DETECTED\n"
        f"Overall Severity: {result.overall_severity.value if result.overall_severity else 'HIGH'} | "
        f"Risk Score: {result.risk_score:.2f} / 1.00\n"
        f"{result.summary}"
    )
    console.print(Panel(status_text, style=sev_style, border_style="red", box=box.ROUNDED))

    # Violations Table
    table = Table(title="Identified Legal Violations", box=box.HEAVY_EDGE, border_style="bright_blue")
    table.add_column("Category", style="cyan", no_wrap=False)
    table.add_column("Law & Citation", style="magenta")
    table.add_column("Variable", style="blue")
    table.add_column("Flagged Span", style="bold red")
    table.add_column("Severity", style="yellow")

    for v in result.violations:
        cat_str = v.category.value if hasattr(v.category, "value") else str(v.category)
        var_str = v.protected_variable.value if hasattr(v.protected_variable, "value") else str(v.protected_variable)
        sev_color = "red" if v.severity == Severity.CRITICAL else ("yellow" if v.severity == Severity.HIGH else "white")
        table.add_row(
            cat_str,
            f"{v.law_cited}\n({v.statutory_reference})",
            var_str,
            v.flagged_text or "[Implicit/Proxy]",
            f"[{sev_color}]{v.severity.value}[/{sev_color}]"
        )

    console.print(table)

    # Explanation & Remediation for each violation
    if verbose:
        for idx, v in enumerate(result.violations, 1):
            detail = (
                f"[bold cyan]Explanation:[/bold cyan] {v.explanation}\n"
                f"[bold green]Legal Remediation Guidance:[/bold green] {v.remediation_guidance}"
            )
            console.print(Panel(detail, title=f"Violation #{idx} Details", border_style="yellow", box=box.ROUNDED))

    # Suggested Rewrite
    if result.suggested_compliant_prompt:
        rewrite_panel = Panel(
            Text(result.suggested_compliant_prompt, style="bold green"),
            title="💡 Recommended Compliant Prompt Rewrite",
            border_style="green",
            box=box.ROUNDED
        )
        console.print(rewrite_panel)


def cmd_audit(args):
    print_banner()
    prompt = args.prompt
    console.print(f"\n[bold]Input Prompt:[/bold]\n\"{prompt}\"\n", style="white")

    validator = PromptValidator(gemini_api_key=args.api_key)
    with console.status("[bold cyan]Running multi-tier compliance audit...", spinner="dots"):
        result = validator.validate(
            prompt=prompt,
            context=args.context,
            enable_semantic=not args.no_semantic,
            api_key_override=args.api_key
        )

    if args.json:
        print(result.model_dump_json(indent=2))
    else:
        format_audit_result(result, verbose=not args.concise)


def cmd_benchmark(args):
    print_banner()
    benchmark_path = Path(__file__).parent.parent / "tests" / "benchmark_cases.json"
    if not benchmark_path.exists():
        console.print(f"[red]Benchmark file not found at: {benchmark_path}[/red]")
        sys.exit(1)

    with open(benchmark_path, "r", encoding="utf-8") as f:
        cases = json.load(f)

    validator = PromptValidator(gemini_api_key=args.api_key)
    table = Table(title=f"Running {len(cases)} Legal Benchmark Cases", box=box.ROUNDED)
    table.add_column("Case ID", style="cyan")
    table.add_column("Expected", style="magenta")
    table.add_column("Actual", style="blue")
    table.add_column("Risk", style="yellow")
    table.add_column("Result", style="bold")

    passed_count = 0
    with console.status("[bold cyan]Executing benchmark suite...", spinner="dots"):
        for case in cases:
            res = validator.validate(case["prompt"], enable_semantic=False)
            expected = "Compliant" if case["expected_compliant"] else "Non-Compliant"
            actual = "Compliant" if res.is_compliant else "Non-Compliant"
            status = res.is_compliant == case["expected_compliant"]

            if status:
                passed_count += 1
                res_cell = "[bold green]PASS[/bold green]"
            else:
                res_cell = "[bold red]FAIL[/bold red]"

            table.add_row(
                case["id"],
                expected,
                actual,
                f"{res.risk_score:.2f}",
                res_cell
            )

    console.print(table)
    pct = (passed_count / len(cases)) * 100
    console.print(Panel(
        f"[bold]Benchmark Summary:[/bold] {passed_count}/{len(cases)} cases passed ([bold green]{pct:.1f}%[/bold green])",
        border_style="green" if passed_count == len(cases) else "yellow"
    ))


def cmd_serve(args):
    print_banner()
    console.print(f"[bold green]Starting Web UI Dashboard on http://{args.host}:{args.port} ...[/bold green]")
    import uvicorn
    uvicorn.run("web.app:app", host=args.host, port=args.port, reload=args.reload)


def main():
    parser = argparse.ArgumentParser(
        description="Housing & Lending Discrimination Prompt Validation Tool"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: audit
    p_audit = subparsers.add_parser("audit", help="Audit a prompt for discrimination violations")
    p_audit.add_argument("prompt", type=str, help="Prompt text to validate")
    p_audit.add_argument("--context", type=str, default="general", help="Context: rental_listing, mortgage_underwriting, etc.")
    p_audit.add_argument("--api-key", type=str, default=None, help="Gemini API Key for semantic checks")
    p_audit.add_argument("--no-semantic", action="store_true", help="Disable remote LLM semantic checks (fast offline mode)")
    p_audit.add_argument("--json", action="store_true", help="Output raw JSON format")
    p_audit.add_argument("--concise", action="store_true", help="Show concise violation output")
    p_audit.set_defaults(func=cmd_audit)

    # Subcommand: benchmark
    p_bench = subparsers.add_parser("benchmark", help="Run compliance benchmark suite")
    p_bench.add_argument("--api-key", type=str, default=None, help="Gemini API Key")
    p_bench.set_defaults(func=cmd_benchmark)

    # Subcommand: serve
    p_serve = subparsers.add_parser("serve", help="Launch the interactive Web UI Dashboard")
    p_serve.add_argument("--host", type=str, default="127.0.0.1", help="Host interface")
    p_serve.add_argument("--port", type=int, default=8000, help="Port to bind")
    p_serve.add_argument("--reload", action="store_true", help="Auto-reload on code change")
    p_serve.set_defaults(func=cmd_serve)

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
