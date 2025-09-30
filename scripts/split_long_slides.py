#!/usr/bin/env python3
"""
Split slides that exceed 40 lines into multiple slides.
Preserves 2-column layouts and code blocks.
"""

import re
import sys

def count_lines(text):
    """Count non-empty lines in text"""
    return len([line for line in text.split('\n') if line.strip()])

def split_slide_content(content, max_lines=40):
    """Split slide content into chunks of max_lines"""
    lines = content.split('\n')

    # If already under limit, return as-is
    if len(lines) <= max_lines:
        return [content]

    chunks = []
    current_chunk = []
    in_code_block = False
    in_columns = False
    code_fence_count = 0

    for i, line in enumerate(lines):
        # Track code blocks
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            code_fence_count += 1

        # Track column divs
        if '<div class="column' in line or '<div class="grid' in line:
            in_columns = True
        if in_columns and '</div>' in line:
            # Check if this closes the columns
            remaining = '\n'.join(lines[i+1:])
            if '</div>' not in remaining[:100]:  # Heuristic
                in_columns = False

        current_chunk.append(line)

        # Split point: when we hit max_lines and not in code/columns
        if len(current_chunk) >= max_lines and not in_code_block and not in_columns:
            # Try to find a good break point (empty line or header)
            for j in range(len(current_chunk) - 1, max(0, len(current_chunk) - 10), -1):
                if current_chunk[j].strip() == '' or current_chunk[j].startswith('#'):
                    chunks.append('\n'.join(current_chunk[:j+1]))
                    current_chunk = current_chunk[j+1:]
                    break
            else:
                # No good break point found, just split
                chunks.append('\n'.join(current_chunk))
                current_chunk = []

    # Add remaining content
    if current_chunk:
        chunks.append('\n'.join(current_chunk))

    return chunks

def process_file(filepath):
    """Process a markdown file and split long slides"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by slide separator
    slides = content.split('\n---\n')

    new_slides = []
    modifications = []

    for i, slide in enumerate(slides):
        line_count = count_lines(slide)

        if line_count > 40:
            # Split this slide
            sub_slides = split_slide_content(slide, max_lines=35)
            new_slides.extend(sub_slides)
            modifications.append(f"Slide {i+1}: Split from {line_count} lines into {len(sub_slides)} slides")
        else:
            new_slides.append(slide)

    # Rejoin with separators
    new_content = '\n---\n'.join(new_slides)

    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

    return modifications

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python split_long_slides.py <markdown_file>")
        sys.exit(1)

    filepath = sys.argv[1]
    mods = process_file(filepath)

    print(f"Processed {filepath}")
    for mod in mods:
        print(f"  - {mod}")
    print(f"Total modifications: {len(mods)}")
