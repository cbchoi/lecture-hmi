#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import sys
import os
from pathlib import Path

def remove_time_allocations(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # Remove time allocation patterns
    patterns = [
        # Remove (X분) patterns
        r'\s*\(\d+분\)',
        # Remove section headers with time allocation like '## ⏰ 세션 구성'
        r'## ⏰ 세션 구성.*?(?=\n## |\n---|\Z)',
        # Remove time allocation section headers
        r'## ⏰.*?(?=\n## |\n---|\Z)',
        # Remove specific session time patterns like ': (45분)'
        r':\s*\(\d+분\)',
        # Remove time allocation in bullet points that contain 분
        r'- \*\*.*?\*\*:\s*\d+분.*?\n',
        # Remove standalone time references at end of lines
        r'\s+\(\d+분\)(?=\s*$)',
        # Remove specific time allocation headers with numbers
        r'### \d+\.\d+.*?\(\d+분\).*?\n',
        # Remove session time allocations in headers
        r'## \d+.*?\(\d+분\)',
    ]

    for pattern in patterns:
        content = re.sub(pattern, '', content, flags=re.MULTILINE | re.DOTALL)

    # Clean up multiple consecutive newlines
    content = re.sub(r'\n{3,}', '\n\n', content)

    # Clean up trailing whitespace
    content = re.sub(r'[ \t]+$', '', content, flags=re.MULTILINE)

    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'Updated: {file_path}')
        return True
    else:
        print(f'No changes: {file_path}')
        return False

def main():
    slides_dir = Path('./src/slides')
    updated_count = 0

    for slides_file in slides_dir.glob('*/slides.md'):
        if remove_time_allocations(slides_file):
            updated_count += 1

    print(f'\nTotal files updated: {updated_count}')

if __name__ == '__main__':
    main()