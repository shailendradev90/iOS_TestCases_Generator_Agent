"""CLI interface for the iOS Test Generator Agent."""

from __future__ import annotations

import sys
import time
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.tree import Tree

from .config import generate_default_config, load_config
from .exceptions import (
    AgentError,
    APIKeyError,
    ConfigurationError,
    LLMError,
    ProjectNotFoundError,
    RateLimitError,
    TestGenerationError,
)
from .generator import TestGenerator
from .logger import get_logger, setup_logging
from .models import AgentConfig, TestSuite
from .parser import SwiftParser
from .scanner import ProjectScanner
from .utils import count_testable_elements, format_file_summary
from .writer import TestWriter

console = Console()
logger = get_logger()


@click.group()
@click.version_option(version="1.0.0", prog_name="ios-test-gen")
def cli() -> None:
    """🧪 iOS Test Generator Agent

    Automatically generate XCTest cases for iOS projects using AI.

    Supports multiple iOS projects - point it at any Swift codebase and
    it will analyze the code structure and generate comprehensive tests.
    """
    pass


@cli.command()
@click.argument("project_path", type=click.Path(exists=True), default=".")
@click.option("--output", "-o", type=click.Path(), default=None,
              help="Output directory for generated tests.")
@click.option("--provider", type=click.Choice(["openai", "anthropic", "groq"]), default=None,
              help="LLM provider to use.")
@click.option("--model", default=None, help="LLM model name.")
@click.option("--framework", type=click.Choice(["XCTest", "SwiftTesting"]),
              default=None, help="Test framework to generate for.")
@click.option("--files", multiple=True, default=None,
              help="Specific files to generate tests for.")
@click.option("--types", multiple=True, default=None,
              help="Specific types to generate tests for.")
@click.option("--no-mocks", is_flag=True, default=None,
              help="Disable mock generation.")
@click.option("--no-setup", is_flag=True, default=None,
              help="Skip setUp/tearDown generation.")
@click.option("--dry-run", is_flag=True, default=False,
              help="Analyze project without generating tests.")
@click.option("--verbose", "-v", is_flag=True, default=False,
              help="Verbose output.")
def generate(
    project_path: str,
    output: str | None,
    provider: str | None,
    model: str | None,
    framework: str | None,
    files: tuple[str, ...],
    types: tuple[str, ...],
    no_mocks: bool | None,
    no_setup: bool | None,
    dry_run: bool,
    verbose: bool,
) -> None:
    """Generate test cases for an iOS project.

    PROJECT_PATH is the path to the iOS project root directory.
    Defaults to the current directory.
    """
    # Setup logging
    log_file = Path.cwd() / "ios-test-gen.log" if verbose else None
    setup_logging(verbose=verbose, log_file=log_file)
    
    logger.info("Starting iOS Test Generator Agent")
    
    try:
        # Build overrides from CLI args
        overrides: dict = {}
        if output:
            overrides["output_path"] = output
        if provider:
            overrides["llm_provider"] = provider
        if model:
            overrides["model"] = model
        if framework:
            overrides["test_framework"] = framework
        if files:
            overrides["target_files"] = list(files)
        if types:
            overrides["target_types"] = list(types)
        if no_mocks is not None:
            overrides["generate_mocks"] = not no_mocks
        if no_setup is not None:
            overrides["include_setup_teardown"] = not no_setup

        # Load config
        try:
            config = load_config(project_path=project_path, **overrides)
            logger.debug(f"Configuration loaded: provider={config.llm_provider}, model={config.model}")
        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration", details=str(e))

        # Print banner
        console.print()
        console.print(
            Panel.fit(
                "[bold blue]🧪 iOS Test Generator Agent[/bold blue]\n"
                f"[dim]Analyzing project at: {config.project_path}[/dim]",
                border_style="blue",
            )
        )
        console.print()

        # Step 1: Scan project
        try:
            with console.status("[bold green]Scanning project structure..."):
                scanner = ProjectScanner(config)
                project = scanner.scan()
            logger.info(f"Project scanned: {project.name}")
        except FileNotFoundError as e:
            raise ProjectNotFoundError(f"Project not found at: {project_path}", details=str(e))
        except Exception as e:
            raise AgentError("Failed to scan project", details=str(e))

        _print_project_summary(project)

        # Step 2: Parse source files
        files_to_analyze = scanner.get_files_to_analyze(project)
        if not files_to_analyze:
            console.print("[yellow]No source files found to analyze.[/yellow]")
            logger.warning("No source files found to analyze")
            return

        parser = SwiftParser(
            target_types=config.target_types if config.target_types else None
        )

        console.print()
        total_types = 0
        total_methods = 0
        total_properties = 0

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(
                f"Parsing {len(files_to_analyze)} Swift files...", total=len(files_to_analyze)
            )

            for file_path in files_to_analyze:
                swift_file = parser.parse_file(file_path)
                project.parsed_files.append(swift_file)

                for t in swift_file.types:
                    counts = count_testable_elements(t)
                    total_types += 1
                    total_methods += counts["methods"]
                    total_properties += counts["properties"]

                if verbose:
                    progress.console.print(f"  {format_file_summary(swift_file)}")

                progress.advance(task)

        # Print analysis summary
        _print_analysis_summary(
            len(files_to_analyze), total_types, total_methods, total_properties
        )

        if dry_run:
            console.print("\n[yellow]Dry run complete. No tests were generated.[/yellow]")
            logger.info("Dry run completed")
            return

        # Step 3: Generate tests
        console.print()
        generator = TestGenerator(config)
        suite = TestSuite(project_name=project.name)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            testable_files = [
                f for f in project.parsed_files if f.types
            ]
            task = progress.add_task(
                f"Generating tests for {len(testable_files)} files...",
                total=len(testable_files),
            )

            for swift_file in testable_files:
                file_label = swift_file.path.name
                type_names = [t.name for t in swift_file.types]
                progress.update(
                    task,
                    description=f"Generating tests for [cyan]{file_label}[/cyan] "
                    f"({', '.join(type_names)})...",
                )

                test_cases = generator.generate_for_file(swift_file)
                suite.test_cases.extend(test_cases)

                for tc in test_cases:
                    progress.console.print(
                        f"  ✓ Generated [green]{tc.test_class_name}[/green] "
                        f"({len(tc.test_methods)} tests)"
                    )

                progress.advance(task)

        # Step 4: Write test files
        if not suite.test_cases:
            console.print("\n[yellow]No test cases were generated.[/yellow]")
            logger.warning("No test cases were generated")
            return

        writer = TestWriter(config)
        written_files = writer.write_suite(suite)
        logger.info(f"Wrote {len(written_files)} test files")

        # Print results
        _print_results(written_files, suite)
        logger.info("Test generation completed successfully")

    except APIKeyError as e:
        console.print(f"\n[bold red]❌ API Key Error:[/bold red] {e.message}")
        console.print(f"\n[yellow]💡 Solution:[/yellow]")
        console.print(f"   Set your API key: export {e.provider.upper()}_API_KEY='your-key-here'")
        console.print(f"   Or see: GROQ_SETUP.md for detailed instructions")
        logger.error(f"API key error: {e}")
        sys.exit(1)

    except RateLimitError as e:
        console.print(f"\n[bold red]❌ Rate Limit Error:[/bold red] {e.message}")
        console.print(f"\n[yellow]💡 Solution:[/yellow]")
        console.print(f"   Wait a moment and try again")
        if e.retry_after:
            console.print(f"   Retry after: {e.retry_after} seconds")
        logger.error(f"Rate limit error: {e}")
        sys.exit(1)

    except ConfigurationError as e:
        console.print(f"\n[bold red]❌ Configuration Error:[/bold red] {e.message}")
        if e.details:
            console.print(f"   Details: {e.details}")
        console.print(f"\n[yellow]💡 Solution:[/yellow]")
        console.print(f"   Run: ios-test-gen init")
        console.print(f"   Then edit: ios-test-gen.yml")
        logger.error(f"Configuration error: {e}")
        sys.exit(1)

    except ProjectNotFoundError as e:
        console.print(f"\n[bold red]❌ Project Not Found:[/bold red] {e.message}")
        console.print(f"\n[yellow]💡 Solution:[/yellow]")
        console.print(f"   Check the project path: {project_path}")
        console.print(f"   Ensure it contains Swift source files")
        logger.error(f"Project not found: {e}")
        sys.exit(1)

    except TestGenerationError as e:
        console.print(f"\n[bold red]❌ Test Generation Error:[/bold red] {e.message}")
        if e.details:
            console.print(f"   Details: {e.details}")
        console.print(f"\n[yellow]💡 Solution:[/yellow]")
        console.print(f"   Check your API key and internet connection")
        console.print(f"   Try with --verbose for more details")
        logger.error(f"Test generation error: {e}")
        sys.exit(1)

    except AgentError as e:
        console.print(f"\n[bold red]❌ Error:[/bold red] {e.message}")
        if e.details:
            console.print(f"   Details: {e.details}")
        logger.error(f"Agent error: {e}")
        sys.exit(1)

    except KeyboardInterrupt:
        console.print("\n\n[yellow]⚠️  Operation cancelled by user[/yellow]")
        logger.info("Operation cancelled by user")
        sys.exit(130)

    except Exception as e:
        console.print(f"\n[bold red]❌ Unexpected Error:[/bold red] {str(e)}")
        console.print(f"\n[yellow]💡 Please report this issue:[/yellow]")
        console.print(f"   https://github.com/yourusername/ios-test-generator-agent/issues")
        logger.exception("Unexpected error occurred")
        if verbose:
            raise
        sys.exit(1)


@cli.command()
@click.argument("project_path", type=click.Path(exists=True), default=".")
@click.option("--verbose", "-v", is_flag=True, default=False,
              help="Show detailed file summaries.")
def analyze(project_path: str, verbose: bool) -> None:
    """Analyze an iOS project without generating tests.

    Shows project structure, source files, types, methods, and properties.
    """
    config = load_config(project_path=project_path)

    console.print()
    console.print(
        Panel.fit(
            "[bold blue]📊 Project Analysis[/bold blue]\n"
            f"[dim]Project: {config.project_path}[/dim]",
            border_style="blue",
        )
    )

    # Scan
    with console.status("[bold green]Scanning..."):
        scanner = ProjectScanner(config)
        project = scanner.scan()

    _print_project_summary(project)

    # Parse
    files_to_analyze = scanner.get_files_to_analyze(project)
    parser = SwiftParser()

    console.print()
    tree = Tree("[bold]📁 Source Files[/bold]")

    total_types = 0
    total_methods = 0
    total_properties = 0

    for file_path in files_to_analyze:
        swift_file = parser.parse_file(file_path)
        project.parsed_files.append(swift_file)

        if swift_file.types or swift_file.top_level_functions:
            file_node = tree.add(f"[cyan]{file_path.name}[/cyan]")
            if swift_file.imports:
                file_node.add(f"[dim]Imports: {', '.join(swift_file.imports)}[/dim]")

            for t in swift_file.types:
                counts = count_testable_elements(t)
                total_types += 1
                total_methods += counts["methods"]
                total_properties += counts["properties"]

                if verbose:
                    file_node.add(format_type_summary_rich(t))
                else:
                    summary = (
                        f"{t.kind.value} [bold]{t.name}[/bold] "
                        f"({counts['methods']}m, {counts['properties']}p, "
                        f"{counts['enum_cases']}ec)"
                    )
                    file_node.add(summary)

    console.print(tree)

    # Summary table
    table = Table(title="Analysis Summary", show_header=False)
    table.add_column("Metric", style="bold")
    table.add_column("Count", justify="right")
    table.add_row("Source Files", str(len(files_to_analyze)))
    table.add_row("Types (classes/structs/enums)", str(total_types))
    table.add_row("Methods", str(total_methods))
    table.add_row("Properties", str(total_properties))
    table.add_row(
        "Testable Elements",
        str(total_types + total_methods + total_properties),
    )
    console.print()
    console.print(table)


@cli.command("init")
@click.argument("path", type=click.Path(), default=".")
def init_config(path: str) -> None:
    """Initialize a default configuration file.

    Creates an ios-test-gen.yml file with default settings.
    """
    config_path = Path(path) / "ios-test-gen.yml"

    if config_path.exists():
        if not click.confirm(f"Config file already exists at {config_path}. Overwrite?"):
            return

    generate_default_config(config_path)
    console.print(f"[green]✓[/green] Configuration file created at: {config_path}")
    console.print("  Edit the file to customize settings for your project.")


# ──────────────────────────────────────────────
# Helper functions
# ──────────────────────────────────────────────


def format_type_summary_rich(swift_type, indent: int = 0) -> str:
    """Format type summary with rich markup."""
    from .models import SwiftDeclarationKind

    kind = swift_type.kind.value
    inheritance = ""
    if swift_type.superclasses:
        inheritance += ": " + ", ".join(swift_type.superclasses)
    if swift_type.conformances:
        sep = ", " if swift_type.superclasses else ": "
        inheritance += sep + ", ".join(swift_type.conformances)

    lines = [f"{kind} [bold]{swift_type.name}[/bold]{inheritance}"]

    for prop in swift_type.properties:
        let_or_var = "let" if prop.is_let else "var"
        static = "[yellow]static[/yellow] " if prop.is_static else ""
        lines.append(f"  {static}{let_or_var} [dim]{prop.name}[/dim]: {prop.type}")

    for case in swift_type.enum_cases:
        raw = f" = {case.raw_value}" if case.raw_value else ""
        lines.append(f"  case [green]{case.name}[/green]{raw}")

    for method in swift_type.methods:
        kind_marker = ""
        if method.kind.value in ("static", "class"):
            kind_marker = f"[yellow]{method.kind.value}[/yellow] "
        async_m = "[magenta]async[/magenta] " if method.is_async else ""
        throw_m = "[red]throws[/red] " if method.is_throwing else ""
        ret = f" -> {method.return_type}" if method.return_type else ""
        params = ", ".join(p.to_signature() for p in method.parameters)
        lines.append(
            f"  {kind_marker}func [blue]{method.name}[/blue]({params}) "
            f"{async_m}{throw_m}{ret}".rstrip()
        )

    return "\n".join(lines)


def _print_project_summary(project) -> None:
    """Print project summary."""
    table = Table(title="Project Info", show_header=False, box=None)
    table.add_column("Key", style="bold")
    table.add_column("Value")

    table.add_row("Name", project.name)
    table.add_row("Root", str(project.root_path))
    table.add_row("Source Files", str(len(project.source_files)))
    table.add_row("Existing Tests", str(len(project.test_files)))

    if project.xcodeproj_path:
        table.add_row("Xcode Project", project.xcodeproj_path.name)
    if project.package_swift_path:
        table.add_row("Swift Package", "✓")

    console.print(table)


def _print_analysis_summary(
    file_count: int, type_count: int, method_count: int, prop_count: int
) -> None:
    """Print analysis summary."""
    console.print()
    table = Table(title="Analysis Results", show_header=False)
    table.add_column("Metric", style="bold")
    table.add_column("Count", justify="right", style="cyan")
    table.add_row("Files Analyzed", str(file_count))
    table.add_row("Types Found", str(type_count))
    table.add_row("Methods Found", str(method_count))
    table.add_row("Properties Found", str(prop_count))
    console.print(table)


def _print_results(written_files: list[Path], suite: TestSuite) -> None:
    """Print generation results."""
    console.print()

    # Results table
    table = Table(title="Generated Test Files")
    table.add_column("#", justify="right", style="dim")
    table.add_column("Test Class", style="green")
    table.add_column("Source Type", style="cyan")
    table.add_column("Tests", justify="right")

    for i, tc in enumerate(suite.test_cases, 1):
        table.add_row(
            str(i),
            tc.test_class_name,
            tc.source_type_name,
            str(len(tc.test_methods)),
        )

    console.print(table)

    # Summary
    total_tests = sum(len(tc.test_methods) for tc in suite.test_cases)
    console.print()
    console.print(
        Panel.fit(
            f"[bold green]✅ Done![/bold green]\n"
            f"Generated [bold]{len(written_files)}[/bold] test files "
            f"with [bold]{total_tests}[/bold] test methods.\n"
            f"[dim]Output: {written_files[0].parent if written_files else 'N/A'}[/dim]",
            border_style="green",
        )
    )