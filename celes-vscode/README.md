# Celes for VS Code

Language support for the Celes 0.1 markup language.

## Features

- **Syntax highlighting** — tag names, attributes, inline tags, comments, and content all coloured distinctly
- **Snippets** — type `header`, `line`, `list`, `table`, `codeblock` etc. and press Tab to expand
- **Validation** — red/yellow squiggles with error messages as you type
- **Live HTML preview** — click the preview icon in the editor title bar to open a side-by-side rendered view that updates as you type

## Requirements

Python must be installed with the `celes` package:

```bash
pip install celes
```

## Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `celes.pythonPath` | `python` | Path to Python executable |

If you use a virtual environment or have Python at a custom path:
```json
{
  "celes.pythonPath": "C:/Users/you/venv/Scripts/python.exe"
}
```

## Usage

1. Open any `.celes` file — syntax highlighting activates automatically
2. Click the **preview icon** (top right of editor) to open live HTML preview
3. Run **Celes: Validate File** from the Command Palette (`Ctrl+Shift+P`) to manually trigger validation

## Building the Extension

```bash
npm install
npm install -g vsce
vsce package
```

This produces a `.vsix` file you can install via:
```
Extensions → ... → Install from VSIX
```
