# Schema Viewer

A beautiful terminal viewer for JSON schemas using the [Rich](https://github.com/Textualize/rich) library.

## Features

- 📊 **Properties Overview** - Tabular view of all schema properties
- 🌳 **Tree View** - Hierarchical structure visualization
- 📝 **Examples** - Formatted example data in panels
- 🎨 **Syntax Highlighting** - Beautiful JSON rendering
- 🔍 **Auto-discovery** - Automatically finds all JSON schemas in docs directory
- 🖥️ **Interactive Mode** - Choose from a list of available schemas
- ⚡ **CLI Support** - Direct access via command-line arguments

## Installation

### Install from local directory

```bash
cd schema-viewer
pip install -e .
```

The `-e` flag installs in editable mode, so changes to the code take effect immediately.

### Install as a regular package

```bash
cd schema-viewer
pip install .
```

### Uninstall

```bash
pip uninstall schema-viewer
```

## Usage

### Interactive Mode
Run without arguments to see a list of all schemas and choose interactively:

```bash
schema-viewer
```

### Select by Number
View a specific schema by its number in the list:

```bash
schema-viewer 3
```

### Select by File Path
View a specific schema file directly:

```bash
schema-viewer docs/schemas/my-schema.json
```

### Full JSON View
Display the complete JSON with syntax highlighting:

```bash
schema-viewer --full docs/schemas/my-schema.json
```

### Custom Search Directory
Search for schemas in a different directory:

```bash
schema-viewer --dir path/to/schemas
```

### Help
Show usage information:

```bash
schema-viewer --help
```

## Package Structure

```
schema-viewer/
├── schema_viewer/
│   ├── __init__.py       # Package initialization
│   ├── cli.py            # Command-line interface
│   └── viewer.py         # Core viewing functions
├── pyproject.toml        # Package configuration
├── README.md             # This file
└── requirements.txt      # Dependencies (optional)
```

## Requirements

- Python 3.8+
- rich >= 13.0.0

## Development

### Install in development mode with dev dependencies

```bash
pip install -e ".[dev]"
```

This installs additional tools like pytest, black, and flake8 for development.

## Examples

**Interactive selection:**
```bash
$ schema-viewer

╭──────────────────────────────╮
│ JSON Schema Viewer with Rich │
╰──────────────────────────────╯

Available JSON Schemas:

┏━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┓
┃   # ┃ Schema File                       ┃   Size ┃
┡━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━┩
│   1 │ docs/schemas/payment-event.json   │ 6.4 KB │
│   2 │ docs/schemas/user-profile.json    │ 3.2 KB │
└─────┴───────────────────────────────────┴────────┘

Select a schema number (or 'q' to quit) (1):
```

**Direct file access:**
```bash
schema-viewer docs/schemas/payment-event.json
```

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
