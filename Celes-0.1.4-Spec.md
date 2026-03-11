# Celes 0.1.4 — Language Specification

Celes is a tag-based markup language. The core syntax is `<tag>{content}`, with optional attributes using `-attribute=value`.

---

## Document Declaration

Every Celes file should begin with a version declaration:

```
<!Celes-0.1.4>
```

Previous versions (`<!Celes-0.1>`) remain valid and are parsed identically.

---

## Comments

```
; This is a comment
```

Anything following a semicolon on a line is treated as a comment and will not be rendered.

---

## Document Tags

| Tag | Description |
|-----|-------------|
| `<title>{text}` | Sets the tab/browser title (not visible on the page) |
| `<header -size=1>{text}` | Visible heading on the page. Size ranges from 1–6 (like HTML h1–h6) |
| `<author>{name}` | Document author metadata (not visible on the page) |
| `<date>{dd/mm/yyyy}` | Document date metadata (not visible on the page) |

---

## Section Tag

Sections group blocks of content under a named heading. A section begins at `<section>` and ends at the next `<section>` or end of file.

```
<section>{Introduction}
<line>{This is the introduction.}

<section>{Conclusion}
<line>{This is the conclusion.}
```

Sections render as a styled divider with the section title, similar to a thematic break.

---

## Block Tags

| Tag | Description |
|-----|-------------|
| `<line>{text}` | A paragraph line. Supports inline tags. |
| `<line -align=left>{text}` | Left-aligned line (default) |
| `<line -align=center>{text}` | Centered line |
| `<line -align=right>{text}` | Right-aligned line |
| `<blockquote>{text}` | A blockquote. Supports inline tags, `<newline>`, and `<nestquote>` inside. |
| `<codeblock>{code}` | A multi-line code block |
| `<image>{path/or/url}` | Displays an image from a path or URL |
| `<linkimage -image=path.png>{url}` | A clickable image that links to a URL |

---

## List Tags

| Tag | Description |
|-----|-------------|
| `<list -bullet=circle>{text}` | A bullet list item |
| `<list -bullet=number>{text}` | A numbered list item |
| `<sublist -bullet=circle>{text}` | A nested bullet sub-item (placed immediately after its parent `<list>`) |
| `<sublist -bullet=number>{text}` | A nested numbered sub-item |
| `<subsublist -bullet=circle>{text}` | A third-level nested bullet item (placed immediately after its parent `<sublist>`) |
| `<subsublist -bullet=number>{text}` | A third-level nested numbered item |

Checkboxes can be placed inside `<list>` items as inline tags:

| Tag | Description |
|-----|-------------|
| `<checkmark -check>{text}` | A checked/completed task |
| `<checkmark -uncheck>{text}` | An unchecked/incomplete task |

---

## Table Tags

```
<table>{Column1, Column2, Column3}
<item>{Value1, Value2, Value3}
<item>{Value4, Value5, Value6}
```

- `<table>` defines the header row with comma-separated column names.
- `<item>` defines each data row with comma-separated values.
- **Note:** Commas are reserved as separators — cell values cannot contain commas.

---

## Self-Closing Tags

These tags take no `{}` content:

| Tag | Description |
|-----|-------------|
| `<newline>` | Inserts a line break |
| `<pagebreak>` | Inserts a page break |
| `<insertspace>` | Inserts extra spacing / horizontal rule |

---

## Inline Tags

These are used **inside** `<line>{...}` content:

| Tag | Description |
|-----|-------------|
| `<bold>{text}` | Bold text |
| `<italic>{text}` | Italic text |
| `<bold+italic>{text}` | Bold and italic combined |
| `<underline>{text}` | Underlined text |
| `<strike>{text}` | Strikethrough text |
| `<super>{text}` | Superscript text (e.g. x`<super>{2}`) |
| `<sub>{text}` | Subscript text (e.g. H`<sub>{2}`O) |
| `<mark>{text}` | Highlighted / marked text |
| `<code>{text}` | Inline code |
| `<link -body=visible text>{url}` | A hyperlink. `-body` is the display text, content is the URL. |
| `<button -body=label>{url}` | A clickable button that links to a URL. |
| `<nestquote>{text}` | A nested blockquote inside a `<blockquote>` |
| `<empty>{text}` | Raw plain text — nothing inside is parsed. Use for literal `<`, `{`, `}` characters. |

---

## Parser Rules

- The `{}` content braces are **required** on all content tags. `<line>text` is invalid; `<line>{text}` is correct.
- The parser is **strict** — malformed tags will not be rendered leniently.
- Emojis are **not** part of standard Celes 0.1.x.
- Footnotes are **not** part of standard Celes 0.1.x.

---

## Example Document

```
<!Celes-0.1.4>
; A full example document
<title>{My Page}
<author>{Sourasish Das}
<date>{11/03/2025}

<section>{Introduction}
<header -size=1>{Hello, Celes 0.1.4!}
<line>{This is <bold>{bold}, <italic>{italic}, <mark>{highlighted}, and <super>{superscript}.}
<line>{Water is H<sub>{2}O. Einstein's formula: E = mc<super>{2}.}
<line>{Click here: <button -body=Visit Site>{https://example.com}}
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
```

---

## Changelog

### 0.1.4
- Added `<super>` — superscript inline tag
- Added `<sub>` — subscript inline tag
- Added `<mark>` — highlight/mark inline tag
- Added `<button -body=label>{url}` — clickable button inline tag
- Added `<subsublist>` — third-level nested list items
- Added `<author>` — document author metadata tag
- Added `<date>` — document date metadata tag
- Added `<section>` — named section divider block tag

### 0.1.1 – 0.1.3
- License updated to SOCL 1.0
- Minor parser and packaging fixes

### 0.1.0
- Initial release
