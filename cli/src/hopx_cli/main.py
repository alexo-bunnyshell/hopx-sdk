"""Main Typer application and command routing for Hopx CLI."""

import sys

import typer
from rich.console import Console
from rich.table import Table

from hopx_cli import __version__
from hopx_cli.core import CLIConfig, CLIContext, OutputFormat


def version_callback(value: bool) -> None:
    """Callback to handle --version flag."""
    if value:
        typer.echo(f"hopx {__version__}")
        raise typer.Exit()


def _print_epilog() -> None:
    """Print the help epilog with proper formatting using Rich."""
    console = Console()

    # Aliases table
    aliases_table = Table(
        show_header=False,
        box=None,
        padding=(0, 2, 0, 0),
        collapse_padding=True,
    )
    aliases_table.add_column("alias", style="cyan")
    aliases_table.add_column("arrow", style="dim")
    aliases_table.add_column("command", style="green")
    aliases_table.add_column("description", style="dim")

    aliases_table.add_row("sb", "→", "sandbox", "Manage sandboxes")
    aliases_table.add_row("tpl", "→", "template", "Manage templates")
    aliases_table.add_row("f", "→", "files", "File operations")
    aliases_table.add_row("term", "→", "terminal", "Interactive terminals")

    console.print()
    console.print("[bold]Aliases:[/bold]")
    console.print(aliases_table)

    # Quick Start table
    quick_start_table = Table(
        show_header=False,
        box=None,
        padding=(0, 2, 0, 0),
        collapse_padding=True,
    )
    quick_start_table.add_column("command", style="cyan")
    quick_start_table.add_column("description", style="dim")

    quick_start_table.add_row("hopx auth login", "Authenticate with browser")
    quick_start_table.add_row("hopx auth keys create", "Create and store API key")
    quick_start_table.add_row("hopx sandbox create", "Create a new sandbox")
    quick_start_table.add_row('hopx run "print(1)"', "Run code in sandbox")

    console.print()
    console.print("[bold]Quick Start:[/bold]")
    console.print(quick_start_table)

    console.print()
    console.print("[dim]Docs: https://docs.hopx.dev | Support: support@hopx.ai[/dim]")


class HopxTyper(typer.Typer):
    """Custom Typer class that adds epilog after help output."""

    def __call__(self, *args: object, **kwargs: object) -> None:
        """Override to add epilog when --help is used."""
        # Check if --help is in sys.argv and we're at the root command
        if "--help" in sys.argv and len([a for a in sys.argv[1:] if not a.startswith("-")]) == 0:
            # This is `hopx --help`, not `hopx <subcommand> --help`
            try:
                super().__call__(*args, **kwargs)
            except SystemExit as e:
                _print_epilog()
                raise e
        else:
            super().__call__(*args, **kwargs)


app = HopxTyper(
    name="hopx",
    help="Hopx CLI - Manage cloud sandboxes from the command line",
    no_args_is_help=True,
    rich_markup_mode="rich",
    add_completion=True,
)


@app.callback()
def main(
    ctx: typer.Context,
    api_key: str | None = typer.Option(
        None,
        "--api-key",
        envvar="HOPX_API_KEY",
        help="API key (overrides HOPX_API_KEY env var)",
    ),
    profile: str = typer.Option(
        "default",
        "--profile",
        envvar="HOPX_PROFILE",
        help="Configuration profile to use",
    ),
    output: OutputFormat = typer.Option(
        OutputFormat.TABLE,
        "--output",
        "-o",
        help="Output format",
        case_sensitive=False,
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        help="Suppress non-essential output",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Increase output verbosity",
    ),
    no_color: bool = typer.Option(
        False,
        "--no-color",
        envvar="NO_COLOR",
        help="Disable colored output",
    ),
    version: bool = typer.Option(
        False,
        "--version",
        help="Show version and exit",
        is_eager=True,
        callback=version_callback,
    ),
) -> None:
    """
    Global options for all commands.

    These options are available to all subcommands via the context object.
    """
    # Load configuration (will read from .env and config file)
    config = CLIConfig()

    # Override API key if provided via flag
    if api_key:
        config = CLIConfig(api_key=api_key, profile=profile)

    # Create CLI context with proper object
    cli_ctx = CLIContext(
        config=config,
        output_format=output,
        verbose=verbose,
        quiet=quiet,
        no_color=no_color,
    )

    # Store context for subcommands
    ctx.obj = cli_ctx


# Import command groups
from hopx_cli.commands import (
    auth,
    billing,
    cmd,
    env,
    files,
    init,
    members,
    org,
    profile,
    run,
    sandbox,
    self_update,
    system,
    template,
    terminal,
    usage,
)
from hopx_cli.commands import config as config_cmd

# Register subcommands with primary names
app.add_typer(init.app, name="init", help="First-run setup wizard")
app.add_typer(system.app, name="system", help="System and health commands")
app.add_typer(run.app, name="run", help="Execute code in sandboxes")
app.add_typer(auth.app, name="auth", help="Authentication management")
app.add_typer(sandbox.app, name="sandbox", help="Manage sandboxes")
app.add_typer(sandbox.app, name="sb", hidden=True)  # Alias
app.add_typer(template.app, name="template", help="Manage templates")
app.add_typer(template.app, name="tpl", hidden=True)  # Alias
app.add_typer(config_cmd.app, name="config", help="Configuration management")
app.add_typer(files.app, name="files", help="File operations")
app.add_typer(files.app, name="f", hidden=True)  # Alias
app.add_typer(cmd.app, name="cmd", help="Run shell commands in sandboxes")
app.add_typer(env.app, name="env", help="Manage environment variables")
app.add_typer(terminal.app, name="terminal", help="Interactive terminal sessions")
app.add_typer(terminal.app, name="term", hidden=True)  # Alias
app.add_typer(org.app, name="org", help="Manage organization settings")
app.add_typer(usage.app, name="usage", help="View usage statistics")
app.add_typer(profile.app, name="profile", help="Manage user profile")
app.add_typer(members.app, name="members", help="Manage organization members")
app.add_typer(billing.app, name="billing", help="View billing information")
app.add_typer(self_update.app, name="self-update", help="Update CLI to latest version")
