#!/usr/bin/env python3
"""
Restore CSS code blocks from original slides.md and add line numbers
"""
import re

# Read original file
with open('/tmp/latest_slides.md', 'r', encoding='utf-8') as f:
    original = f.read()

# Read current file
with open('/home/cbchoi/Projects/lecture-hmi/src/slides/week01-hci-hmi-theory/slides-05-practice3.md', 'r', encoding='utf-8') as f:
    current = f.read()

# Extract CSS code blocks from original
css_blocks = []
in_css = False
current_css = []
for line in original.split('\n'):
    if line.strip() == '```css':
        in_css = True
        current_css = []
    elif in_css and line.strip() == '```':
        in_css = False
        css_blocks.append('\n'.join(current_css))
    elif in_css:
        current_css.append(line)

print(f"Found {len(css_blocks)} CSS code blocks in original")

# Replace empty CSS blocks in current file
result = []
lines = current.split('\n')
i = 0
css_index = 0

while i < len(lines):
    line = lines[i]

    # Check if this is an empty CSS block
    if re.match(r'^```css \{1-\d+\}$', line.strip()):
        # Found empty CSS block with line numbers
        # Skip until we find the closing ```
        result.append(line)
        i += 1

        # Skip content until closing ```
        while i < len(lines) and not (lines[i].strip() == '```' or lines[i].strip() == '---'):
            i += 1

        # Insert CSS code if available
        if css_index < len(css_blocks):
            css_code = css_blocks[css_index]
            # Count actual code lines (non-empty)
            code_lines = [l for l in css_code.split('\n') if l.strip()]
            line_count = len(code_lines)

            # Update the opening with correct line count
            result[-1] = f'```css {{1-{line_count}}}'

            # Insert CSS code
            result.append(css_code)
            result.append('```')
            css_index += 1

            # Skip the old closing tag
            if i < len(lines) and lines[i].strip() in ['```', '---']:
                i += 1
        else:
            result.append(lines[i])
            i += 1
    else:
        result.append(line)
        i += 1

# Write result
output = '\n'.join(result)
with open('/home/cbchoi/Projects/lecture-hmi/src/slides/week01-hci-hmi-theory/slides-05-practice3.md', 'w', encoding='utf-8') as f:
    f.write(output)

print("Restored CSS blocks with line numbers")

# Copy to slides folder
import shutil
dest = '/home/cbchoi/Projects/lecture-hmi/slides/week01-hci-hmi-theory/slides-05-practice3.md'
shutil.copy(
    '/home/cbchoi/Projects/lecture-hmi/src/slides/week01-hci-hmi-theory/slides-05-practice3.md',
    dest
)
print(f"Copied to: {dest}")
