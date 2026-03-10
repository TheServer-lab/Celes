"""
Celes 0.1 — Markdown to Celes converter.
"""

import re
from .core import find_matching_brace


def convert_inline(text):
    text = re.sub(r'\*{3}(.+?)\*{3}', r'<bold+italic>{\1}', text)
    text = re.sub(r'_{3}(.+?)_{3}',   r'<bold+italic>{\1}', text)
    text = re.sub(r'\*{2}(.+?)\*{2}', r'<bold>{\1}', text)
    text = re.sub(r'_{2}(.+?)_{2}',   r'<bold>{\1}', text)
    text = re.sub(r'\*(.+?)\*', r'<italic>{\1}', text)
    text = re.sub(r'_(.+?)_',   r'<italic>{\1}', text)
    text = re.sub(r'~~(.+?)~~', r'<strike>{\1}', text)
    text = re.sub(r'`(.+?)`', r'<code>{\1}', text)
    text = re.sub(
        r'\[!\[.*?\]\((.+?)\)\]\((.+?)\)',
        lambda m: f'<linkimage -image={m.group(1)}>{{{m.group(2)}}}',
        text
    )
    text = re.sub(r'!\[.*?\]\((.+?)\)', r'<image>{\1}', text)
    text = re.sub(r'\[(.+?)\]\((.+?)\)', r'<link -body=\1>{\2}', text)
    text = re.sub(r'<u>(.*?)</u>', r'<underline>{\1}', text)

    def protect_bare_angles(t):
        return re.sub(r'<(?!/?(?:bold|italic|strike|code|underline|link|image|checkmark|newline|empty|nestquote|bold\+italic))', '<empty>{<}', t)

    text = protect_bare_angles(text)
    return text


def convert_md_to_celes(source):
    lines = source.splitlines()
    output = ['<!Celes-0.1>']
    i = 0

    if lines and lines[0].strip() == '---':
        j = 1
        while j < len(lines) and lines[j].strip() != '---':
            m = re.match(r'^title:\s*(.+)', lines[j], re.IGNORECASE)
            if m:
                output.append(f'<title>{{{m.group(1).strip()}}}')
            j += 1
        i = j + 1

    while i < len(lines):
        line = lines[i]

        if line.strip().startswith('```'):
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                code_lines.append(lines[i])
                i += 1
            output.append('<codeblock>{' + '\n'.join(code_lines) + '}')
            i += 1
            continue

        if line.strip().startswith('<!--') and line.strip().endswith('-->'):
            comment = line.strip()[4:-3].strip()
            output.append(f'; {comment}')
            i += 1
            continue

        if re.match(r'^(-{3,}|\*{3,}|_{3,})\s*$', line.strip()):
            output.append('<insertspace>')
            i += 1
            continue

        m = re.match(r'^(#{1,6})\s+(.*)', line)
        if m:
            size = len(m.group(1))
            text = convert_inline(m.group(2).strip())
            output.append(f'<header -size={size}>{{{text}}}')
            i += 1
            continue

        prev = lines[i - 1].strip() if i > 0 else ''
        if i + 1 < len(lines) and prev and not prev.startswith('#') and not prev.startswith('>'):
            if re.match(r'^=+\s*$', lines[i + 1]):
                text = convert_inline(line.strip())
                output.append(f'<header -size=1>{{{text}}}')
                i += 2
                continue
            if re.match(r'^-+\s*$', lines[i + 1]) and not re.match(r'^[-*+]\s', line):
                text = convert_inline(line.strip())
                output.append(f'<header -size=2>{{{text}}}')
                i += 2
                continue

        if line.startswith('>'):
            bq_lines = []
            while i < len(lines) and lines[i].startswith('>'):
                bq_line = lines[i][1:].strip()
                if bq_line.startswith('>'):
                    bq_lines.append('<nestquote>{' + convert_inline(bq_line[1:].strip()) + '}')
                elif bq_line:
                    bq_lines.append(convert_inline(bq_line))
                i += 1
            content = ' <newline>'.join(bq_lines)
            output.append(f'<blockquote>{{{content}}}')
            continue

        if '|' in line and i + 1 < len(lines) and re.match(r'^[\|\s\-:]+$', lines[i + 1]):
            cols = [c.strip() for c in line.strip().strip('|').split('|')]
            output.append('<table>{' + ', '.join(cols) + '}')
            i += 2
            while i < len(lines) and '|' in lines[i]:
                cells = [c.strip() for c in lines[i].strip().strip('|').split('|')]
                output.append('<item>{' + ', '.join(cells) + '}')
                i += 1
            continue

        if re.match(r'^(\s*)[-*+]\s+\[[ xX]\]\s+', line):
            checked_m  = re.match(r'^(\s*)[-*+]\s+\[([xX])\]\s+(.*)', line)
            unchecked_m = re.match(r'^(\s*)[-*+]\s+\[ \]\s+(.*)', line)
            indent = len(re.match(r'^(\s*)', line).group(1))
            tag = 'sublist' if indent > 0 else 'list'
            if checked_m:
                text = convert_inline(checked_m.group(3))
                output.append(f'<{tag} -bullet=circle>{{<checkmark -check>{{{text}}}}}')
            elif unchecked_m:
                text = convert_inline(unchecked_m.group(2))
                output.append(f'<{tag} -bullet=circle>{{<checkmark -uncheck>{{{text}}}}}')
            i += 1
            continue

        if re.match(r'^(\s*)[-*+]\s+', line):
            indent = len(re.match(r'^(\s*)', line).group(1))
            text = re.sub(r'^\s*[-*+]\s+', '', line)
            tag = 'sublist' if indent > 0 else 'list'
            output.append(f'<{tag} -bullet=circle>{{{convert_inline(text)}}}')
            i += 1
            continue

        if re.match(r'^(\s*)\d+\.\s+', line):
            indent = len(re.match(r'^(\s*)', line).group(1))
            text = re.sub(r'^\s*\d+\.\s+', '', line)
            tag = 'sublist' if indent > 0 else 'list'
            output.append(f'<{tag} -bullet=number>{{{convert_inline(text)}}}')
            i += 1
            continue

        m = re.match(r'<div\s+align=["\']?(\w+)["\']?>(.*?)</div>', line.strip())
        if m:
            align = m.group(1)
            text = convert_inline(m.group(2))
            output.append(f'<line -align={align}>{{{text}}}')
            i += 1
            continue

        if not line.strip():
            output.append('<newline>')
            i += 1
            continue

        text = convert_inline(line.strip())
        output.append(f'<line>{{{text}}}')
        i += 1

    return '\n'.join(output)
