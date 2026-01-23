"""Project commands."""

from typing import Annotated

import typer

from asana_cli.client import AsanaClient, ConfigurationError, NotFoundError
from asana_cli.config import get_workspace
from asana_cli.utils import OutputFormat, console, format_output

app = typer.Typer(no_args_is_help=True)


@app.command("list")
def cmd_list(
    workspace: Annotated[
        str | None, typer.Option("--workspace", "-w", help="Workspace GID")
    ] = None,
    archived: Annotated[
        bool, typer.Option("--archived", help="Include archived projects")
    ] = False,
    output: Annotated[
        OutputFormat, typer.Option("--output", "-o", help="Output format")
    ] = OutputFormat.TABLE,
) -> None:
    """List projects in a workspace."""
    workspace_gid = workspace or get_workspace()
    if not workspace_gid:
        console.print(
            "[red]Error:[/red] No workspace specified. Use --workspace or run "
            "'asana workspaces select' to set a default."
        )
        raise typer.Exit(1)

    try:
        with AsanaClient() as client:
            projects = client.get_projects(
                workspace_gid,
                archived=archived,
                opt_fields=["gid", "name", "archived", "owner.name"],
            )

        format_output(
            projects,
            output,
            columns=[
                ("gid", "GID"),
                ("name", "Name"),
                ("archived", "Archived"),
                ("owner", "Owner"),
            ],
            title="Projects",
        )
    except ConfigurationError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command("get")
def cmd_get(
    project_gid: Annotated[str, typer.Argument(help="Project GID")],
    output: Annotated[
        OutputFormat, typer.Option("--output", "-o", help="Output format")
    ] = OutputFormat.TABLE,
) -> None:
    """Get project details."""
    try:
        with AsanaClient() as client:
            project = client.get_project(
                project_gid,
                opt_fields=[
                    "gid",
                    "name",
                    "notes",
                    "archived",
                    "owner.name",
                    "workspace.name",
                    "created_at",
                    "due_on",
                    "start_on",
                ],
            )

        format_output(
            project,
            output,
            detail_fields=[
                ("gid", "GID"),
                ("name", "Name"),
                ("notes", "Notes"),
                ("archived", "Archived"),
                ("owner", "Owner"),
                ("workspace", "Workspace"),
                ("created_at", "Created"),
                ("start_on", "Start Date"),
                ("due_on", "Due Date"),
            ],
        )
    except NotFoundError:
        console.print(f"[red]Error:[/red] Project {project_gid} not found.")
        raise typer.Exit(1)
    except ConfigurationError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
