<div align="center">
  <img src="celes-icons/celes-128.png" width="96" alt="Celes logo"/>
  <h1>Celes</h1>
  <p>A strict, tag-based markup language. Explicit syntax. Zero ambiguity.</p>

  <a href="https://pypi.org/project/celes/"><img src="https://img.shields.io/pypi/v/celes?color=D4622A&label=pypi" alt="PyPI"/></a>
  <a href="https://pypi.org/project/celes/"><img src="https://img.shields.io/pypi/dm/celes?color=D4622A&label=downloads" alt="Downloads"/></a>
  <a href="https://marketplace.visualstudio.com/items?itemName=rr1ck.celes-lang"><img src="https://img.shields.io/visual-studio-marketplace/v/rr1ck.celes-lang?color=D4622A&label=vscode" alt="VS Code"/></a>
  <img src="https://img.shields.io/badge/version-0.1.4-D4622A" alt="Version"/>
  <img src="https://img.shields.io/badge/python-3.8%2B-blue" alt="Python"/>
  <img src="https://img.shields.io/badge/license-SOCL--1.0-lightgrey" alt="License"/>
</div>

---

```
<!Celes-0.1.4>
<title>{Hello World}
<header -size=1>{Welcome to Celes}
<line>{This is <bold>{bold}, <mark>{highlighted}, and E=mc<super>{2}.}
<list -bullet=circle>{Simple}
<list -bullet=circle>{Explicit}
<list -bullet=circle>{Powerful}
<line>{<button -body=Get Started>{https://github.com/TheServer-lab/Celes}}
```

---

## Why Celes?

Markdown's symbol-based syntax has real ambiguity problems. A `*` might be bold, italic, or a list item depending on context. Indentation rules differ between parsers. Nested structures are fragile.

Celes takes the opposite approach: **every element is a named tag, every attribute is explicit, and the parser is strict**. If something is wrong, you get an error — not silently broken output.

```
; Markdown — ambiguous
**bold** or __bold__?    * list or *italic*?

; Celes — one way to do everything
<bold>{bold}             <list -bullet=circle>{item}
```

---

## Installation

```bash
pip install celes
```

Requires Python 3.8+. No external dependencies.

---

## CLI

```bash
# Parse Celes → HTML
celes parse doc.celes doc.html

# Validate a file
celes validate doc.celes

# Convert Markdown → Celes
celes md README.md README.celes

# Convert Celes → Markdown
celes tomd doc.celes doc.md
```

---

## Python API

```python
from celes import parse_celes, validate_celes, convert_md_to_celes, convert_celes_to_md

# Parse to HTML
html = parse_celes(source)

# Validate — returns (is_valid, list of errors)
is_valid, errors = validate_celes(source)
for e in errors:
    print(e)  # "  ✗ Line 3: <header> is missing required -size attribute"

# Convert
celes_source = convert_md_to_celes(markdown_source)
markdown_source = convert_celes_to_md(celes_source)
```

---

## Syntax

Every Celes file starts with a version declaration:

```
<!Celes-0.1.4>
```

Comments use a semicolon prefix:

```
; This is a comment
```

### Document & Metadata

| Tag | Description |
|-----|-------------|
| `<title>{text}` | Browser/tab title |
| `<header -size=1>{text}` | Heading, size 1–6 |
| `<author>{name}` | Author metadata (not rendered) |
| `<date>{dd/mm/yyyy}` | Date metadata (not rendered) |
| `<section>{name}` | Named section divider with horizontal rules |

### Block Tags

| Tag | Description |
|-----|-------------|
| `<line>{text}` | Paragraph |
| `<line -align=center>{text}` | Aligned paragraph (`left`, `center`, `right`) |
| `<blockquote>{text}` | Blockquote |
| `<codeblock>{code}` | Multi-line code block |
| `<image>{path/url}` | Image |
| `<linkimage -image=path.png>{url}` | Clickable image |

### Lists

| Tag | Description |
|-----|-------------|
| `<list -bullet=circle>{text}` | Bullet list item |
| `<list -bullet=number>{text}` | Numbered list item |
| `<sublist -bullet=circle>{text}` | Nested item (level 2) |
| `<subsublist -bullet=circle>{text}` | Deeply nested item (level 3) |

### Tables

```
<table>{Name, Age, City}
<item>{Alice, 30, New York}
<item>{Bob, 25, London}
```

> Commas are reserved as column separators — cell values cannot contain commas.

### Self-Closing Tags

| Tag | Description |
|-----|-------------|
| `<newline>` | Line break |
| `<pagebreak>` | Page break |
| `<insertspace>` | Extra spacing / horizontal rule |

### Inline Tags

| Tag | Description |
|-----|-------------|
| `<bold>{text}` | Bold |
| `<italic>{text}` | Italic |
| `<bold+italic>{text}` | Bold and italic |
| `<underline>{text}` | Underline |
| `<strike>{text}` | Strikethrough |
| `<super>{text}` | Superscript |
| `<sub>{text}` | Subscript |
| `<mark>{text}` | Highlighted text |
| `<code>{text}` | Inline code |
| `<link -body=display text>{url}` | Hyperlink |
| `<button -body=label>{url}` | Clickable button |
| `<checkmark -check>{text}` | Checked item (inside `<list>`) |
| `<checkmark -uncheck>{text}` | Unchecked item (inside `<list>`) |
| `<nestquote>{text}` | Nested blockquote (inside `<blockquote>`) |
| `<empty>{raw text}` | Raw text — nothing inside is parsed |

---

## Full Example

```
<!Celes-0.1.4>
<title>{My Page}
<author>{Sourasish Das}
<date>{11/03/2025}

<section>{Introduction}
<header -size=1>{Hello, Celes 0.1.4!}
<line>{This is <bold>{bold}, <italic>{italic}, <mark>{highlighted}, and <super>{superscript} text.}
<line>{Water is H<sub>{2}O. Visit <link -body=example>{https://example.com}.}
<line>{<button -body=Click Me>{https://example.com}}
<newline>

<section>{Lists}
<list -bullet=circle>{Fruits}
<sublist -bullet=circle>{Citrus}
<subsublist -bullet=circle>{Lemon}
<subsublist -bullet=circle>{Lime}
<list -bullet=number>{Step one}
<list -bullet=number>{Step two}
<newline>

<section>{Data}
<table>{Name, Age, City}
<item>{Alice, 30, New York}
<item>{Bob, 25, London}
<newline>
<codeblock>{print("Hello, World!")}
<blockquote>{A quote. <nestquote>{A nested quote.}}
<insertspace>
<line -align=center>{Made with <bold>{Celes} 0.1.4}
```

---

## Tools

### 🖊 WYSIWYG Editor
A standalone browser-based editor — no install needed. Word-like toolbar, live Celes output panel, and a raw Celes playground. Open `celes-editor.html` in any browser.

### 💻 Desktop App
A native Windows application (`Celes.exe`) wrapping the editor with native Open / Save / Export HTML file dialogs.

- `Ctrl+S` — Save
- `Ctrl+Shift+S` — Save As
- `Ctrl+O` — Open `.celes` file
- `Ctrl+Shift+E` — Export to HTML

### 🧩 VS Code Extension
[![VS Marketplace](https://img.shields.io/visual-studio-marketplace/v/rr1ck.celes-lang?label=Install%20from%20Marketplace&color=D4622A)](https://marketplace.visualstudio.com/items?itemName=rr1ck.celes-lang)

Syntax highlighting, snippets for every tag, live validation with error squiggles, and a live HTML preview panel.

### 🌐 Browser Extension
Automatically renders `.celes` files when opened in Chrome or Edge. Available on the Chrome Web Store and Edge Add-ons.

---

## Project Structure

```
Celes/
├── celes/                  # Python package (pip install celes)
│   ├── parser.py           # Celes → HTML
│   ├── validator.py        # Strict validator with line-number errors
│   ├── md_to_celes.py      # Markdown → Celes
│   └── celes_to_md.py      # Celes → Markdown
├── celes-vscode/           # VS Code extension
├── celes-browser/          # Chrome / Edge extension
├── celes-desktop/          # PyInstaller desktop app
├── celes-editor.html       # Standalone WYSIWYG editor
├── Celes-0.1.4-Spec.md     # Full language specification
└── README.md
```

---

## Changelog

### 0.1.4
- Added `<super>`, `<sub>`, `<mark>`, `<button>`, `<subsublist>`, `<section>`, `<author>`, `<date>`
- Desktop app (`Celes.exe`) with native file dialogs
- VS Code extension published to marketplace
- Browser extension published to Chrome Web Store and Edge Add-ons

### 0.1.1 – 0.1.3
- License updated to SOCL 1.0
- Minor parser and packaging fixes

### 0.1.0
- Initial release

---

## License

[Server-Lab Open-Control License (SOCL) 1.0](LICENSE) — Copyright © 2025 Sourasish Das.
