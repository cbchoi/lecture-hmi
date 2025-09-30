#!/usr/bin/env python3
"""
Add line numbers to all code blocks (Python, JavaScript, C#, etc.)
"""
import re

def count_code_lines(code_block):
    """Count non-empty code lines"""
    lines = code_block.strip().split('\n')
    return len([l for l in lines if l.strip()])

def add_line_numbers_to_file(filepath):
    """Add line numbers to all code blocks in a markdown file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern to match code blocks without line numbers
    pattern = r'^```(python|javascript|csharp|cpp|java|css)$'

    lines = content.split('\n')
    result = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Check if this is a code block start without line numbers
        match = re.match(pattern, line.strip())
        if match:
            lang = match.group(1)

            # Find the closing ```
            code_lines = []
            i += 1
            while i < len(lines) and lines[i].strip() != '```':
                code_lines.append(lines[i])
                i += 1

            # Count non-empty lines
            line_count = len([l for l in code_lines if l.strip()])

            # Add line numbers to opening tag
            result.append(f'```{lang} {{1-{line_count}}}')
            result.extend(code_lines)
            if i < len(lines):
                result.append(lines[i])  # closing ```
        else:
            result.append(line)

        i += 1

    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(result))

    print(f"Added line numbers to: {filepath}")

if __name__ == '__main__':
    files = [
        '/home/cbchoi/Projects/lecture-hmi/src/slides/week01-hci-hmi-theory/slides-03-practice1.md',
        '/home/cbchoi/Projects/lecture-hmi/src/slides/week01-hci-hmi-theory/slides-04-practice2.md',
        '/home/cbchoi/Projects/lecture-hmi/src/slides/week01-hci-hmi-theory/slides-05-practice3.md',
    ]

    for filepath in files:
        add_line_numbers_to_file(filepath)

        # Copy to slides folder
        import shutil
        dest = filepath.replace('/src/slides/', '/slides/')
        shutil.copy(filepath, dest)
        print(f"Copied to: {dest}")
