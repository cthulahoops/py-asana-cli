"""Output formatting utilities."""

import json
from enum import Enum
from typing import Any

from rich.table import Table

from asana_cli.utils.console import console


class OutputFormat(str, Enum):
    """Output format options."""

    TABLE = "table"
    JSON = "json"


def print_json(data: Any) -> None:
    """Print data as formatted JSON."""
    console.print(json.dumps(data, indent=2, default=str))


def print_table(
    data: list[dict[str, Any]],
    columns: list[tuple[str, str]],
    title: str | None = None,
) -> None:
    """Print data as a Rich table.

    Args:
        data: List of dictionaries to display
        columns: List of (key, header) tuples defining columns
        title: Optional table title
    """
    table = Table(title=title, show_header=True, header_style="bold")

    for _, header in columns:
        table.add_column(header)

    for item in data:
        row = []
        for key, _ in columns:
            value = item.get(key, "")
            if isinstance(value, bool):
                value = "[green]\u2713[/green]" if value else "[red]\u2717[/red]"
            elif isinstance(value, dict):
                value = value.get("name", str(value))
            elif value is None:
                value = ""
            row.append(str(value))
        table.add_row(*row)

    console.print(table)


def print_detail(data: dict[str, Any], fields: list[tuple[str, str]]) -> None:
    """Print a single item's details.

    Args:
        data: Dictionary to display
        fields: List of (key, label) tuples defining fields to show
    """
    for key, label in fields:
        value = data.get(key, "")
        if isinstance(value, bool):
            value = "[green]Yes[/green]" if value else "[red]No[/red]"
        elif isinstance(value, dict):
            value = value.get("name", str(value))
        elif isinstance(value, list):
            if value and isinstance(value[0], dict):
                value = ", ".join(item.get("name", str(item)) for item in value)
            else:
                value = ", ".join(str(v) for v in value)
        elif value is None:
            value = "[dim]Not set[/dim]"
        console.print(f"[bold]{label}:[/bold] {value}")


def format_output(
    data: Any,
    output_format: OutputFormat,
    columns: list[tuple[str, str]] | None = None,
    title: str | None = None,
    detail_fields: list[tuple[str, str]] | None = None,
) -> None:
    """Format and print output based on format preference.

    Args:
        data: Data to display (dict for detail, list for table)
        output_format: Output format (table or json)
        columns: Columns for table output
        title: Title for table output
        detail_fields: Fields for detail output
    """
    if output_format == OutputFormat.JSON:
        print_json(data)
    elif isinstance(data, list):
        if columns:
            print_table(data, columns, title)
        else:
            print_json(data)
    elif isinstance(data, dict) and detail_fields:
        print_detail(data, detail_fields)
    else:
        print_json(data)
