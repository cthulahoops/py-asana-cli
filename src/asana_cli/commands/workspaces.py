"""Workspace commands."""

from typing import Annotated

import typer

from asana_cli.client import AsanaClient, ConfigurationError
from asana_cli.config import set_workspace
from asana_cli.utils import OutputFormat, console, format_output

app = typer.Typer(no_args_is_help=True)


@app.command("list")
def cmd_list(
    output: Annotated[
        OutputFormat, typer.Option("--output", "-o", help="Output format")
    ] = OutputFormat.TABLE,
) -> None:
    """List available workspaces."""
    try:
        with AsanaClient() as client:
            workspaces = client.get_workspaces(opt_fields=["gid", "name"])

        format_output(
            workspaces,
            output,
            columns=[("gid", "GID"), ("name", "Name")],
            title="Workspaces",
        )
    except ConfigurationError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command("select")
def cmd_select(
    workspace_gid: Annotated[
        str | None, typer.Argument(help="Workspace GID to select")
    ] = None,
) -> None:
    """Select a workspace as default (interactive if no GID provided)."""
    try:
        with AsanaClient() as client:
            workspaces = client.get_workspaces(opt_fields=["gid", "name"])

        if not workspaces:
            console.print("[yellow]No workspaces found.[/yellow]")
            raise typer.Exit(1)

        if workspace_gid:
            # Verify the workspace exists
            workspace = next((w for w in workspaces if w["gid"] == workspace_gid), None)
            if not workspace:
                console.print(f"[red]Workspace {workspace_gid} not found.[/red]")
                raise typer.Exit(1)
        else:
            # Interactive selection
            console.print("[bold]Available workspaces:[/bold]")
            for i, ws in enumerate(workspaces, 1):
                console.print(f"  {i}. {ws['name']} ({ws['gid']})")

            console.print()
            choice = typer.prompt("Select workspace number", type=int)

            if choice < 1 or choice > len(workspaces):
                console.print("[red]Invalid selection.[/red]")
                raise typer.Exit(1)

            workspace = workspaces[choice - 1]
            workspace_gid = workspace["gid"]

        set_workspace(workspace_gid)
        workspace_name = next(
            (w["name"] for w in workspaces if w["gid"] == workspace_gid), workspace_gid
        )
        console.print(f"[green]Selected workspace: {workspace_name}[/green]")

    except ConfigurationError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
