<div align="center">
  <img src="celes-icons/celes-128.png" width="96" alt="Celes logo"/>
  <h1>Celes</h1>
  <p>A markup language designed for archiving. Explicit syntax. Built to last.</p>

  <a href="https://pypi.org/project/celes/"><img src="https://img.shields.io/pypi/v/celes?color=D4622A&label=pypi" alt="PyPI"/></a>
  <a href="https://pypi.org/project/celes/"><img src="https://img.shields.io/pypi/dm/celes?color=D4622A&label=downloads" alt="Downloads"/></a>
  <a href="https://marketplace.visualstudio.com/items?itemName=TheServer-lab.celes-lang"><img src="https://img.shields.io/visual-studio-marketplace/v/TheServer-lab.celes-lang?color=D4622A&label=vscode" alt="VS Code"/></a>
  <img src="https://img.shields.io/badge/version-0.1.5-D4622A" alt="Version"/>
  <img src="https://img.shields.io/badge/python-3.8%2B-blue" alt="Python"/>
  <img src="https://img.shields.io/badge/license-SOCL--1.0-lightgrey" alt="License"/>
</div>

---

```
<!Celes-0.1.5>
<title>{Hello World}
<background>{#0f0f0f}
<header -size=1>{Welcome to Celes}
<line>{This is <bold>{bold}, <mark>{highlighted}, and <coloredtext -color=#D4622A>{colored} text.}
<list -bullet=circle>{Plain text — readable forever}
<list -bullet=circle>{Strict parser — errors are never silent}
<list -bullet=circle>{Version-stamped — every file knows its spec}
<line>{<button -body=Get Started>{https://celes.is-best.net}}
```

---

## Why Celes?

Most document formats are designed to look good today. **Celes is designed to still be readable in 50 years.**

Word documents corrupt. Markdown parsers disagree on spec. HTML rots. PDFs are opaque binaries. None of them were built with long-term archiving as the primary goal.

Celes is plain UTF-8 text with named tags and explicit attributes. Every document declares its version at the top. A future parser — or a human with no tooling — can read it without guessing.

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
<!Celes-0.1.5>
```

Comments use a semicolon prefix:

```
; This is a comment
```

### Document & Metadata

| Tag | Description |
|-----|-------------|
| `<title>{text}` | Browser/tab title |
| `<author>{name}` | Author metadata (not rendered) |
| `<date>{dd/mm/yyyy}` | Date metadata (not rendered) |
| `<background>{color}` | Page background — named color or hex e.g. `#1a1a2e` *(new in 0.1.5)* |

### Block Tags

| Tag | Description |
|-----|-------------|
| `<header -size=1>{text}` | Heading, size 1–6 |
| `<section>{name}` | Named section divider with horizontal rules |
| `<line>{text}` | Paragraph |
| `<line -align=center>{text}` | Aligned paragraph (`left`, `center`, `right`) |
| `<blockquote>{text}` | Blockquote |
| `<codeblock>{code}` | Multi-line code block (raw — nothing inside is parsed) |
| `<image>{path/url}` | Image |
| `<linkimage -image=path.png>{url}` | Clickable image |
| `<video>{url}` | HTML5 video player *(new in 0.1.5)* |
| `<audio>{url}` | HTML5 audio player *(new in 0.1.5)* |

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
| `<coloredtext -color=value>{text}` | Colored text — named color or hex *(new in 0.1.5)* |
| `<link -body=display text>{url}` | Hyperlink |
| `<button -body=label>{url}` | Clickable button |
| `<checkmark -check>{text}` | Checked item (inside `<list>`) |
| `<checkmark -uncheck>{text}` | Unchecked item (inside `<list>`) |
| `<nestquote>{text}` | Nested blockquote (inside `<blockquote>`) |
| `<empty>{raw text}` | Raw text — nothing inside is parsed |

### Video & Audio Attributes

| Tag | Attribute | Description |
|-----|-----------|-------------|
| `<video>` | `-loop` | Loops on end |
| `<video>` | `-autoplay` | Plays on load (pair with `-mute` for browser compatibility) |
| `<video>` | `-mute` | Muted playback |
| `<audio>` | `-loop` | Loops on end |
| `<audio>` | `-autoplay` | Plays on load |

---

## Full Example

```
<!Celes-0.1.5>
<title>{My Page}
<author>{Sourasish Das}
<date>{13/03/2025}
<background>{#0f0f0f}

<section>{Introduction}
<header -size=1>{Hello, Celes 0.1.5!}
<line>{This is <bold>{bold}, <italic>{italic}, <mark>{highlighted}, and <coloredtext -color=#D4622A>{colored} text.}
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

<section>{Media}
<video -loop -mute>{assets/demo.mp4}
<audio>{podcast-episode-1.mp3}
<insertspace>
<line -align=center>{Made with <bold>{Celes} 0.1.5}
```

---

## Tools

### 🖊 WYSIWYG Editor
A standalone browser-based editor — no install needed. Word-like toolbar, live Celes output panel, and a raw Celes playground. [Try it online](https://celes.is-best.net/celes-editor.html) or open `celes-editor.html` in any browser.

### 💻 Desktop App
A native Windows application (`Celes.exe`) wrapping the editor with native Open / Save / Export HTML file dialogs.

- `Ctrl+S` — Save
- `Ctrl+Shift+S` — Save As
- `Ctrl+O` — Open `.celes` file
- `Ctrl+Shift+E` — Export to HTML

### 🧩 VS Code Extension
[![VS Marketplace](https://img.shields.io/visual-studio-marketplace/v/TheServer-lab.celes-lang?label=Install%20from%20Marketplace&color=D4622A)](https://marketplace.visualstudio.com/items?itemName=TheServer-lab.celes-lang)

Syntax highlighting, snippets for every tag, live validation with error squiggles, and a live HTML preview panel.

### 🌐 Browser Extension
Automatically renders `.celes` files when opened in Chrome or Edge. Supports `file://` and `http://` URLs.

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
├── Celes-0.1.5-Spec.md     # Full language specification
└── README.md
```

---

## Changelog

### 0.1.5
- Added `<video>` — HTML5 video player with `-loop`, `-autoplay`, `-mute`
- Added `<audio>` — HTML5 audio player with `-loop`, `-autoplay`
- Added `<background>` — document-level page background color
- Added `<coloredtext -color=value>` — inline colored text
- Parser: `<coloredtext>` without `-color` is a parse error
- Parser: duplicate `<background>` warns and uses first value
- Parser: `<video>`/`<audio>` used inline is a parse error
- Parser: `-autoplay` without `-mute` on `<video>` warns
- Fixed multiline `<codeblock>` parsing in all JS parsers

### 0.1.4
- Added `<super>`, `<sub>`, `<mark>`, `<button>`, `<subsublist>`, `<section>`, `<author>`, `<date>`
- Desktop app (`Celes.exe`) with native file dialogs
- VS Code extension published to marketplace
- Browser extension for Chrome and Edge

### 0.1.1 – 0.1.3
- License updated to SOCL 1.0
- Minor parser and packaging fixes

### 0.1.0
- Initial release

---

## License

[Server-Lab Open-Control License (SOCL) 1.0](LICENSE) — Copyright © 2025 Sourasish Das.
