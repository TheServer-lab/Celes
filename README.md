# Celes

> A tag-based markup language designed to be explicit, readable, and unambiguous.

```
<!Celes-0.1>
<title>{Hello World}
<header -size=1>{Welcome to Celes}
<line>{This is <bold>{bold}, <italic>{italic}, and <code>{inline code}.}
<list -bullet=circle>{Simple}<list -bullet=circle>{Explicit}<list -bullet=circle>{Powerful}
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
<!Celes-0.1>
```

### Comments
```
; This is a comment — anything after a semicolon is ignored
```

### Document Tags
| Tag | Description |
|-----|-------------|
| `<title>{text}` | Browser/tab title |
| `<header -size=1>{text}` | Heading, size 1–6 |

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
| `<sublist -bullet=circle>{text}` | Nested sub-item (placed right after `<list>`) |

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
| `<code>{text}` | Inline code |
| `<link -body=display text>{url}` | Hyperlink |
| `<checkmark -check>{text}` | Checked task |
| `<checkmark -uncheck>{text}` | Unchecked task |
| `<nestquote>{text}` | Nested blockquote (inside `<blockquote>`) |
| `<empty>{raw text}` | Raw text — nothing inside is parsed, safe for `<` and `{` |

### Parser Rules
- `{}` content braces are **required** on all content tags — the parser is strict
- Emojis are not part of standard Celes 0.1
- Footnotes are not part of standard Celes 0.1

---

## Full Example

```
<!Celes-0.1>
; My first Celes document
<title>{My Page}
<header -size=1>{Hello, World!}
<line>{This is <bold>{bold} and <italic>{italic} text with a <link -body=link>{https://example.com}.}
<newline>
<list -bullet=circle>{Apples}<sublist -bullet=circle>{Fuji}<sublist -bullet=circle>{Gala}
<list -bullet=number>{First step}
<list -bullet=number>{Second step}
<newline>
<table>{Name, Age, City}
<item>{Alice, 30, New York}
<item>{Bob, 25, London}
<newline>
<codeblock>{print("Hello, World!")}
<blockquote>{A quote. <nestquote>{A nested quote.}}
<line -align=center>{Centered text}
<list -bullet=circle>{<checkmark -check>{Done}}<list -bullet=circle>{<checkmark -uncheck>{Pending}}
<image>{photo.png}
<linkimage -image=photo.png>{https://example.com}
<insertspace>
<empty>{Use <angle brackets> freely in here without breaking the parser.}
```

---

## Tools

### VS Code Extension

Full language support for `.celes` files in Visual Studio Code:

- Syntax highlighting
- Snippets for every tag (type `header`, `line`, `table`, etc. and press Tab)
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
├── Celes-0.1-Spec.md       # Full language specification
├── setup.py
└── README.md
```

---

## License

Server-Lab Open-Control License (SOCL) 1.0 — Copyright (c) 2025 Sourasish Das.

See [LICENSE](LICENSE) for full terms.
