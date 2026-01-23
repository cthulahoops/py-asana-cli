"""User commands."""

from typing import Annotated

import typer

from asana_cli.client import AsanaClient, ConfigurationError, NotFoundError
from asana_cli.utils import OutputFormat, console, format_output

app = typer.Typer(no_args_is_help=True)


@app.command("me")
def cmd_me(
    output: Annotated[
        OutputFormat, typer.Option("--output", "-o", help="Output format")
    ] = OutputFormat.TABLE,
) -> None:
    """Show current user information."""
    try:
        with AsanaClient() as client:
            user = client.get_me(
                opt_fields=["gid", "name", "email", "workspaces.name"]
            )

        format_output(
            user,
            output,
            detail_fields=[
                ("gid", "GID"),
                ("name", "Name"),
                ("email", "Email"),
                ("workspaces", "Workspaces"),
            ],
        )
    except ConfigurationError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command("get")
def cmd_get(
    user_gid: Annotated[str, typer.Argument(help="User GID")],
    output: Annotated[
        OutputFormat, typer.Option("--output", "-o", help="Output format")
    ] = OutputFormat.TABLE,
) -> None:
    """Get user details."""
    try:
        with AsanaClient() as client:
            user = client.get_user(
                user_gid, opt_fields=["gid", "name", "email", "workspaces.name"]
            )

        format_output(
            user,
            output,
            detail_fields=[
                ("gid", "GID"),
                ("name", "Name"),
                ("email", "Email"),
                ("workspaces", "Workspaces"),
            ],
        )
    except NotFoundError:
        console.print(f"[red]Error:[/red] User {user_gid} not found.")
        raise typer.Exit(1)
    except ConfigurationError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
