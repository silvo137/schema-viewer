"""Core viewing functions for JSON schemas"""
import json
from pathlib import Path
from rich.console import Console
from rich.tree import Tree
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.prompt import Prompt

console = Console()


def load_schema(file_path):
    """Load JSON schema from file"""
    with open(file_path, 'r') as f:
        return json.load(f)


def display_pretty_json(schema):
    """Display JSON with syntax highlighting"""
    console.print("\n[bold cyan]═══ Pretty JSON with Syntax Highlighting ═══[/bold cyan]\n")
    syntax = Syntax(json.dumps(schema, indent=2), "json", theme="monokai", line_numbers=True)
    console.print(syntax)


def display_tree_view(schema, name="JSON Schema"):
    """Display schema as a tree structure"""
    console.print("\n[bold cyan]═══ Tree View ═══[/bold cyan]\n")

    def build_tree(obj, tree=None, key="root"):
        if tree is None:
            title = f"[bold blue]{schema.get('title', name)}[/bold blue]"
            if 'description' in schema and key == "root":
                title += f"\n[italic dim]{schema['description']}[/italic dim]"
            tree = Tree(title)

        if isinstance(obj, dict):
            for k, v in obj.items():
                if k in ['title', 'description', '$schema'] and key == "root":
                    continue  # Already shown in root

                if isinstance(v, (dict, list)):
                    if k == 'properties':
                        branch = tree.add(f"[bold green]{k}[/bold green] (fields)")
                    elif k == 'required':
                        branch = tree.add(f"[bold red]{k}[/bold red]: {v}")
                        continue
                    elif k == 'enum':
                        branch = tree.add(f"[yellow]{k}[/yellow]: {', '.join(map(str, v))}")
                        continue
                    else:
                        branch = tree.add(f"[green]{k}[/green]")
                    build_tree(v, branch, k)
                else:
                    if k == 'type':
                        tree.add(f"[magenta]type[/magenta]: [bold yellow]{v}[/bold yellow]")
                    elif k == 'description':
                        tree.add(f"[cyan]description[/cyan]: [italic]{v[:80]}{'...' if len(str(v)) > 80 else ''}[/italic]")
                    else:
                        tree.add(f"[cyan]{k}[/cyan]: [yellow]{v}[/yellow]")
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                if isinstance(item, (dict, list)):
                    branch = tree.add(f"[dim]\\[{i}][/dim]")
                    build_tree(item, branch, f"item_{i}")
                else:
                    tree.add(f"[yellow]{item}[/yellow]")

        return tree

    tree = build_tree(schema)
    console.print(tree)


def display_properties_table(schema):
    """Display schema properties as a table"""
    console.print("\n[bold cyan]═══ Properties Overview ═══[/bold cyan]\n")

    if 'properties' not in schema:
        console.print("[yellow]No properties defined[/yellow]")
        return

    table = Table(show_header=True, header_style="bold magenta", border_style="blue")
    table.add_column("Property", style="cyan", width=25, no_wrap=False)
    table.add_column("Type", style="green", width=30, no_wrap=False)
    table.add_column("Required", style="red", width=10, justify="center")
    table.add_column("Description", style="white", no_wrap=False)

    required = schema.get('required', [])

    for prop_name, prop_info in schema['properties'].items():
        prop_type = prop_info.get('type', 'any')
        if 'enum' in prop_info:
            # Show all enum values
            prop_type += f"\nenum: {', '.join(map(str, prop_info['enum']))}"

        is_required = "✓" if prop_name in required else "✗"
        description = prop_info.get('description', '')

        # Truncate long descriptions
        if len(description) > 3000:
            description = description[:2997] + "..."

        table.add_row(prop_name, prop_type, is_required, description)

    console.print(table)


def display_examples(schema):
    """Display schema examples"""
    if 'examples' not in schema:
        return

    console.print("\n[bold cyan]═══ Examples ═══[/bold cyan]\n")

    for i, example in enumerate(schema['examples'], 1):
        desc = example.get('description', f'Example {i}')
        example_data = {k: v for k, v in example.items() if k != 'description'}

        panel_content = Syntax(
            json.dumps(example_data, indent=2),
            "json",
            theme="monokai"
        )

        console.print(Panel(
            panel_content,
            title=f"[bold yellow]{desc}[/bold yellow]",
            border_style="green"
        ))


def find_json_schemas(base_dir='docs'):
    """Find all JSON files in the specified directory"""
    schemas = []
    base_path = Path(base_dir)

    if not base_path.exists():
        console.print(f"[bold red]Error:[/bold red] Directory '{base_dir}' not found")
        return schemas

    # Find all .json files recursively
    for json_file in base_path.rglob('*.json'):
        schemas.append(json_file)

    return sorted(schemas)


def display_schema_menu(schemas):
    """Display menu of available schemas and let user choose"""
    if not schemas:
        console.print("[bold red]No JSON schemas found[/bold red]")
        return None

    console.print("\n[bold cyan]Available JSON Schemas:[/bold cyan]\n")

    # Create a table to display schemas
    table = Table(show_header=True, header_style="bold magenta", border_style="blue")
    table.add_column("#", style="cyan", width=5, justify="right")
    table.add_column("Schema File", style="green")
    table.add_column("Size", style="yellow", justify="right")

    for idx, schema_path in enumerate(schemas, 1):
        # Get file size
        size = schema_path.stat().st_size
        if size < 1024:
            size_str = f"{size} B"
        elif size < 1024 * 1024:
            size_str = f"{size / 1024:.1f} KB"
        else:
            size_str = f"{size / (1024 * 1024):.1f} MB"

        # Display relative path
        if schema_path.is_absolute():
            try:
                rel_path = schema_path.relative_to(Path.cwd())
            except ValueError:
                rel_path = schema_path
        else:
            rel_path = schema_path

        table.add_row(str(idx), str(rel_path), size_str)

    console.print(table)

    # Prompt user to choose
    console.print()
    choice = Prompt.ask(
        "[bold cyan]Select a schema number (or 'q' to quit)[/bold cyan]",
        default="1"
    )

    if choice.lower() == 'q':
        return None

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(schemas):
            return schemas[idx]
        else:
            console.print(f"[bold red]Invalid choice. Please select 1-{len(schemas)}[/bold red]")
            return None
    except ValueError:
        console.print("[bold red]Invalid input. Please enter a number.[/bold red]")
        return None


def display_schema(schema_file):
    """Display a schema file with all views"""
    schema = load_schema(schema_file)

    # Display overview
    console.print(f"\n[bold]Schema:[/bold] {schema.get('title', 'Unknown')}")
    console.print(f"[bold]Description:[/bold] {schema.get('description', 'N/A')}")
    console.print(f"[bold]File:[/bold] {schema_file}\n")

    # Display properties table
    display_properties_table(schema)

    # Display tree view
    display_tree_view(schema)

    # Display examples
    display_examples(schema)

    # Optionally show full JSON
    console.print("\n[dim]Run with --full <file> to see complete JSON with syntax highlighting[/dim]")
