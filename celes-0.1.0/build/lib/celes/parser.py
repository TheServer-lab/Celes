"""
Celes Parser — converts Celes source to HTML.
Supports Celes 0.1.5.
"""

from html import escape
from .core import tokenize, find_matching_brace, parse_attributes, SELF_CLOSING_TAGS, CSS_COLOR_PATTERN


def parse_inline(content):
    nodes = []
    i = 0
    while i < len(content):
        tag_start = content.find('<', i)
        if tag_start == -1:
            if i < len(content):
                nodes.append({'type': 'text', 'text': content[i:]})
            break
        if tag_start > i:
            nodes.append({'type': 'text', 'text': content[i:tag_start]})
        tag_end = content.find('>', tag_start)
        if tag_end == -1:
            nodes.append({'type': 'text', 'text': content[tag_start:]})
            break
        tag_header = content[tag_start + 1:tag_end]
        import re
        header_match = re.match(r'^([\w+]+)(.*)', tag_header, re.DOTALL)
        if not header_match:
            nodes.append({'type': 'text', 'text': content[tag_start:tag_end + 1]})
            i = tag_end + 1
            continue
        tagname = header_match.group(1).lower()
        attrs = parse_attributes(header_match.group(2))
        after_tag = tag_end + 1
        if after_tag < len(content) and content[after_tag] == '{':
            close = find_matching_brace(content, after_tag)
            if close != -1:
                inner = content[after_tag + 1:close]
                nodes.append({'type': 'tag', 'name': tagname, 'attrs': attrs, 'content': inner})
                i = close + 1
                continue
        nodes.append({'type': 'tag', 'name': tagname, 'attrs': attrs, 'content': None})
        i = after_tag
    return nodes


def inline_to_html(content, raw=False):
    if raw or content is None:
        return escape(content or '')
    return ''.join(node_to_html(n) for n in parse_inline(content))


def node_to_html(node):
    if node['type'] == 'text':
        return escape(node['text'])
    name = node['name']
    attrs = node['attrs']
    inner = node['content'] or ''
    mapping = {
        'bold':        lambda: f'<strong>{inline_to_html(inner)}</strong>',
        'italic':      lambda: f'<em>{inline_to_html(inner)}</em>',
        'bold+italic': lambda: f'<strong><em>{inline_to_html(inner)}</em></strong>',
        'underline':   lambda: f'<u>{inline_to_html(inner)}</u>',
        'strike':      lambda: f'<s>{inline_to_html(inner)}</s>',
        'super':       lambda: f'<sup>{inline_to_html(inner)}</sup>',
        'sub':         lambda: f'<sub>{inline_to_html(inner)}</sub>',
        'mark':        lambda: f'<mark>{inline_to_html(inner)}</mark>',
        'code':        lambda: f'<code>{escape(inner)}</code>',
        'newline':     lambda: '<br>',
        'empty':       lambda: inline_to_html(inner, raw=True),
        'nestquote':   lambda: f'<blockquote class="nested">{inline_to_html(inner)}</blockquote>',
    }
    if name in mapping:
        return mapping[name]()
    if name == 'link':
        body = attrs.get('body', inner)
        return f'<a href="{escape(inner)}">{escape(body)}</a>'
    if name == 'button':
        body = attrs.get('body', inner)
        return f'<a href="{escape(inner)}" class="celes-button">{escape(body)}</a>'
    if name == 'checkmark':
        checked = 'checked' if 'check' in attrs else ''
        return f'<input type="checkbox" {checked} disabled> {inline_to_html(inner)}'
    # 0.1.5 — coloredtext
    if name == 'coloredtext':
        color = attrs.get('color', '')
        safe_color = escape(str(color))
        return f'<span style="color:{safe_color}">{inline_to_html(inner)}</span>'
    return escape(inner)


def tags_to_html(tags):
    title = 'Celes Document'
    bg_color = None
    body_parts = []
    i = 0
    while i < len(tags):
        _, tagname, attrs, content = tags[i]

        if tagname in ('comment', 'declaration'):
            i += 1; continue

        if tagname == 'title':
            title = content or ''
            i += 1

        elif tagname in ('author', 'date'):
            i += 1

        # 0.1.5 — background (document-level, not rendered as block)
        elif tagname == 'background':
            if bg_color is None:
                bg_color = (content or '').strip()
            i += 1

        elif tagname == 'section':
            body_parts.append(
                f'<div class="celes-section"><span class="celes-section-label">{inline_to_html(content)}</span></div>'
            )
            i += 1

        elif tagname == 'header':
            size = attrs.get('size', '1')
            body_parts.append(f'<h{size}>{inline_to_html(content)}</h{size}>')
            i += 1

        elif tagname == 'line':
            align = attrs.get('align', '')
            style = f' style="text-align:{escape(align)}"' if align else ''
            body_parts.append(f'<p{style}>{inline_to_html(content)}</p>')
            i += 1

        elif tagname == 'blockquote':
            body_parts.append(f'<blockquote>{inline_to_html(content)}</blockquote>')
            i += 1

        elif tagname == 'codeblock':
            body_parts.append(f'<pre><code>{escape(content or "")}</code></pre>')
            i += 1

        elif tagname == 'image':
            body_parts.append(f'<img src="{escape(content or "")}" alt="">')
            i += 1

        elif tagname == 'linkimage':
            img_src = attrs.get('image', '')
            body_parts.append(
                f'<a href="{escape(content or "")}">'
                f'<img src="{escape(img_src)}" alt=""></a>'
            )
            i += 1

        # 0.1.5 — video
        elif tagname == 'video':
            src = escape(content or '')
            loop     = ' loop'     if 'loop'     in attrs else ''
            autoplay = ' autoplay' if 'autoplay' in attrs else ''
            muted    = ' muted'    if 'mute'     in attrs else ''
            body_parts.append(
                f'<video controls{loop}{autoplay}{muted} class="celes-video">'
                f'<source src="{src}">'
                f'Your browser does not support the video tag.'
                f'</video>'
            )
            i += 1

        # 0.1.5 — audio
        elif tagname == 'audio':
            src = escape(content or '')
            loop     = ' loop'     if 'loop'     in attrs else ''
            autoplay = ' autoplay' if 'autoplay' in attrs else ''
            body_parts.append(
                f'<audio controls{loop}{autoplay} class="celes-audio">'
                f'<source src="{src}">'
                f'Your browser does not support the audio tag.'
                f'</audio>'
            )
            i += 1

        elif tagname == 'table':
            cols = [c.strip() for c in (content or '').split(',')]
            header_cells = ''.join(f'<th>{escape(c)}</th>' for c in cols)
            rows = [f'<thead><tr>{header_cells}</tr></thead>']
            body_rows = []
            i += 1
            while i < len(tags) and tags[i][1] == 'item':
                cells = [c.strip() for c in (tags[i][3] or '').split(',')]
                cell_html = ''.join(f'<td>{escape(c)}</td>' for c in cells)
                body_rows.append(f'<tr>{cell_html}</tr>')
                i += 1
            rows.append(f'<tbody>{"".join(body_rows)}</tbody>')
            body_parts.append(f'<table>{"".join(rows)}</table>')

        elif tagname == 'list':
            list_items = []
            while i < len(tags) and tags[i][1] == 'list':
                item_attrs = tags[i][2]
                item_content = tags[i][3] or ''
                bullet = item_attrs.get('bullet', 'circle')
                list_type = 'ol' if bullet == 'number' else 'ul'
                i += 1
                sub_items = []
                sub_type = 'ul'
                while i < len(tags) and tags[i][1] == 'sublist':
                    sub_bullet = tags[i][2].get('bullet', 'circle')
                    sub_type = 'ol' if sub_bullet == 'number' else 'ul'
                    sub_content = tags[i][3] or ''
                    i += 1
                    subsub_items = []
                    subsub_type = 'ul'
                    while i < len(tags) and tags[i][1] == 'subsublist':
                        subsub_bullet = tags[i][2].get('bullet', 'circle')
                        subsub_type = 'ol' if subsub_bullet == 'number' else 'ul'
                        subsub_items.append(f'<li>{inline_to_html(tags[i][3] or "")}</li>')
                        i += 1
                    subsub_html = f'<{subsub_type}>{"".join(subsub_items)}</{subsub_type}>' if subsub_items else ''
                    sub_items.append(f'<li>{inline_to_html(sub_content)}{subsub_html}</li>')
                sub_html = f'<{sub_type}>{"".join(sub_items)}</{sub_type}>' if sub_items else ''
                list_items.append((list_type, item_content, sub_html))
            groups = []
            if list_items:
                current_type = list_items[0][0]
                current_items = []
                for lt, lc, ls in list_items:
                    if lt != current_type and current_items:
                        groups.append((current_type, current_items))
                        current_items = []
                        current_type = lt
                    current_items.append((lc, ls))
                if current_items:
                    groups.append((current_type, current_items))
            for lt, items in groups:
                lis = ''.join(f'<li>{inline_to_html(c)}{s}</li>' for c, s in items)
                body_parts.append(f'<{lt}>{lis}</{lt}>')

        elif tagname == 'newline':
            body_parts.append('<br>')
            i += 1

        elif tagname == 'pagebreak':
            body_parts.append('<div style="page-break-after:always"></div>')
            i += 1

        elif tagname == 'insertspace':
            body_parts.append('<div style="margin:2em 0"></div>')
            i += 1

        elif tagname == 'error':
            body_parts.append(f'<div class="celes-error">⚠ {escape(content or "")}</div>')
            i += 1

        else:
            i += 1

    body = '\n'.join(body_parts)

    # Build background style
    bg_style = f'background-color:{escape(bg_color)};' if bg_color else ''
    body_style = f' style="{bg_style}"' if bg_style else ''

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{escape(title)}</title>
  <style>
    body {{
      font-family: system-ui, sans-serif;
      max-width: 800px;
      margin: 2rem auto;
      padding: 0 1.5rem;
      line-height: 1.7;
      color: #222;
    }}
    h1, h2, h3, h4, h5, h6 {{ line-height: 1.3; margin-top: 1.5em; }}
    blockquote {{
      border-left: 4px solid #ccc;
      margin: 1em 0;
      padding: 0.4rem 1rem;
      color: #555;
    }}
    blockquote.nested {{
      border-left: 4px solid #aaa;
      margin-left: 1.5rem;
    }}
    pre {{
      background: #f5f5f5;
      padding: 1rem;
      border-radius: 5px;
      overflow-x: auto;
    }}
    code {{
      background: #f0f0f0;
      padding: 0.15em 0.4em;
      border-radius: 3px;
      font-size: 0.92em;
    }}
    pre code {{ background: none; padding: 0; font-size: 1em; }}
    table {{
      border-collapse: collapse;
      width: 100%;
      margin: 1em 0;
    }}
    th, td {{
      border: 1px solid #ccc;
      padding: 0.5rem 1rem;
      text-align: left;
    }}
    th {{ background: #f0f0f0; font-weight: 600; }}
    img {{ max-width: 100%; height: auto; }}
    input[type="checkbox"] {{ margin-right: 0.4em; }}
    mark {{ background: #fff176; padding: 0.05em 0.2em; border-radius: 2px; }}
    .celes-button {{
      display: inline-block;
      background: #D4622A;
      color: #fff;
      padding: 0.35em 0.9em;
      border-radius: 5px;
      text-decoration: none;
      font-size: 0.9em;
      font-weight: 500;
      margin: 0 0.1em;
    }}
    .celes-button:hover {{ background: #b84e1e; }}
    .celes-section {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
      margin: 2em 0 1em;
    }}
    .celes-section::before, .celes-section::after {{
      content: '';
      flex: 1;
      height: 1px;
      background: #ddd;
    }}
    .celes-section-label {{
      font-size: 0.75rem;
      font-weight: 600;
      color: #888;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      white-space: nowrap;
    }}
    .celes-error {{
      color: #c00;
      background: #fff0f0;
      border: 1px solid #fcc;
      padding: 0.4rem 0.8rem;
      border-radius: 4px;
      font-family: monospace;
      margin: 0.5em 0;
    }}
    .celes-video, .celes-audio {{
      width: 100%;
      margin: 1em 0;
      border-radius: 6px;
    }}
    .celes-audio {{
      height: 48px;
    }}
  </style>
</head>
<body{body_style}>
{body}
</body>
</html>"""


def parse_celes(source):
    """Parse a Celes source string and return an HTML string."""
    tokens = tokenize(source)
    return tags_to_html(tokens)
