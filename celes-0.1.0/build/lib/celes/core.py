"""
Celes core utilities — shared across parser, validator, and converters.
"""

import re


SELF_CLOSING_TAGS = {'newline', 'pagebreak', 'insertspace'}

BLOCK_TAGS = {
    'title', 'header', 'line', 'blockquote', 'codeblock',
    'image', 'linkimage', 'list', 'sublist', 'table', 'item',
    'newline', 'pagebreak', 'insertspace',
}

INLINE_TAGS = {
    'bold', 'italic', 'bold+italic', 'underline', 'strike',
    'code', 'link', 'checkmark', 'nestquote', 'empty',
}

REQUIRED_ATTRS = {
    'header':    ['size'],
    'link':      ['body'],
    'linkimage': ['image'],
    'checkmark': [],   # needs either -check or -uncheck key
}

VALID_ATTR_VALUES = {
    'size':   {'1', '2', '3', '4', '5', '6'},
    'bullet': {'circle', 'number'},
    'align':  {'left', 'center', 'right'},
}


def find_matching_brace(s, start):
    """Return index of closing } matching { at s[start]. Returns -1 if not found."""
    depth = 0
    for i in range(start, len(s)):
        if s[i] == '{':
            depth += 1
        elif s[i] == '}':
            depth -= 1
            if depth == 0:
                return i
    return -1


def parse_attributes(attr_str):
    """Parse '-key=value -flag' strings into a dict."""
    attrs = {}
    attr_str = attr_str.strip()
    pattern = re.compile(r'-(\w+)(?:=(?=\S)(.*?))?(?=\s+-\w|$)', re.DOTALL)
    for m in pattern.finditer(attr_str):
        key = m.group(1)
        val = m.group(2)
        attrs[key] = val.strip() if val is not None else True
    return attrs


def split_multi_tag_line(line):
    """
    Split a line containing multiple adjacent tags into individual tag strings.
    e.g. '<list>{Item}<sublist>{Sub}' → ['<list>{Item}', '<sublist>{Sub}']
    """
    line = line.strip()
    if line.startswith(';') or line.startswith('<!'):
        return [line]
    result = []
    i = 0
    while i < len(line):
        if line[i] != '<':
            break
        tag_end = line.find('>', i)
        if tag_end == -1:
            result.append(line[i:])
            break
        after_tag = tag_end + 1
        if after_tag < len(line) and line[after_tag] == '{':
            close = find_matching_brace(line, after_tag)
            if close != -1:
                result.append(line[i:close + 1])
                i = close + 1
                continue
        result.append(line[i:after_tag])
        i = after_tag
    return result if result else [line]


def parse_tag_line(line):
    """
    Parse a single tag string into (tagname, attrs, content).
    Returns ('comment', {}, text) for comments.
    Returns ('error', {}, message) for parse failures.
    Self-closing tags return content=None.
    """
    line = line.strip()
    if not line:
        return None
    if line.startswith(';'):
        return ('comment', {}, line[1:].strip())
    if line.startswith('<!Celes'):
        return ('declaration', {}, line)
    if not line.startswith('<'):
        return ('error', {}, f'Line does not start with a tag: {line!r}')
    tag_end = line.find('>')
    if tag_end == -1:
        return ('error', {}, f'Unclosed tag header: {line!r}')
    tag_header = line[1:tag_end]
    header_match = re.match(r'^([\w+]+)(.*)', tag_header, re.DOTALL)
    if not header_match:
        return ('error', {}, f'Cannot parse tag name from: {line!r}')
    tagname = header_match.group(1).lower()
    attrs = parse_attributes(header_match.group(2))
    rest = line[tag_end + 1:].strip()
    if not rest:
        return (tagname, attrs, None)
    if not rest.startswith('{'):
        return ('error', {}, f'Missing {{...}} content after tag in: {line!r}')
    close = find_matching_brace(rest, 0)
    if close == -1:
        return ('error', {}, f'Unclosed brace in: {line!r}')
    content = rest[1:close]
    return (tagname, attrs, content)


def tokenize(source):
    """
    Convert a Celes source string into a list of (line_number, tagname, attrs, content) tuples.
    """
    tokens = []
    for lineno, raw_line in enumerate(source.splitlines(), start=1):
        if not raw_line.strip():
            continue
        for single in split_multi_tag_line(raw_line):
            if not single.strip():
                continue
            result = parse_tag_line(single)
            if result:
                tokens.append((lineno, *result))
    return tokens
