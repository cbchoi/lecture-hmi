#!/usr/bin/env python3
"""
Aggressively split ALL slides over 40 lines
"""
import re
import sys

def split_at_empty_lines(lines, max_lines=40):
    """Split at empty lines when over max_lines"""
    if len(lines) <= max_lines:
        return ['\n'.join(lines)]

    chunks = []
    current = []

    for i, line in enumerate(lines):
        current.append(line)

        # When we hit max_lines, look for next empty line to split
        if len(current) >= max_lines:
            # Find next empty line within next 5 lines
            for j in range(i+1, min(i+6, len(lines))):
                if lines[j].strip() == '':
                    # Found empty line, split here
                    remaining_in_section = j - i
                    current.extend(lines[i+1:j+1])
                    chunks.append('\n'.join(current))
                    current = []
                    # Skip the lines we just added
                    lines = lines[j+1:]
                    return chunks + split_at_empty_lines(lines, max_lines)

            # No empty line found, just split now
            chunks.append('\n'.join(current))
            return chunks + split_at_empty_lines(lines[i+1:], max_lines)

    if current:
        chunks.append('\n'.join(current))

    return chunks

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    slides = content.split('\n---\n')
    new_slides = []
    mods = []

    for i, slide in enumerate(slides):
        lines = slide.split('\n')

        if len(lines) > 40:
            # Aggressively split
            sub_slides = split_at_empty_lines(lines, max_lines=38)
            new_slides.extend(sub_slides)
            mods.append(f"Slide {i}: Split {len(lines)} lines → {len(sub_slides)} slides")
        else:
            new_slides.append(slide)

    new_content = '\n---\n'.join(new_slides)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

    return mods

if __name__ == '__main__':
    filepath = sys.argv[1]
    mods = process_file(filepath)

    print(f"Processed {filepath}")
    for mod in mods:
        print(f"  - {mod}")
    print(f"Total: {len(mods)} slides split")
