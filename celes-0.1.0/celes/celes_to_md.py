"""
Celes 0.1 — Celes to Markdown converter.
"""

import re
from .core import tokenize, find_matching_brace, parse_attributes


def inline_to_md(content):
    if content is None:
        return ''
    result = ''
    i = 0
    while i < len(content):
        tag_start = content.find('<', i)
        if tag_start == -1:
            result += content[i:]
            break
        result += content[i:tag_start]
        tag_end = content.find('>', tag_start)
        if tag_end == -1:
            result += content[tag_start:]
            break
        tag_header = content[tag_start + 1:tag_end]
        header_match = re.match(r'^([\w+]+)(.*)', tag_header, re.DOTALL)
        if not header_match:
            result += content[tag_start:tag_end + 1]
            i = tag_end + 1
            continue
        tagname = header_match.group(1).lower()
        attrs = parse_attributes(header_match.group(2))
        after_tag = tag_end + 1
        inner = ''
        end = after_tag
        if after_tag < len(content) and content[after_tag] == '{':
            close = find_matching_brace(content, after_tag)
            if close != -1:
                inner = content[after_tag + 1:close]
                end = close + 1
        inner_md = inline_to_md(inner)
        if tagname == 'bold':              result += f'**{inner_md}**'
        elif tagname == 'italic':          result += f'*{inner_md}*'
        elif tagname == 'bold+italic':     result += f'***{inner_md}***'
        elif tagname == 'underline':       result += f'<u>{inner_md}</u>'
        elif tagname == 'strike':          result += f'~~{inner_md}~~'
        elif tagname == 'code':            result += f'`{inner}`'
        elif tagname == 'link':
            body = attrs.get('body', inner_md)
            result += f'[{body}]({inner})'
        elif tagname == 'newline':         result += '\n'
        elif tagname == 'empty':           result += inner
        elif tagname == 'checkmark':
            checked = 'x' if 'check' in attrs else ' '
            result += f'[{checked}] {inner_md}'
        elif tagname == 'nestquote':       result += f'>> {inner_md}'
        else:                              result += inner_md
        i = end
    return result


def convert_celes_to_md(source):
    tokens = tokenize(source)
    output = []
    title = None
    i = 0

    while i < len(tokens):
        lineno, tagname, attrs, content = tokens[i]

        if tagname == 'declaration':
            i += 1; continue
        elif tagname == 'comment':
            output.append(f'<!-- {content} -->')
            i += 1
        elif tagname == 'title':
            title = content
            i += 1
        elif tagname == 'header':
            size = int(attrs.get('size', 1))
            output.append(f'{"#" * size} {inline_to_md(content)}')
            i += 1
        elif tagname == 'line':
            align = attrs.get('align', '')
            text = inline_to_md(content)
            if align and align != 'left':
                output.append(f'<div align="{align}">{text}</div>')
            else:
                output.append(text)
            i += 1
        elif tagname == 'blockquote':
            text = inline_to_md(content)
            for bq_line in text.splitlines():
                output.append(f'> {bq_line}')
            i += 1
        elif tagname == 'codeblock':
            output.append('```')
            output.append(content or '')
            output.append('```')
            i += 1
        elif tagname == 'image':
            output.append(f'![image]({content})')
            i += 1
        elif tagname == 'linkimage':
            img = attrs.get('image', '')
            output.append(f'[![image]({img})]({content})')
            i += 1
        elif tagname == 'table':
            cols = [c.strip() for c in (content or '').split(',')]
            output.append('| ' + ' | '.join(cols) + ' |')
            output.append('| ' + ' | '.join(['---'] * len(cols)) + ' |')
            i += 1
            while i < len(tokens) and tokens[i][1] == 'item':
                cells = [c.strip() for c in (tokens[i][3] or '').split(',')]
                output.append('| ' + ' | '.join(cells) + ' |')
                i += 1
        elif tagname == 'list':
            counter = 1
            while i < len(tokens) and tokens[i][1] == 'list':
                t_attrs = tokens[i][2]
                t_content = tokens[i][3] or ''
                t_bullet = t_attrs.get('bullet', 'circle')
                text = inline_to_md(t_content)
                if t_bullet == 'number':
                    output.append(f'{counter}. {text}')
                    counter += 1
                else:
                    output.append(f'- {text}')
                i += 1
                while i < len(tokens) and tokens[i][1] == 'sublist':
                    s_attrs = tokens[i][2]
                    s_content = tokens[i][3] or ''
                    s_bullet = s_attrs.get('bullet', 'circle')
                    s_text = inline_to_md(s_content)
                    if s_bullet == 'number':
                        output.append(f'   1. {s_text}')
                    else:
                        output.append(f'   - {s_text}')
                    i += 1
        elif tagname == 'newline':
            output.append('')
            i += 1
        elif tagname in ('pagebreak', 'insertspace'):
            output.append('\n---\n')
            i += 1
        else:
            i += 1

    if title:
        output.insert(0, f'---\ntitle: {title}\n---\n')

    return '\n'.join(output)
