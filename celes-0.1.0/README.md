# Celes 0.1

A tag-based markup language and toolkit. Write documents in Celes, convert to HTML, validate, or round-trip with Markdown.

## Install

```bash
pip install celes
```

## CLI Usage

```bash
# Convert a Celes file to HTML
celes parse doc.celes doc.html

# Validate a Celes file
celes validate doc.celes

# Convert Markdown to Celes
celes md README.md README.celes

# Convert Celes to Markdown
celes tomd doc.celes doc.md
```

## Python API

```python
from celes import parse_celes, validate_celes, convert_md_to_celes, convert_celes_to_md

# Parse to HTML
html = parse_celes(source)

# Validate
is_valid, errors = validate_celes(source)
for e in errors:
    print(e)  # "  ✗ Line 3: <header> is missing required -size attribute"

# Convert
celes_source = convert_md_to_celes(markdown_source)
markdown_source = convert_celes_to_md(celes_source)
```

## Celes Syntax (0.1)

```
<!Celes-0.1>
; This is a comment
<title>{My Page}
<header -size=1>{Hello, World!}
<line>{This is <bold>{bold} and <italic>{italic} text.}
<list -bullet=circle>{Item one}<sublist -bullet=circle>{Sub-item}
<list -bullet=number>{Numbered item}
<table>{Name, Age}
<item>{Alice, 30}
<codeblock>{print("hello")}
<image>{photo.png}
<linkimage -image=photo.png>{https://example.com}
<blockquote>{A quote <nestquote>{nested}}
<line -align=center>{Centered}
<newline>
<pagebreak>
<insertspace>
<empty>{<raw> text with <angle> brackets}
```
