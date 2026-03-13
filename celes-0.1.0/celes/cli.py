"""
Celes CLI — command line interface for the Celes 0.1 toolkit.

Commands:
    celes parse    input.celes [output.html]   — convert to HTML
    celes validate input.celes                 — validate a file
    celes md       input.md    [output.celes]  — convert Markdown to Celes
    celes tomd     input.celes [output.md]     — convert Celes to Markdown
"""

import sys
import os


def read_file(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f'Error: File not found: {path}', file=sys.stderr)
        sys.exit(1)


def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'✓ Output written to {path}')


def cmd_parse(args):
    if not args:
        print('Usage: celes parse <input.celes> [output.html]')
        sys.exit(1)
    from .parser import parse_celes
    source = read_file(args[0])
    result = parse_celes(source)
    if len(args) >= 2:
        write_file(args[1], result)
    else:
        print(result)


def cmd_validate(args):
    if not args:
        print('Usage: celes validate <input.celes>')
        sys.exit(1)
    from .validator import main_validate
    source = read_file(args[0])
    code = main_validate(source, filename=args[0])
    sys.exit(code)


def cmd_md(args):
    if not args:
        print('Usage: celes md <input.md> [output.celes]')
        sys.exit(1)
    from .md_to_celes import convert_md_to_celes
    source = read_file(args[0])
    result = convert_md_to_celes(source)
    if len(args) >= 2:
        write_file(args[1], result)
    else:
        print(result)


def cmd_tomd(args):
    if not args:
        print('Usage: celes tomd <input.celes> [output.md]')
        sys.exit(1)
    from .celes_to_md import convert_celes_to_md
    source = read_file(args[0])
    result = convert_celes_to_md(source)
    if len(args) >= 2:
        write_file(args[1], result)
    else:
        print(result)


COMMANDS = {
    'parse':    cmd_parse,
    'validate': cmd_validate,
    'md':       cmd_md,
    'tomd':     cmd_tomd,
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ('-h', '--help'):
        print("""Celes 0.1 Toolkit

Usage:
  celes parse    <input.celes> [output.html]   Convert Celes → HTML
  celes validate <input.celes>                 Validate a Celes file
  celes md       <input.md>    [output.celes]  Convert Markdown → Celes
  celes tomd     <input.celes> [output.md]     Convert Celes → Markdown

Examples:
  celes parse    doc.celes doc.html
  celes validate doc.celes
  celes md       README.md  README.celes
  celes tomd     doc.celes  doc.md
""")
        sys.exit(0)

    command = sys.argv[1]
    if command not in COMMANDS:
        print(f'Unknown command: {command!r}')
        print(f'Available commands: {", ".join(COMMANDS)}')
        sys.exit(1)

    COMMANDS[command](sys.argv[2:])


if __name__ == '__main__':
    main()
