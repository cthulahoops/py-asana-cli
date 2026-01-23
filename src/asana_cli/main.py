"""Main Typer application entry point."""

import typer

from asana_cli.commands import config, projects, sections, tasks, users, workspaces

app = typer.Typer(
    name="asana",
    help="A modern CLI for interacting with Asana.",
    no_args_is_help=True,
)

app.add_typer(config.app, name="config", help="Manage CLI configuration")
app.add_typer(workspaces.app, name="workspaces", help="Manage workspaces")
app.add_typer(projects.app, name="projects", help="Manage projects")
app.add_typer(tasks.app, name="tasks", help="Manage tasks")
app.add_typer(sections.app, name="sections", help="Manage sections")
app.add_typer(users.app, name="users", help="Manage users")


if __name__ == "__main__":
    app()
