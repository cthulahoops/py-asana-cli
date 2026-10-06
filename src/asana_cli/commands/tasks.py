"""Task commands."""

import sys
from pathlib import Path
from typing import Annotated

import typer

from asana_cli.client import AsanaClient, ConfigurationError, NotFoundError
from asana_cli.config import get_workspace
from asana_cli.utils import OutputFormat, console, format_output

app = typer.Typer(no_args_is_help=True)


@app.command("list")
def cmd_list(
    project: Annotated[
        str | None, typer.Option("--project", "-p", help="Project GID")
    ] = None,
    assignee: Annotated[
        str | None, typer.Option("--assignee", "-a", help="Assignee GID or 'me'")
    ] = None,
    workspace: Annotated[
        str | None, typer.Option("--workspace", "-w", help="Workspace GID (required with --assignee)")
    ] = None,
    completed: Annotated[
        bool, typer.Option("--completed", help="Include completed tasks")
    ] = False,
    output: Annotated[
        OutputFormat, typer.Option("--output", "-o", help="Output format")
    ] = OutputFormat.TABLE,
) -> None:
    """List tasks with optional filters."""
    if not project and not assignee:
        console.print("[red]Error:[/red] Specify --project or --assignee to list tasks.")
        raise typer.Exit(1)

    # If assignee is specified, workspace is required
    if assignee and not workspace:
        workspace = get_workspace()
        if not workspace:
            console.print(
                "[red]Error:[/red] --workspace required with --assignee. "
                "Set default with 'asana workspaces select'."
            )
            raise typer.Exit(1)

    try:
        with AsanaClient() as client:
            # completed_since=now means only incomplete tasks
            completed_since = None if completed else "now"

            tasks = client.get_tasks(
                project=project,
                assignee=assignee,
                workspace=workspace,
                completed_since=completed_since,
                opt_fields=[
                    "gid",
                    "name",
                    "completed",
                    "due_on",
                    "assignee.name",
                    "num_subtasks",
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
                ("num_subtasks", "Subtasks"),
            ],
            title="Tasks",
        )
    except ConfigurationError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command("get")
def cmd_get(
    task_gid: Annotated[str, typer.Argument(help="Task GID")],
    output: Annotated[
        OutputFormat, typer.Option("--output", "-o", help="Output format")
    ] = OutputFormat.TABLE,
) -> None:
    """Get task details."""
    try:
        with AsanaClient() as client:
            task = client.get_task(
                task_gid,
                opt_fields=[
                    "gid",
                    "name",
                    "notes",
                    "completed",
                    "completed_at",
                    "created_at",
                    "due_on",
                    "due_at",
                    "assignee.name",
                    "projects.name",
                    "parent.name",
                    "num_subtasks",
                    "permalink_url",
                ],
            )

        format_output(
            task,
            output,
            detail_fields=[
                ("gid", "GID"),
                ("name", "Name"),
                ("notes", "Notes"),
                ("completed", "Completed"),
                ("completed_at", "Completed At"),
                ("created_at", "Created"),
                ("due_on", "Due Date"),
                ("assignee", "Assignee"),
                ("projects", "Projects"),
                ("parent", "Parent Task"),
                ("num_subtasks", "Subtasks"),
                ("permalink_url", "URL"),
            ],
        )
    except NotFoundError:
        console.print(f"[red]Error:[/red] Task {task_gid} not found.")
        raise typer.Exit(1)
    except ConfigurationError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command("create")
def cmd_create(
    name: Annotated[str, typer.Argument(help="Task name")],
    project: Annotated[
        str | None, typer.Option("--project", "-p", help="Project GID")
    ] = None,
    assignee: Annotated[
        str | None, typer.Option("--assignee", "-a", help="Assignee GID or 'me'")
    ] = None,
    due_on: Annotated[
        str | None, typer.Option("--due", "-d", help="Due date (YYYY-MM-DD)")
    ] = None,
    notes: Annotated[
        str | None, typer.Option("--notes", "-n", help="Task notes/description")
    ] = None,
    workspace: Annotated[
        str | None, typer.Option("--workspace", "-w", help="Workspace GID")
    ] = None,
    output: Annotated[
        OutputFormat, typer.Option("--output", "-o", help="Output format")
    ] = OutputFormat.TABLE,
) -> None:
    """Create a new task."""
    workspace_gid = workspace or get_workspace()
    if not workspace_gid and not project:
        console.print(
            "[red]Error:[/red] Specify --workspace or --project, or run "
            "'asana workspaces select' to set a default."
        )
        raise typer.Exit(1)

    data: dict = {"name": name}
    if project:
        data["projects"] = [project]
    if workspace_gid and not project:
        data["workspace"] = workspace_gid
    if assignee:
        data["assignee"] = assignee
    if due_on:
        data["due_on"] = due_on
    if notes:
        data["notes"] = notes

    try:
        with AsanaClient() as client:
            task = client.create_task(data)

        if output == OutputFormat.JSON:
            format_output(task, output)
        else:
            console.print(f"[green]Created task:[/green] {task['name']} ({task['gid']})")

    except ConfigurationError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command("complete")
def cmd_complete(
    task_gid: Annotated[str, typer.Argument(help="Task GID")],
) -> None:
    """Mark a task as complete."""
    try:
        with AsanaClient() as client:
            task = client.update_task(task_gid, {"completed": True})

        console.print(f"[green]Completed:[/green] {task['name']}")

    except NotFoundError:
        console.print(f"[red]Error:[/red] Task {task_gid} not found.")
        raise typer.Exit(1)
    except ConfigurationError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command("update")
def cmd_update(
    task_gid: Annotated[str, typer.Argument(help="Task GID")],
    name: Annotated[str | None, typer.Option("--name", help="New task name")] = None,
    assignee: Annotated[
        str | None, typer.Option("--assignee", "-a", help="New assignee GID or 'me'")
    ] = None,
    due_on: Annotated[
        str | None, typer.Option("--due", "-d", help="New due date (YYYY-MM-DD)")
    ] = None,
    notes: Annotated[
        str | None, typer.Option("--notes", "-n", help="New notes/description")
    ] = None,
    completed: Annotated[
        bool | None, typer.Option("--completed/--incomplete", help="Mark complete/incomplete")
    ] = None,
) -> None:
    """Update a task."""
    data: dict = {}
    if name is not None:
        data["name"] = name
    if assignee is not None:
        data["assignee"] = assignee
    if due_on is not None:
        data["due_on"] = due_on
    if notes is not None:
        data["notes"] = notes
    if completed is not None:
        data["completed"] = completed

    if not data:
        console.print("[yellow]No updates specified.[/yellow]")
        raise typer.Exit(1)

    try:
        with AsanaClient() as client:
            task = client.update_task(task_gid, data)

        console.print(f"[green]Updated:[/green] {task['name']}")

    except NotFoundError:
        console.print(f"[red]Error:[/red] Task {task_gid} not found.")
        raise typer.Exit(1)
    except ConfigurationError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command("subtasks")
def cmd_subtasks(
    task_gid: Annotated[str, typer.Argument(help="Parent task GID")],
    output: Annotated[
        OutputFormat, typer.Option("--output", "-o", help="Output format")
    ] = OutputFormat.TABLE,
) -> None:
    """List subtasks of a task."""
    try:
        with AsanaClient() as client:
            subtasks = client.get_subtasks(
                task_gid,
                opt_fields=["gid", "name", "completed", "due_on", "assignee.name"],
            )

        format_output(
            subtasks,
            output,
            columns=[
                ("gid", "GID"),
                ("name", "Name"),
                ("completed", "Done"),
                ("due_on", "Due"),
                ("assignee", "Assignee"),
            ],
            title="Subtasks",
        )
    except NotFoundError:
        console.print(f"[red]Error:[/red] Task {task_gid} not found.")
        raise typer.Exit(1)
    except ConfigurationError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command("add-subtask")
def cmd_add_subtask(
    parent_gid: Annotated[str, typer.Argument(help="Parent task GID")],
    name: Annotated[str, typer.Argument(help="Subtask name")],
    assignee: Annotated[
        str | None, typer.Option("--assignee", "-a", help="Assignee GID or 'me'")
    ] = None,
    due_on: Annotated[
        str | None, typer.Option("--due", "-d", help="Due date (YYYY-MM-DD)")
    ] = None,
    notes: Annotated[
        str | None, typer.Option("--notes", "-n", help="Subtask notes")
    ] = None,
    output: Annotated[
        OutputFormat, typer.Option("--output", "-o", help="Output format")
    ] = OutputFormat.TABLE,
) -> None:
    """Create a subtask under a parent task."""
    data: dict = {"name": name}
    if assignee:
        data["assignee"] = assignee
    if due_on:
        data["due_on"] = due_on
    if notes:
        data["notes"] = notes

    try:
        with AsanaClient() as client:
            subtask = client.create_subtask(parent_gid, data)

        if output == OutputFormat.JSON:
            format_output(subtask, output)
        else:
            console.print(f"[green]Created subtask:[/green] {subtask['name']} ({subtask['gid']})")

    except NotFoundError:
        console.print(f"[red]Error:[/red] Parent task {parent_gid} not found.")
        raise typer.Exit(1)
    except ConfigurationError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command("comment")
def cmd_comment(
    task_gid: Annotated[str, typer.Argument(help="Task GID")],
    text: Annotated[str | None, typer.Argument(help="Comment text")] = None,
    body_file: Annotated[
        str | None,
        typer.Option("--body-file", "-F", help="Read comment text from a file ('-' for stdin)"),
    ] = None,
    output: Annotated[
        OutputFormat, typer.Option("--output", "-o", help="Output format")
    ] = OutputFormat.TABLE,
) -> None:
    """Add a comment to a task."""
    if (text is None) == (body_file is None):
        console.print("[red]Error:[/red] Give the comment as either TEXT or --body-file.")
        raise typer.Exit(1)

    if body_file is not None:
        try:
            text = sys.stdin.read() if body_file == "-" else Path(body_file).read_text()
        except OSError as e:
            console.print(f"[red]Error:[/red] Cannot read {body_file}: {e.strerror}")
            raise typer.Exit(1)
        except UnicodeDecodeError:
            console.print(f"[red]Error:[/red] {body_file} is not valid UTF-8 text.")
            raise typer.Exit(1)

    text = (text or "").rstrip()
    if not text:
        console.print("[red]Error:[/red] Comment text is empty.")
        raise typer.Exit(1)

    try:
        with AsanaClient() as client:
            story = client.create_comment(task_gid, text)

        if output == OutputFormat.JSON:
            format_output(story, output)
        else:
            console.print(story["gid"], markup=False, highlight=False)

    except NotFoundError:
        console.print(f"[red]Error:[/red] Task {task_gid} not found.")
        raise typer.Exit(1)
    except ConfigurationError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command("comments")
def cmd_comments(
    task_gid: Annotated[str, typer.Argument(help="Task GID")],
    output: Annotated[
        OutputFormat, typer.Option("--output", "-o", help="Output format")
    ] = OutputFormat.TABLE,
) -> None:
    """List comments on a task."""
    try:
        with AsanaClient() as client:
            stories = client.get_stories(
                task_gid,
                opt_fields=["gid", "resource_subtype", "created_at", "created_by.name", "text"],
            )

        comments = [s for s in stories if s.get("resource_subtype") == "comment_added"]

        format_output(
            comments,
            output,
            columns=[
                ("created_by", "Author"),
                ("created_at", "Time"),
                ("text", "Text"),
            ],
            title="Comments",
        )
    except NotFoundError:
        console.print(f"[red]Error:[/red] Task {task_gid} not found.")
        raise typer.Exit(1)
    except ConfigurationError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command("move")
def cmd_move(
    task_gid: Annotated[str, typer.Argument(help="Task GID")],
    section: Annotated[str, typer.Option("--section", "-s", help="Target section GID")],
) -> None:
    """Move a task to a section."""
    try:
        with AsanaClient() as client:
            client.add_task_to_section(section, task_gid)

        console.print(f"[green]Moved task {task_gid} to section {section}[/green]")

    except NotFoundError:
        console.print("[red]Error:[/red] Task or section not found.")
        raise typer.Exit(1)
    except ConfigurationError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command("delete")
def cmd_delete(
    task_gid: Annotated[str, typer.Argument(help="Task GID to delete")],
    force: Annotated[
        bool, typer.Option("--force", "-f", help="Skip confirmation")
    ] = False,
) -> None:
    """Delete a task permanently."""
    if not force:
        confirm = typer.confirm(f"Are you sure you want to delete task {task_gid}?")
        if not confirm:
            console.print("[yellow]Cancelled.[/yellow]")
            raise typer.Exit(0)

    try:
        with AsanaClient() as client:
            client.delete_task(task_gid)

        console.print(f"[green]Deleted task {task_gid}[/green]")

    except NotFoundError:
        console.print(f"[red]Error:[/red] Task {task_gid} not found.")
        raise typer.Exit(1)
    except ConfigurationError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
