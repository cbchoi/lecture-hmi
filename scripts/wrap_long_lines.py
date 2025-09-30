#!/usr/bin/env python3
"""
Wrap long lines in two-column layouts to prevent horizontal scrolling
"""
import re
import sys

def wrap_line(line, max_width=70):
    """Wrap a line if it's too long, respecting markdown formatting"""
    if len(line) <= max_width:
        return line

    # Don't wrap code blocks, headers, or list items with code
    if line.strip().startswith(('```', '#', '|', '    ')):
        return line

    # Don't wrap if it contains inline code with long content
    if '`' in line and len(re.findall(r'`[^`]+`', line)) > 0:
        return line

    # For bullet points, preserve indentation
    indent_match = re.match(r'^(\s*[-*]\s+\*\*[^*]+\*\*:\s*)', line)
    if indent_match:
        prefix = indent_match.group(1)
        rest = line[len(prefix):]

        # Split on sentence boundaries or commas
        if '。' in rest or '. ' in rest or ', ' in rest:
            return line

        words = rest.split()
        lines = []
        current_line = prefix + words[0] if words else prefix

        for word in words[1:]:
            if len(current_line + ' ' + word) <= max_width:
                current_line += ' ' + word
            else:
                lines.append(current_line)
                current_line = '  ' + word  # Indent continuation

        if current_line:
            lines.append(current_line)

        return '\n'.join(lines)

    return line

def process_file(filepath):
    """Process a markdown file to wrap long lines in two-column layouts"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    result = []
    in_two_column = False
    in_code_block = False

    for i, line in enumerate(lines):
        # Track if we're in a two-column layout
        if '<div class="grid grid-cols-2 gap-8">' in line:
            in_two_column = True
            result.append(line)
            continue

        if in_two_column and '</div>' in line and '</div>' in lines[i-1] if i > 0 else False:
            in_two_column = False
            result.append(line)
            continue

        # Track code blocks
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            result.append(line)
            continue

        # Only wrap lines inside two-column layouts, outside code blocks
        if in_two_column and not in_code_block:
            wrapped = wrap_line(line, max_width=70)
            result.append(wrapped)
        else:
            result.append(line)

    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(result))

    print(f"Processed: {filepath}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 wrap_long_lines.py <file1> [file2] ...")
        sys.exit(1)

    for filepath in sys.argv[1:]:
        process_file(filepath)
