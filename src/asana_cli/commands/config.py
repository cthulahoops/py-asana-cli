"""Configuration commands."""

from typing import Annotated

import typer

from asana_cli.config import get_token, get_workspace, load_config, set_token, set_workspace
from asana_cli.utils import console

app = typer.Typer(no_args_is_help=True)


@app.command("set-token")
def cmd_set_token(
    token: Annotated[str, typer.Argument(help="Asana Personal Access Token")],
) -> None:
    """Set the Asana API token."""
    set_token(token)
    console.print("[green]Token saved successfully.[/green]")


@app.command("set-workspace")
def cmd_set_workspace(
    workspace_gid: Annotated[str, typer.Argument(help="Workspace GID to use as default")],
) -> None:
    """Set the default workspace."""
    set_workspace(workspace_gid)
    console.print(f"[green]Default workspace set to {workspace_gid}.[/green]")


@app.command("show")
def cmd_show() -> None:
    """Show current configuration."""
    config = load_config()
    token = get_token()
    workspace = get_workspace()

    console.print("[bold]Current Configuration:[/bold]")
    console.print()

    if token:
        masked_token = f"{token[:8]}...{token[-4:]}" if len(token) > 12 else "****"
        console.print(f"[bold]Token:[/bold] {masked_token}")
    else:
        console.print("[bold]Token:[/bold] [dim]Not set[/dim]")

    if workspace:
        console.print(f"[bold]Default Workspace:[/bold] {workspace}")
    else:
        console.print("[bold]Default Workspace:[/bold] [dim]Not set[/dim]")

    # Show source of config
    console.print()
    if config.get("token"):
        console.print("[dim]Token source: config file[/dim]")
    elif token:
        console.print("[dim]Token source: ASANA_TOKEN environment variable[/dim]")
