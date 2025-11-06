"""Simple TUI for Schema Viewer using Textual"""
import json
import subprocess
from pathlib import Path
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.widgets import Header, Footer, Static, Button
from textual.binding import Binding
from rich.console import Console
from rich.tree import Tree
from rich.syntax import Syntax
from rich.text import Text
from rich.json import JSON
from io import StringIO

from .viewer import load_schema


class SchemaViewerApp(App):
    """A simple Textual app for viewing JSON schemas."""

    CSS = """
    Screen {
        layout: horizontal;
    }

    #sidebar {
        width: 30;
        background: $panel;
        border-right: solid $primary;
        padding: 1;
    }

    #content-area {
        width: 1fr;
    }

    Button {
        width: 100%;
        margin-bottom: 1;
    }

    #content {
        padding: 2;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("1", "show_overview", "Overview"),
        Binding("2", "show_properties", "Properties"),
        Binding("3", "show_tree", "Tree"),
        Binding("4", "show_examples", "Examples"),
        Binding("c", "copy_all_examples", "Copy All"),
    ]

    def __init__(self, schema_file: str):
        super().__init__()
        self.schema_file = schema_file
        self.schema = load_schema(schema_file)
        self.title = f"Schema Viewer - {Path(schema_file).name}"
        self.current_examples = []  # Store examples for copying
        self.viewing_examples = False  # Track if we're in examples view

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()

        with Horizontal():
            with Vertical(id="sidebar"):
                yield Button("1. Overview", id="btn-overview", variant="primary")
                yield Button("2. Properties", id="btn-properties")
                yield Button("3. Tree View", id="btn-tree")
                if 'examples' in self.schema:
                    yield Button("4. Examples", id="btn-examples")

            with VerticalScroll(id="content-area"):
                yield Static(id="content", markup=True)

        yield Footer()

    def on_mount(self) -> None:
        """Called when app starts."""
        self.viewing_examples = False
        self.show_overview()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "btn-overview":
            self.viewing_examples = False
            self.show_overview()
        elif button_id == "btn-properties":
            self.viewing_examples = False
            self.show_properties()
        elif button_id == "btn-tree":
            self.viewing_examples = False
            self.show_tree()
        elif button_id == "btn-examples":
            self.viewing_examples = True
            self.show_examples()

    def action_show_overview(self) -> None:
        self.viewing_examples = False
        self.show_overview()

    def action_show_properties(self) -> None:
        self.viewing_examples = False
        self.show_properties()

    def action_show_tree(self) -> None:
        self.viewing_examples = False
        self.show_tree()

    def action_show_examples(self) -> None:
        self.viewing_examples = True
        self.show_examples()

    def on_key(self, event) -> None:
        """Handle key presses for copying individual examples."""
        if self.viewing_examples and event.character and event.character.isdigit():
            example_num = int(event.character)
            if 1 <= example_num <= len(self.current_examples):
                self.copy_example(example_num - 1)
                event.prevent_default()

    def copy_example(self, index: int) -> None:
        """Copy a specific example to clipboard."""
        if not self.current_examples or index >= len(self.current_examples):
            return

        json_text = json.dumps(self.current_examples[index], indent=2)

        try:
            # Try clip.exe first (WSL/Windows)
            subprocess.run(['clip.exe'], input=json_text.encode('utf-8'), check=True)
            self.notify(f"Copied example {index + 1} to clipboard", severity="information")
        except FileNotFoundError:
            try:
                # Try xclip (Linux)
                subprocess.run(['xclip', '-selection', 'clipboard'], input=json_text.encode('utf-8'), check=True)
                self.notify(f"Copied example {index + 1} to clipboard", severity="information")
            except FileNotFoundError:
                try:
                    # Try pbcopy (macOS)
                    subprocess.run(['pbcopy'], input=json_text.encode('utf-8'), check=True)
                    self.notify(f"Copied example {index + 1} to clipboard", severity="information")
                except FileNotFoundError:
                    self.notify("Clipboard tool not found (tried clip.exe, xclip, pbcopy)", severity="error")

    def action_copy_all_examples(self) -> None:
        """Copy current examples to clipboard."""
        if not self.current_examples:
            self.notify("No examples to copy", severity="warning")
            return

        # Prepare JSON to copy
        if len(self.current_examples) == 1:
            json_text = json.dumps(self.current_examples[0], indent=2)
        else:
            json_text = json.dumps(self.current_examples, indent=2)

        try:
            # Try clip.exe first (WSL/Windows)
            subprocess.run(['clip.exe'], input=json_text.encode('utf-8'), check=True)
            self.notify(f"Copied {len(self.current_examples)} example(s) to clipboard", severity="information")
        except FileNotFoundError:
            try:
                # Try xclip (Linux)
                subprocess.run(['xclip', '-selection', 'clipboard'], input=json_text.encode('utf-8'), check=True)
                self.notify(f"Copied {len(self.current_examples)} example(s) to clipboard", severity="information")
            except FileNotFoundError:
                try:
                    # Try pbcopy (macOS)
                    subprocess.run(['pbcopy'], input=json_text.encode('utf-8'), check=True)
                    self.notify(f"Copied {len(self.current_examples)} example(s) to clipboard", severity="information")
                except FileNotFoundError:
                    self.notify("Clipboard tool not found (tried clip.exe, xclip, pbcopy)", severity="error")

    def render_to_string(self, renderable) -> str:
        """Render a Rich renderable to a string."""
        console = Console(file=StringIO(), width=120, legacy_windows=False)
        console.print(renderable)
        return console.file.getvalue()

    def show_overview(self) -> None:
        """Show schema overview."""
        content = self.query_one("#content", Static)

        text = f"""[bold cyan]Schema Overview[/bold cyan]

[bold]Title:[/bold] {self.schema.get('title', 'Unknown')}
[bold]Description:[/bold] {self.schema.get('description', 'N/A')}
[bold]File:[/bold] {self.schema_file}
[bold]Schema Version:[/bold] {self.schema.get('$schema', 'N/A')}
"""

        if 'type' in self.schema:
            text += f"[bold]Type:[/bold] {self.schema['type']}\n"

        if 'required' in self.schema:
            text += f"\n[bold]Required Fields ({len(self.schema['required'])}):[/bold]\n"
            for field in self.schema['required']:
                text += f"  • {field}\n"

        content.update(text)

    def show_properties(self) -> None:
        """Show properties table."""
        content = self.query_one("#content", Static)

        if 'properties' not in self.schema:
            content.update("[yellow]No properties defined[/yellow]")
            return

        text = "[bold cyan]Properties Overview[/bold cyan]\n\n"
        required = self.schema.get('required', [])

        for prop_name, prop_info in self.schema['properties'].items():
            prop_type = prop_info.get('type', 'any')
            is_required = "✓" if prop_name in required else "✗"
            description = prop_info.get('description', '')

            # Truncate long descriptions
            if len(description) > 3000:
                description = description[:2997] + "..."

            text += f"[bold cyan]{prop_name}[/bold cyan]\n"
            text += f"  Type: [green]{prop_type}[/green]\n"

            if 'enum' in prop_info:
                enum_vals = ', '.join(map(str, prop_info['enum']))
                text += f"  Enum: [yellow]{enum_vals}[/yellow]\n"

            text += f"  Required: [red]{is_required}[/red]\n"

            if description:
                text += f"  Description: {description}\n"

            text += "\n"

        content.update(text)

    def show_tree(self) -> None:
        """Show tree view."""
        content = self.query_one("#content", Static)

        tree = self._build_tree(self.schema)

        # Build the content with title and tree
        from rich.console import Group
        from rich.text import Text

        title = Text("Tree View", style="bold cyan")
        content.update(Group(title, Text("\n"), tree))

    def _build_tree(self, obj, tree=None, key="root"):
        """Build a tree structure from schema."""
        if tree is None:
            title = f"[bold magenta]{self.schema.get('title', 'JSON Schema')}[/bold magenta]"
            if 'description' in self.schema and key == "root":
                desc = self.schema['description']
                if len(desc) > 100:
                    desc = desc[:97] + "..."
                title += f"\n[italic bright_black]{desc}[/italic bright_black]"
            tree = Tree(title)

        if isinstance(obj, dict):
            for k, v in obj.items():
                if k in ['title', 'description', '$schema'] and key == "root":
                    continue

                if isinstance(v, (dict, list)):
                    if k == 'properties':
                        branch = tree.add(f"[bold green]{k}[/bold green] [dim](fields)[/dim]")
                    elif k == 'required':
                        req_list = ', '.join(v) if len(v) <= 5 else ', '.join(v[:5]) + '...'
                        tree.add(f"[bold red]{k}[/bold red]: [bright_red]{req_list}[/bright_red]")
                        continue
                    elif k == 'enum':
                        enum_str = ', '.join(map(str, v[:5]))
                        if len(v) > 5:
                            enum_str += '...'
                        tree.add(f"[bold yellow]{k}[/bold yellow]: [bright_yellow]{enum_str}[/bright_yellow]")
                        continue
                    elif k == 'examples':
                        branch = tree.add(f"[bold cyan]{k}[/bold cyan]")
                    elif k == 'items':
                        branch = tree.add(f"[bold blue]{k}[/bold blue] [dim](array items)[/dim]")
                    elif k == 'definitions' or k == '$defs':
                        branch = tree.add(f"[bold magenta]{k}[/bold magenta]")
                    else:
                        branch = tree.add(f"[bold bright_blue]{k}[/bold bright_blue]")
                    self._build_tree(v, branch, k)
                else:
                    if k == 'type':
                        tree.add(f"[bold magenta]type[/bold magenta]: [bold bright_yellow]{v}[/bold bright_yellow]")
                    elif k == 'description':
                        desc_text = str(v)[:500] + ('...' if len(str(v)) > 500 else '')
                        tree.add(f"[bright_cyan]description[/bright_cyan]: [italic white]{desc_text}[/italic white]")
                    elif k == 'default':
                        tree.add(f"[bright_green]{k}[/bright_green]: [bold green]{v}[/bold green]")
                    elif k == 'format':
                        tree.add(f"[bright_magenta]{k}[/bright_magenta]: [magenta]{v}[/magenta]")
                    elif k in ['minimum', 'maximum', 'minLength', 'maxLength', 'minItems', 'maxItems']:
                        tree.add(f"[bright_blue]{k}[/bright_blue]: [blue]{v}[/blue]")
                    elif k == 'pattern':
                        tree.add(f"[bright_yellow]{k}[/bright_yellow]: [yellow]{v}[/yellow]")
                    else:
                        val_str = str(v)
                        if len(val_str) > 100:
                            val_str = val_str[:97] + "..."
                        tree.add(f"[cyan]{k}[/cyan]: [bright_white]{val_str}[/bright_white]")
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                if isinstance(item, (dict, list)):
                    branch = tree.add(f"[bright_blue]\\[{i}][/bright_blue]")
                    self._build_tree(item, branch, f"item_{i}")
                else:
                    item_str = str(item)
                    if len(item_str) > 100:
                        item_str = item_str[:97] + "..."
                    tree.add(f"[bright_yellow]{item_str}[/bright_yellow]")

        return tree

    def show_examples(self) -> None:
        """Show examples."""
        content = self.query_one("#content", Static)

        if 'examples' not in self.schema:
            content.update("[yellow]No examples defined[/yellow]")
            self.current_examples = []
            return

        from rich.console import Group
        from rich.text import Text

        renderables = []
        renderables.append(Text("Examples", style="bold cyan"))
        renderables.append(Text("Press number key (1-9) to copy that example, 'c' to copy all", style="dim italic"))
        renderables.append(Text("\n"))

        self.current_examples = []

        for i, example in enumerate(self.schema['examples'], 1):
            desc = example.get('description', f'Example {i}')
            example_data = {k: v for k, v in example.items() if k != 'description'}

            # Store for copying
            self.current_examples.append(example_data)

            # Add decorative separator with number
            renderables.append(Text("─" * 60, style="bold bright_magenta"))
            renderables.append(Text(f"[{i}] {desc}", style="bold bright_yellow"))
            renderables.append(Text("─" * 60, style="bold bright_magenta"))
            renderables.append(Text(""))

            # Use Rich JSON renderer for better key highlighting
            json_renderer = JSON.from_data(example_data)
            renderables.append(json_renderer)
            renderables.append(Text("\n"))

        content.update(Group(*renderables))


def run_tui(schema_file: str):
    """Run the TUI app for a schema file."""
    app = SchemaViewerApp(schema_file)
    app.run()
