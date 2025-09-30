#!/usr/bin/env python3
"""
Fix CSS code blocks to use grid layout and add line numbers
"""
import re

def fix_css_blocks(filepath):
    """Fix CSS code blocks in markdown file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace <div class="columns"> with <div class="grid grid-cols-2 gap-8">
    content = re.sub(
        r'<div class="columns">',
        '<div class="grid grid-cols-2 gap-8">',
        content
    )

    # Replace <div class="column"> with <div>
    content = re.sub(
        r'<div class="column">',
        '<div>',
        content
    )

    # Add line numbers to CSS code blocks
    def add_line_numbers(match):
        code = match.group(0)
        # Check if already has line numbers
        if '{' in code.split('\n')[0]:
            return code

        # Count lines in the code block
        lines = code.split('\n')
        code_lines = len([l for l in lines[1:-1] if l.strip()])  # Skip ``` lines

        # Add line numbers
        first_line = lines[0]
        return first_line.replace('```css', f'```css {{1-{code_lines}}}')

    # Find all CSS code blocks and add line numbers
    content = re.sub(
        r'```css\n.*?```',
        add_line_numbers,
        content,
        flags=re.DOTALL
    )

    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Fixed CSS blocks in: {filepath}")

if __name__ == '__main__':
    filepath = '/home/cbchoi/Projects/lecture-hmi/src/slides/week01-hci-hmi-theory/slides-05-practice3.md'
    fix_css_blocks(filepath)

    # Copy to slides folder
    import shutil
    dest = '/home/cbchoi/Projects/lecture-hmi/slides/week01-hci-hmi-theory/slides-05-practice3.md'
    shutil.copy(filepath, dest)
    print(f"Copied to: {dest}")
