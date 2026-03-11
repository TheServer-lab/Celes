# Celes

> A tag-based markup language designed to be explicit, readable, and unambiguous.

```
<!Celes-0.1.4>
<author>{Sourasish Das}
<date>{11/03/2025}
<title>{Hello World}
<header -size=1>{Welcome to Celes}
<line>{This is <bold>{bold}, <mark>{highlighted}, and E=mc<super>{2}.}
<list -bullet=circle>{Simple}<list -bullet=circle>{Explicit}<list -bullet=circle>{Powerful}
<line>{<button -body=Get Started>{https://github.com/TheServer-lab/celes}}
```

---

## What is Celes?

Celes is a markup language alternative to Markdown. Where Markdown relies on symbols and whitespace rules that can behave unpredictably, Celes uses a consistent `<tag>{content}` syntax — every element is named, every attribute is explicit, and the parser is strict.

---

## Installation

```bash
pip install celes
```

Requires Python 3.8+. No external dependencies.

---

## CLI Usage

```bash
# Convert a Celes file to HTML
py -m celes parse doc.celes doc.html

# Validate a Celes file
py -m celes validate doc.celes

# Convert Markdown → Celes
py -m celes md README.md README.celes

# Convert Celes → Markdown
py -m celes tomd doc.celes doc.md
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

## Syntax Reference

### Document Declaration
Every Celes file starts with:
```
<!Celes-0.1.4>
```

### Comments
```
; This is a comment — anything after a semicolon is ignored
```

### Document & Metadata Tags
| Tag | Description |
|-----|-------------|
| `<title>{text}` | Browser/tab title (not visible on page) |
| `<author>{name}` | Document author metadata (not visible on page) |
| `<date>{dd/mm/yyyy}` | Document date metadata (not visible on page) |
| `<header -size=1>{text}` | Heading, size 1–6 |

### Section Tag
```
<section>{Introduction}
<line>{This content belongs to the Introduction section.}

<section>{Conclusion}
<line>{This content belongs to the Conclusion section.}
```
Renders as a styled label with horizontal rules on either side.

### Block Tags
| Tag | Description |
|-----|-------------|
| `<line>{text}` | Paragraph line |
| `<line -align=center>{text}` | Aligned line (`left`, `center`, `right`) |
| `<blockquote>{text}` | Blockquote, supports `<nestquote>` inside |
| `<codeblock>{code}` | Multi-line code block |
| `<image>{path/url}` | Image |
| `<linkimage -image=path.png>{url}` | Clickable image |

### Lists
| Tag | Description |
|-----|-------------|
| `<list -bullet=circle>{text}` | Bullet list item |
| `<list -bullet=number>{text}` | Numbered list item |
| `<sublist -bullet=circle>{text}` | Nested sub-item (level 2) |
| `<sublist -bullet=number>{text}` | Numbered nested sub-item (level 2) |
| `<subsublist -bullet=circle>{text}` | Deeply nested item (level 3) |
| `<subsublist -bullet=number>{text}` | Numbered deeply nested item (level 3) |

### Tables
```
<table>{Name, Age, City}
<item>{Alice, 30, New York}
<item>{Bob, 25, London}
```
> Note: cell values cannot contain commas — commas are reserved as column separators.

### Self-Closing Tags
| Tag | Description |
|-----|-------------|
| `<newline>` | Line break |
| `<pagebreak>` | Page break |
| `<insertspace>` | Extra spacing / horizontal rule |

### Inline Tags
Used inside `<line>`, `<blockquote>`, and list content:

| Tag | Description |
|-----|-------------|
| `<bold>{text}` | Bold |
| `<italic>{text}` | Italic |
| `<bold+italic>{text}` | Bold and italic combined |
| `<underline>{text}` | Underline |
| `<strike>{text}` | Strikethrough |
| `<super>{text}` | Superscript (e.g. x`<super>{2}`) |
| `<sub>{text}` | Subscript (e.g. H`<sub>{2}`O) |
| `<mark>{text}` | Highlighted text |
| `<code>{text}` | Inline code |
| `<link -body=display text>{url}` | Hyperlink |
| `<button -body=label>{url}` | Clickable button that links to a URL |
| `<checkmark -check>{text}` | Checked task (inside `<list>`) |
| `<checkmark -uncheck>{text}` | Unchecked task (inside `<list>`) |
| `<nestquote>{text}` | Nested blockquote (inside `<blockquote>`) |
| `<empty>{raw text}` | Raw text — nothing inside is parsed, safe for `<` and `{` |

### Parser Rules
- `{}` content braces are **required** on all content tags — the parser is strict
- Emojis are not part of standard Celes 0.1.x
- Footnotes are not part of standard Celes 0.1.x

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
<sublist -bullet=circle>{Citrus}<subsublist -bullet=circle>{Lemon}<subsublist -bullet=circle>{Lime}
<sublist -bullet=circle>{Berries}
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
<image>{photo.png}
<insertspace>
<line -align=center>{Made with <bold>{Celes} 0.1.4}
```

---

## Tools

### WYSIWYG Editor

A browser-based Word-like editor that outputs Celes markup live as you type — no installation needed.

- Toolbar with bold, italic, headings, lists, tables, links, and more
- Live Celes output panel with syntax highlighting
- Playground tab to write raw Celes and see it render instantly
- Download as `.celes` file

Open `celes-editor.html` directly in any browser.

### VS Code Extension

Full language support for `.celes` files in Visual Studio Code:

- Syntax highlighting
- Snippets for every tag (type the tag name and press Tab)
- Validation with error squiggles as you type
- Live HTML preview side panel

**Installation:** Requires Node.js.

```bash
cd celes-vscode
npm install
npm install -g vsce
vsce package
```

Then in VS Code: **Extensions → ··· → Install from VSIX** and select the generated `.vsix` file.

The preview and validation require the `celes` Python package to be installed.

### Browser Extension (Chrome & Edge)

Automatically renders `.celes` files when opened directly in the browser. Displays a styled page with a **View Source** toggle.

**Installation:**
1. Go to `chrome://extensions` or `edge://extensions`
2. Enable **Developer mode**
3. Click **Load unpacked**
4. Select the `celes-browser` folder

---

## Project Structure

```
celes/
├── celes/                  # Python package
│   ├── __init__.py
│   ├── core.py             # Shared tokenizer and utilities
│   ├── parser.py           # Celes → HTML
│   ├── validator.py        # Validator with line-number errors
│   ├── md_to_celes.py      # Markdown → Celes
│   └── celes_to_md.py      # Celes → Markdown
├── celes-vscode/           # VS Code extension
│   ├── src/extension.js
│   ├── syntaxes/
│   ├── snippets/
│   └── package.json
├── celes-browser/          # Chrome/Edge browser extension
│   ├── manifest.json
│   ├── celes-parser.js
│   ├── content.js
│   └── popup.html
├── celes-editor.html       # Standalone WYSIWYG editor
├── Celes-0.1.4-Spec.md     # Full language specification
├── setup.py
└── README.md
```

---

## Changelog

### 0.1.4
- Added `<super>{text}` — superscript
- Added `<sub>{text}` — subscript
- Added `<mark>{text}` — highlighted text
- Added `<button -body=label>{url}` — clickable button
- Added `<subsublist>` — third-level nested list items
- Added `<author>{name}` — document author metadata
- Added `<date>{dd/mm/yyyy}` — document date metadata
- Added `<section>{name}` — named section divider

### 0.1.1 – 0.1.3
- License updated to SOCL 1.0
- Minor parser and packaging fixes

### 0.1.0
- Initial release

---

## License

Server-Lab Open-Control License (SOCL) 1.0 — Copyright (c) 2025 Sourasish Das.

See [LICENSE](LICENSE) for full terms.
