"""Section commands."""

from typing import Annotated

import typer

from asana_cli.client import AsanaClient, ConfigurationError, NotFoundError
from asana_cli.utils import OutputFormat, console, format_output

app = typer.Typer(no_args_is_help=True)


@app.command("list")
def cmd_list(
    project: Annotated[str, typer.Option("--project", "-p", help="Project GID")],
    output: Annotated[
        OutputFormat, typer.Option("--output", "-o", help="Output format")
    ] = OutputFormat.TABLE,
) -> None:
    """List sections in a project."""
    try:
        with AsanaClient() as client:
            sections = client.get_sections(project, opt_fields=["gid", "name", "created_at"])

        format_output(
            sections,
            output,
            columns=[("gid", "GID"), ("name", "Name"), ("created_at", "Created")],
            title="Sections",
        )
    except NotFoundError:
        console.print(f"[red]Error:[/red] Project {project} not found.")
        raise typer.Exit(1)
    except ConfigurationError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command("tasks")
def cmd_tasks(
    section_gid: Annotated[str, typer.Argument(help="Section GID")],
    output: Annotated[
        OutputFormat, typer.Option("--output", "-o", help="Output format")
    ] = OutputFormat.TABLE,
) -> None:
    """List tasks in a section."""
    try:
        with AsanaClient() as client:
            tasks = client.get_section_tasks(
                section_gid,
                opt_fields=[
                    "gid",
                    "name",
                    "completed",
                    "due_on",
                    "assignee.name",
                ],
            )

        format_output(
            tasks,
            output,
            columns=[
                ("gid", "GID"),
                ("name", "Name"),
                ("completed", "Done"),
                ("due_on", "Due"),
                ("assignee", "Assignee"),
            ],
            title="Tasks",
        )
    except NotFoundError:
        console.print(f"[red]Error:[/red] Section {section_gid} not found.")
        raise typer.Exit(1)
    except ConfigurationError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
