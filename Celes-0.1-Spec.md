# Celes 0.1 — Language Specification

Celes is a tag-based markup language. The core syntax is `<tag>{content}`, with optional attributes using `-attribute=value`.

---

## Document Declaration

Every Celes file should begin with a version declaration:

```
<!Celes-0.1>
```

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

---

## Block Tags

| Tag | Description |
|-----|-------------|
| `<line>{text}` | A paragraph line. Supports inline tags. |
| `<line -align=left>{text}` | Left-aligned line (default) |
| `<line -align=center>{text}` | Centered line |
| `<line -align=right>{text}` | Right-aligned line |
| `<blockquote>{text}` | A blockquote. Supports inline tags, `<newline>`, and `<nestquote>` inside. |
| `<codeblock>{code}` | A multi-line block of code |
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
| `<insertspace>` | Inserts extra spacing |

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
| `<code>{text}` | Inline code |
| `<link -body=visible text>{url}` | A hyperlink. `-body` is the display text, content is the URL. |
| `<nestquote>{text}` | A nested blockquote inside a `<blockquote>` |
| `<empty>{text}` | Raw plain text — nothing inside is parsed. Use for literal `<`, `{`, `}` characters. |

---

## Parser Rules

- The `{}` content braces are **required** on all content tags. `<line>text` is invalid; `<line>{text}` is correct.
- The parser is **strict** — malformed tags will not be rendered leniently.
- Emojis are **not** part of standard Celes 0.1.

```
<!Celes-0.1>
; This is a sample Celes document
<title>{My Page}
<header -size=1>{Hello, World!}
<line>{This is a <bold>{bold} word and this is <italic>{italic} text.}
<line>{Visit <link -body=Anthropic>{https://anthropic.com} for more.}
<newline>
<list -bullet=circle>{First item}<sublist -bullet=circle>{Sub-item}
<list -bullet=number>{Second item}
<newline>
<table>{Name, Age, City}
<item>{Alice, 30, New York}
<item>{Bob, 25, London}
<newline>
<codeblock>{print("Hello, World!")}
<image>{assets/logo.png}
<linkimage -image=assets/logo.png>{https://example.com}
```
