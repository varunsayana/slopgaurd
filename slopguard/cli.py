"""
CLI endpoints for SlopGuard.
"""

import typer
import sys
from rich.console import Console
from typing import Optional
import json

from slopguard.config import SlopGuardConfig
from slopguard.models import RunContext
from slopguard.engine.analyzer import Analyzer
from slopguard.formatters import get_formatter

app = typer.Typer(
    name="slopguard",
    help="A PR quality and production-slop detector to stop bad patches before merge.",
    add_completion=False,
)
console = Console()


@app.command()
def analyze(
    repo: str = typer.Option(".", help="Path to the repository root."),
    base: Optional[str] = typer.Option(None, help="Base git ref for diff comparison."),
    head: Optional[str] = typer.Option(
        "HEAD", help="Head git ref for diff comparison."
    ),
    staged: bool = typer.Option(False, "--staged", help="Analyze staged changes only."),
    patch: Optional[str] = typer.Option(None, help="Path to a diff patch file."),
    output_format: str = typer.Option(
        "text", help="Output format: text, json, sarif, github"
    ),
):
    """
    Analyze the repository or patch for slop.
    """
    config = SlopGuardConfig.load()
    context = RunContext(
        repo_path=repo,
        base_ref=base,
        head_ref=head,
        is_staged_only=staged,
        patch_file=patch,
    )

    analyzer = Analyzer(config, context)
    results = analyzer.run()

    formatter = get_formatter(output_format)
    formatted_output = formatter.format(results)

    if output_format != "text":
        print(formatted_output)

    # Fail CI if score drops below threshold
    if config.ci.fail_on_error and results.get("score", 100) < config.ci.fail_on_score:
        sys.exit(1)


@app.command()
def explain(rule_id: str):
    """
    Explain a given rule ID.
    """
    from slopguard.rules import registry

    if rule_id in registry:
        # Instantiate with empty config just to read metadata
        instance = registry[rule_id]({})
        dummy_findings = instance.evaluate("dummy.py", "", None, None)
        fnd = dummy_findings[0] if dummy_findings else None

        console.print(f"\n[bold magenta]Rule ID:[/bold magenta] {rule_id}")
        if fnd:
            console.print(
                f"[bold cyan]Category:[/bold cyan] {', '.join(c.value for c in fnd.categories)}"
            )
            console.print(
                f"[bold red]Default Severity:[/bold red] {fnd.severity.upper()}"
            )
            console.print("\n[bold]What it detects:[/bold]")
            console.print(fnd.short_explanation)
            console.print("\n[bold]Why it matters:[/bold]")
            console.print(fnd.why_it_matters)
            console.print("\n[bold]Suggested Remediation:[/bold]")
            console.print(fnd.suggested_remediation)
        console.print("")
    else:
        console.print(f"Rule '{rule_id}' not found.", style="red")


@app.command()
def rules(action: str = typer.Argument("list", help="list or show <rule_id>")):
    """
    Manage and display rules.
    """
    from slopguard.rules import registry

    if action == "list":
        console.print("Available Rules:")
        for r in registry.keys():
            console.print(f" - {r}")


@app.command()
def config(action: str = typer.Argument("init", help="init to generate config")):
    """
    Manage configuration.
    """
    if action == "init":
        conf = SlopGuardConfig()
        conf.save()
        console.print(
            "[green]Created .slopguard.yml with default configuration.[/green]"
        )


@app.command()
def autofix(
    safe: bool = typer.Option(True, "--safe", help="Only apply 100% safe fixes.")
):
    """
    Apply safe automatic fixes to unambiguous slop findings.
    """
    console.print("[yellow]Autofix is experimental. Scaffolding built...[/yellow]")


if __name__ == "__main__":
    app()

