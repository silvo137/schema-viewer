#!/usr/bin/env python3
"""Command-line interface for Schema Viewer"""
import sys
import json
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

from .viewer import (
    find_json_schemas,
    display_schema_menu,
    display_schema,
    display_pretty_json,
    load_schema
)

console = Console()


def show_help():
    """Display help message"""
    help_text = """
[bold cyan]Schema Viewer[/bold cyan] - Beautiful JSON Schema Viewer

[bold]Usage:[/bold]
  schema-viewer                      Interactive mode (choose from list)
  schema-viewer <number>             View schema by number from list
  schema-viewer <path>               View specific schema file
  schema-viewer --full <path>        View full JSON with syntax highlighting
  schema-viewer --help               Show this help message

[bold]Examples:[/bold]
  schema-viewer                      # Interactive menu
  schema-viewer 3                    # View schema #3
  schema-viewer docs/schema.json     # View specific file
  schema-viewer --full schema.json   # Full JSON view

[bold]Options:[/bold]
  -d, --dir <path>    Search directory (default: docs)
  --full              Show full JSON with syntax highlighting
  --help              Show this help message
"""
    console.print(Panel(help_text, border_style="cyan"))


def main():
    """Main entry point for the CLI"""

    # Parse command line arguments
    args = sys.argv[1:]
    search_dir = 'docs'

    # Check for help
    if '--help' in args or '-h' in args:
        show_help()
        return 0

    # Check for custom directory
    if '--dir' in args or '-d' in args:
        dir_flag = '--dir' if '--dir' in args else '-d'
        dir_idx = args.index(dir_flag)
        if dir_idx + 1 < len(args):
            search_dir = args[dir_idx + 1]
            args.pop(dir_idx)  # Remove flag
            args.pop(dir_idx)  # Remove value

    console.print(Panel.fit(
        "[bold magenta]JSON Schema Viewer with Rich[/bold magenta]",
        border_style="magenta"
    ))

    # Find all schemas
    schemas = find_json_schemas(search_dir)

    if not schemas:
        return 1

    # Handle different command modes
    if '--full' in args:
        # Full JSON view mode
        if len(args) > 1:
            schema_file = args[1]
        else:
            console.print("[bold red]Error:[/bold red] Please specify a schema file")
            return 1

        try:
            schema = load_schema(schema_file)
            display_pretty_json(schema)
        except FileNotFoundError:
            console.print(f"[bold red]Error:[/bold red] File '{schema_file}' not found")
            return 1
        except json.JSONDecodeError as e:
            console.print(f"[bold red]Error:[/bold red] Invalid JSON: {e}")
            return 1

    elif len(args) > 0 and args[0].isdigit():
        # Select by number
        choice = int(args[0])
        if 1 <= choice <= len(schemas):
            display_schema(schemas[choice - 1])
        else:
            console.print(f"[bold red]Invalid choice. Please select 1-{len(schemas)}[/bold red]")
            return 1

    elif len(args) > 0:
        # Select by file path
        schema_file = args[0]
        if Path(schema_file).exists():
            try:
                display_schema(schema_file)
            except json.JSONDecodeError as e:
                console.print(f"[bold red]Error:[/bold red] Invalid JSON: {e}")
                return 1
        else:
            console.print(f"[bold red]Error:[/bold red] File '{schema_file}' not found")
            return 1
    else:
        # Interactive mode
        selected_schema = display_schema_menu(schemas)
        if selected_schema:
            display_schema(selected_schema)

    return 0


if __name__ == '__main__':
    sys.exit(main())
