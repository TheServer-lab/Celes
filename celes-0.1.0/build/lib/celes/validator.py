"""
Celes Validator
Validates a Celes source file and reports errors with line numbers.
Supports Celes 0.1.5.
"""

import re
from .core import (
    tokenize, parse_attributes, find_matching_brace,
    SELF_CLOSING_TAGS, BLOCK_TAGS, INLINE_TAGS,
    REQUIRED_ATTRS, VALID_ATTR_VALUES, CSS_COLOR_PATTERN,
)


class CelesError:
    """Represents a single validation error or warning."""

    def __init__(self, level, line, message):
        self.level = level    # 'error' or 'warning'
        self.line = line
        self.message = message

    def __str__(self):
        icon = '✗' if self.level == 'error' else '⚠'
        return f'  {icon} Line {self.line}: {self.message}'

    def __repr__(self):
        return f'CelesError({self.level!r}, line={self.line}, {self.message!r})'


# ─────────────────────────────────────────────
# INLINE VALIDATOR
# ─────────────────────────────────────────────

def validate_inline(content, lineno, errors, parent_tag=None):
    """Recursively validate inline tags within a content string."""
    if content is None:
        return

    i = 0
    while i < len(content):
        tag_start = content.find('<', i)
        if tag_start == -1:
            break

        tag_end = content.find('>', tag_start)
        if tag_end == -1:
            errors.append(CelesError('error', lineno,
                f'Unclosed inline tag starting at position {tag_start} in content: {content[tag_start:tag_start+20]!r}'))
            break

        tag_header = content[tag_start + 1:tag_end]
        header_match = re.match(r'^([\w+]+)(.*)', tag_header, re.DOTALL)
        if not header_match:
            i = tag_end + 1
            continue

        tagname = header_match.group(1).lower()
        attrs = parse_attributes(header_match.group(2))
        after_tag = tag_end + 1

        # Block tags used inline
        if tagname in ('video', 'audio'):
            errors.append(CelesError('error', lineno,
                f'<{tagname}> is a block-level tag and cannot be used inline'))
            i = after_tag
            continue

        # Must be a known inline tag
        if tagname not in INLINE_TAGS and tagname not in SELF_CLOSING_TAGS:
            errors.append(CelesError('error', lineno,
                f'Unknown inline tag <{tagname}>'))

        # Self-closing inline tags should have no content
        if tagname in SELF_CLOSING_TAGS:
            i = after_tag
            continue

        # Must have {content}
        if after_tag >= len(content) or content[after_tag] != '{':
            errors.append(CelesError('error', lineno,
                f'Inline tag <{tagname}> is missing {{...}} content'))
            i = after_tag
            continue

        close = find_matching_brace(content, after_tag)
        if close == -1:
            errors.append(CelesError('error', lineno,
                f'Unclosed brace in inline tag <{tagname}>'))
            break

        inner = content[after_tag + 1:close]

        # 0.1.5 — coloredtext: -color required, value must look like a color
        if tagname == 'coloredtext':
            color = attrs.get('color')
            if not color:
                errors.append(CelesError('error', lineno,
                    '<coloredtext> requires a -color attribute (e.g. -color=red or -color=#ff6600)'))
            elif not CSS_COLOR_PATTERN.match(str(color)):
                errors.append(CelesError('error', lineno,
                    f'<coloredtext -color={color}> — invalid color value. '
                    'Use a named color (e.g. red, royalblue) or hex code (e.g. #D4622A)'))

        # Validate checkmark attributes
        if tagname == 'checkmark':
            if 'check' not in attrs and 'uncheck' not in attrs:
                errors.append(CelesError('error', lineno,
                    '<checkmark> requires either -check or -uncheck attribute'))

        # Validate link attributes
        if tagname == 'link' and 'body' not in attrs:
            errors.append(CelesError('warning', lineno,
                '<link> is missing -body attribute (display text)'))

        # <empty> content is raw — don't recurse
        if tagname != 'empty':
            validate_inline(inner, lineno, errors, parent_tag=tagname)

        i = close + 1


# ─────────────────────────────────────────────
# BLOCK VALIDATOR
# ─────────────────────────────────────────────

def validate_celes(source):
    """
    Validate a Celes 0.1.5 source string.

    Returns a tuple: (is_valid: bool, errors: list[CelesError])

    Example:
        valid, errors = validate_celes(source)
        for e in errors:
            print(e)
    """
    errors = []
    tokens = tokenize(source)

    # ── Check for version declaration ──
    has_declaration = any(t[1] == 'declaration' for t in tokens)
    if not has_declaration:
        errors.append(CelesError('warning', 1,
            'Missing version declaration <!Celes-0.1.5> at top of file'))

    title_count = 0
    background_count = 0
    seen_tags = []
    table_open = False
    i = 0

    while i < len(tokens):
        lineno, tagname, attrs, content = tokens[i]
        seen_tags.append(tagname)

        # ── Skip meta ──
        if tagname in ('comment', 'declaration'):
            i += 1
            continue

        # ── Unknown tag ──
        all_known = BLOCK_TAGS | INLINE_TAGS | {'comment', 'declaration', 'error'}
        if tagname not in all_known:
            errors.append(CelesError('error', lineno,
                f'Unknown tag <{tagname}>'))
            i += 1
            continue

        # ── Parse errors ──
        if tagname == 'error':
            errors.append(CelesError('error', lineno,
                f'Syntax error: {content}'))
            i += 1
            continue

        # ── Self-closing tags must have no content ──
        if tagname in SELF_CLOSING_TAGS and content is not None:
            errors.append(CelesError('warning', lineno,
                f'Self-closing tag <{tagname}> should not have {{...}} content'))

        # ── Content tags must have content ──
        if tagname not in SELF_CLOSING_TAGS and tagname not in ('image', 'linkimage', 'background') and content is None:
            errors.append(CelesError('error', lineno,
                f'<{tagname}> requires {{...}} content but none was found'))

        # ── title ──
        if tagname == 'title':
            title_count += 1
            if title_count > 1:
                errors.append(CelesError('warning', lineno,
                    'Multiple <title> tags found — only the first will be used'))

        # ── 0.1.5 background ──
        if tagname == 'background':
            background_count += 1
            if background_count > 1:
                errors.append(CelesError('warning', lineno,
                    'Duplicate <background> tag — first value will be used'))
            color = (content or '').strip()
            if color and not CSS_COLOR_PATTERN.match(color):
                errors.append(CelesError('error', lineno,
                    f'<background> — invalid color value {color!r}. '
                    'Use a named color or hex code (e.g. #1a1a2e or cornsilk)'))

        # ── 0.1.5 video ──
        if tagname == 'video':
            if not content:
                errors.append(CelesError('warning', lineno,
                    '<video> has no source path or URL in {content}'))
            if 'autoplay' in attrs and 'mute' not in attrs:
                errors.append(CelesError('warning', lineno,
                    '<video -autoplay> without -mute may be silently suppressed by browsers'))

        # ── 0.1.5 audio ──
        if tagname == 'audio':
            if not content:
                errors.append(CelesError('warning', lineno,
                    '<audio> has no source path or URL in {content}'))

        # ── header ──
        if tagname == 'header':
            size = attrs.get('size')
            if size is None:
                errors.append(CelesError('error', lineno,
                    '<header> is missing required -size attribute'))
            elif str(size) not in VALID_ATTR_VALUES['size']:
                errors.append(CelesError('error', lineno,
                    f'<header -size={size}> is invalid — size must be 1–6'))

        # ── line ──
        if tagname == 'line':
            align = attrs.get('align')
            if align and align not in VALID_ATTR_VALUES['align']:
                errors.append(CelesError('error', lineno,
                    f'<line -align={align}> is invalid — align must be left, center, or right'))
            validate_inline(content, lineno, errors, parent_tag='line')

        # ── blockquote ──
        if tagname == 'blockquote':
            validate_inline(content, lineno, errors, parent_tag='blockquote')

        # ── list / sublist / subsublist ──
        if tagname in ('list', 'sublist', 'subsublist'):
            bullet = attrs.get('bullet')
            if bullet is None:
                errors.append(CelesError('error', lineno,
                    f'<{tagname}> is missing required -bullet attribute'))
            elif bullet not in VALID_ATTR_VALUES['bullet']:
                errors.append(CelesError('error', lineno,
                    f'<{tagname} -bullet={bullet}> is invalid — bullet must be circle or number'))
            if content:
                validate_inline(content, lineno, errors, parent_tag=tagname)

        if tagname == 'sublist':
            if len(seen_tags) < 2 or seen_tags[-2] not in ('list', 'sublist', 'subsublist'):
                errors.append(CelesError('warning', lineno,
                    '<sublist> should immediately follow a <list> or another <sublist>'))

        if tagname == 'subsublist':
            if len(seen_tags) < 2 or seen_tags[-2] not in ('sublist', 'subsublist'):
                errors.append(CelesError('warning', lineno,
                    '<subsublist> should immediately follow a <sublist> or another <subsublist>'))

        # ── table ──
        if tagname == 'table':
            if table_open:
                errors.append(CelesError('warning', lineno,
                    'New <table> opened before previous table was closed'))
            table_open = True
            cols = [c.strip() for c in (content or '').split(',')]
            if len(cols) == 0 or (len(cols) == 1 and not cols[0]):
                errors.append(CelesError('error', lineno,
                    '<table> must define at least one column'))
            j = i + 1
            while j < len(tokens) and tokens[j][1] == 'item':
                item_cells = [c.strip() for c in (tokens[j][3] or '').split(',')]
                if len(item_cells) != len(cols):
                    errors.append(CelesError('error', tokens[j][0],
                        f'<item> has {len(item_cells)} cell(s) but table has {len(cols)} column(s)'))
                j += 1
            table_open = False

        # ── item outside table ──
        if tagname == 'item':
            prev_block = next(
                (t for t in reversed(seen_tags[:-1]) if t not in ('comment', 'declaration')),
                None
            )
            if prev_block not in ('table', 'item'):
                errors.append(CelesError('error', lineno,
                    '<item> used outside of a <table>'))

        # ── linkimage ──
        if tagname == 'linkimage':
            if 'image' not in attrs:
                errors.append(CelesError('error', lineno,
                    '<linkimage> is missing required -image attribute'))
            if not content:
                errors.append(CelesError('warning', lineno,
                    '<linkimage> has no URL in {content}'))

        # ── image ──
        if tagname == 'image':
            if not content:
                errors.append(CelesError('warning', lineno,
                    '<image> has no path or URL in {content}'))

        # ── codeblock ──
        if tagname == 'codeblock':
            if content is None:
                errors.append(CelesError('warning', lineno,
                    '<codeblock> is empty'))

        i += 1

    is_valid = not any(e.level == 'error' for e in errors)
    return is_valid, errors


# ─────────────────────────────────────────────
# CLI ENTRY POINT
# ─────────────────────────────────────────────

def main_validate(source, filename='<input>'):
    """Run validation and print a formatted report. Returns exit code."""
    is_valid, errors = validate_celes(source)

    error_count   = sum(1 for e in errors if e.level == 'error')
    warning_count = sum(1 for e in errors if e.level == 'warning')

    if not errors:
        print(f'✓ {filename}: Valid Celes 0.1.5 document')
        return 0

    print(f'Validation report for {filename}:')
    for e in errors:
        print(e)

    print()
    parts = []
    if error_count:
        parts.append(f'{error_count} error(s)')
    if warning_count:
        parts.append(f'{warning_count} warning(s)')
    status = '✗ Invalid' if not is_valid else '⚠ Valid with warnings'
    print(f'{status} — {", ".join(parts)}')

    return 0 if is_valid else 1
