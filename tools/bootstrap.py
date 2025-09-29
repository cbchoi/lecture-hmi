#!/usr/bin/env python3
"""
Bootstrap script for System Programming Lecture Slides
Dynamically generates index.html based on available weeks in slides/ directory
"""

import os
import re
import json
from pathlib import Path
from typing import List, Dict, Any

def scan_weeks_directory(slides_path: Path) -> List[Dict[str, Any]]:
    """
    Scan slides directory for weekXX folders and extract week information

    Args:
        slides_path: Path to slides directory

    Returns:
        List of week dictionaries with metadata
    """
    weeks = []

    if not slides_path.exists():
        print(f"Warning: slides directory not found at {slides_path}")
        return weeks

    # Pattern to match weekXX or weekXX-description directories
    week_pattern = re.compile(r'^week(\d{2})(?:-.*)?$')

    for item in slides_path.iterdir():
        if item.is_dir():
            match = week_pattern.match(item.name)
            if match:
                week_num = match.group(1)
                week_info = extract_week_info(item, week_num)
                if week_info:
                    weeks.append(week_info)

    # Sort weeks by number
    weeks.sort(key=lambda x: x['number'])
    return weeks

def extract_week_info(week_path: Path, week_num: str) -> Dict[str, Any]:
    """
    Extract week information from week directory

    Args:
        week_path: Path to weekXX directory
        week_num: Week number string (e.g., "03")

    Returns:
        Dictionary with week metadata
    """
    week_info = {
        'number': week_num,
        'title': f'Week {week_num}',
        'description': 'No description available',
        'has_slides': False,
        'has_code': False,
        'has_images': False
    }

    # Check for slides.md
    slides_file = week_path / 'slides.md'
    if slides_file.exists():
        week_info['has_slides'] = True
        # Try to extract title from slides.md
        title = extract_title_from_slides(slides_file)
        if title:
            week_info['title'] = title

    # Check for summary.md
    summary_file = week_path / 'summary.md'
    if summary_file.exists():
        summary_info = extract_summary_info(summary_file)
        week_info.update(summary_info)

    # Check for code directory
    code_dir = week_path / 'code'
    if code_dir.exists() and any(code_dir.iterdir()):
        week_info['has_code'] = True

    # Check for images directory
    images_dir = week_path / 'images'
    if images_dir.exists() and any(images_dir.iterdir()):
        week_info['has_images'] = True

    return week_info

def extract_title_from_slides(slides_file: Path) -> str:
    """Extract title from slides.md file"""
    try:
        with open(slides_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('# '):
                    return line[2:].strip()
                # Stop after first few lines to avoid performance issues
                if len(line) > 0 and not line.startswith('#'):
                    break
    except Exception as e:
        print(f"Warning: Could not read {slides_file}: {e}")
    return ""

def extract_summary_info(summary_file: Path) -> Dict[str, Any]:
    """Extract information from summary.md file"""
    info = {}

    try:
        with open(summary_file, 'r', encoding='utf-8') as f:
            content = f.read()

            # Extract title (first h1)
            title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
            if title_match:
                info['title'] = title_match.group(1).strip()

            # Extract learning objectives (첫 번째 ## 🎯 학습 목표 섹션)
            objective_match = re.search(
                r'## 🎯 학습 목표\s*\n(.+?)(?=\n##|\n$)',
                content,
                re.DOTALL
            )
            if objective_match:
                info['description'] = objective_match.group(1).strip()

    except Exception as e:
        print(f"Warning: Could not read {summary_file}: {e}")

    return info

def generate_index_html(weeks: List[Dict[str, Any]]) -> str:
    """
    Generate complete index.html content

    Args:
        weeks: List of week dictionaries

    Returns:
        Complete HTML content as string
    """

    # Generate lecture cards HTML
    lecture_cards = []
    for week in weeks:
        week_num = week['number']
        title = week['title']
        description = week['description']

        # Generate status indicators
        indicators = []
        if week['has_slides']:
            indicators.append('<span class="status-indicator slides">📄 Slides</span>')
        if week['has_code']:
            indicators.append('<span class="status-indicator code">💻 Code</span>')
        if week['has_images']:
            indicators.append('<span class="status-indicator images">🖼️ Images</span>')

        indicators_html = ''.join(indicators) if indicators else '<span class="status-indicator none">📋 준비중</span>'

        card_html = f'''
            <div class="lecture-card">
                <div class="week-number">Week {week_num}</div>
                <h3>{title}</h3>
                <div class="description">
                    {description}
                </div>
                <div class="status-indicators">
                    {indicators_html}
                </div>
                <div class="actions">
                    <a href="?week={week_num}" class="view-link">강의 보기</a>
                    <button onclick="generatePDF('{week_num}')" class="pdf-button">PDF 생성</button>
                </div>
            </div>'''

        lecture_cards.append(card_html)

    cards_html = '\n'.join(lecture_cards)

    # Complete HTML template
    html_content = f'''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HCI/HMI Lecture</title>

    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.0.4/dist/reveal.css">
    <link rel="stylesheet" id="theme-link" href="https://cdn.jsdelivr.net/npm/reveal.js@5.0.4/dist/theme/white.css">
    <link rel="stylesheet" href="/themes/custom.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.0.4/plugin/highlight/monokai.css">
    <link rel="stylesheet" href="/css/main.css">
</head>

<body class="theme-custom">
    <!-- Main Page -->
    <div id="main-page" class="main-page">
        <div class="header">
            <h1>HCI/HMI 강의</h1>
            <p>Human Computer Interaction / Human Machine Interface Lecture Slides</p>
            <div class="stats">
                <span class="stat-item">📚 총 {len(weeks)}주차</span>
                <span class="stat-item">💻 {sum(1 for w in weeks if w.get("has_code"))}개 코드 예제</span>
                <span class="stat-item">📄 {sum(1 for w in weeks if w.get("has_slides"))}개 슬라이드</span>
            </div>
        </div>

        <div class="lectures-grid">
            {cards_html}
        </div>

        <div class="footer">
            <p>© 2024 HCI/HMI Course | Built with reveal.js & Vite</p>
            <p>🤖 Generated automatically by bootstrap.py</p>
        </div>
    </div>

    <!-- Presentation View -->
    <div id="presentation-view" class="reveal hidden">
        <div class="slides">
            <section data-markdown data-separator="^\n---\n$" data-separator-vertical="^\n--\n$">
                <textarea data-template id="slide-content">
                    # Loading...
                    Please wait while the content loads.
                </textarea>
            </section>
        </div>
    </div>

    <script type="module">
        // Get URL parameters
        const urlParams = new URLSearchParams(window.location.search);
        const weekParam = urlParams.get('week') || urlParams.get('w');
        const themeParam = urlParams.get('theme');

        // DOM elements
        const mainPage = document.getElementById('main-page');
        const presentationView = document.getElementById('presentation-view');
        const themeLink = document.getElementById('theme-link');

        // Always use custom theme
        const currentTheme = 'custom';

        // PDF generation function
        async function generatePDF(week) {{
            const isWindows = navigator.platform.toLowerCase().includes('win');
            const command = isWindows ? `exec_script\\\\export-pdf.bat ${{week}}` : `./exec_script/export-pdf.sh ${{week}}`;
            const platform = isWindows ? 'Windows' : 'Linux/Mac';

            // Show command in modal dialog
            const message = `Week ${{week}}의 PDF를 생성하려면 터미널에서 다음 명령어를 실행하세요:\\n\\n${{platform}}: ${{command}}\\n\\n생성된 PDF는 pdf-exports 폴더에 저장됩니다.\\n\\n※ 먼저 개발 서버가 실행 중인지 확인해주세요.`;

            if (confirm(message + '\\n\\n명령어를 클립보드에 복사하시겠습니까?')) {{
                try {{
                    await navigator.clipboard.writeText(command);
                    alert('명령어가 클립보드에 복사되었습니다!\\n터미널에서 붙여넣기(Ctrl+V)하여 실행하세요.');
                }} catch (err) {{
                    // Fallback for browsers that don't support clipboard API
                    const textArea = document.createElement('textarea');
                    textArea.value = command;
                    document.body.appendChild(textArea);
                    textArea.select();
                    try {{
                        document.execCommand('copy');
                        alert('명령어가 클립보드에 복사되었습니다!\\n터미널에서 붙여넣기(Ctrl+V)하여 실행하세요.');
                    }} catch (err2) {{
                        alert('클립보드 복사에 실패했습니다. 수동으로 복사해주세요:\\n' + command);
                    }}
                    document.body.removeChild(textArea);
                }}
            }}
        }}

        // Make generatePDF globally available
        window.generatePDF = generatePDF;

        function updateTheme(theme) {{
            if (theme === 'custom') {{
                // Load white theme first, then add custom enhancements
                if (themeLink) {{
                    themeLink.href = `https://cdn.jsdelivr.net/npm/reveal.js@5.0.4/dist/theme/white.css`;
                }}
                loadCustomThemeCSS();
                document.body.className = document.body.className.replace(/theme-\\w+/g, '');
                document.body.classList.add('theme-custom');
            }} else {{
                // Remove custom theme CSS if it exists
                removeCustomThemeCSS();
                if (themeLink) {{
                    themeLink.href = `https://cdn.jsdelivr.net/npm/reveal.js@5.0.4/dist/theme/${{theme}}.css`;
                }}
                document.body.className = document.body.className.replace(/theme-\\w+/g, '');
                document.body.classList.add(`theme-${{theme}}`);
            }}
        }}

        function loadCustomThemeCSS() {{
            // Check if custom theme CSS is already loaded
            if (document.getElementById('custom-theme-css')) {{
                return;
            }}

            const link = document.createElement('link');
            link.id = 'custom-theme-css';
            link.rel = 'stylesheet';
            link.href = '/themes/custom.css';
            document.head.appendChild(link);
        }}

        function removeCustomThemeCSS() {{
            const existingLink = document.getElementById('custom-theme-css');
            if (existingLink) {{
                existingLink.remove();
            }}
        }}

        // Check if we should show presentation or main page
        if (weekParam) {{
            showPresentation();
        }} else {{
            showMainPage();
        }}

        function showMainPage() {{
            mainPage.classList.remove('hidden');
            presentationView.classList.add('hidden');
            document.title = 'HCI/HMI Lecture';
            updateTheme(currentTheme);
        }}

        async function showPresentation() {{
            try {{
                // Import reveal.js modules
                const Reveal = (await import('https://cdn.jsdelivr.net/npm/reveal.js@5.0.4/dist/reveal.esm.js')).default;
                const Markdown = (await import('https://cdn.jsdelivr.net/npm/reveal.js@5.0.4/plugin/markdown/markdown.esm.js')).default;
                const Highlight = (await import('https://cdn.jsdelivr.net/npm/reveal.js@5.0.4/plugin/highlight/highlight.esm.js')).default;
                const Notes = (await import('https://cdn.jsdelivr.net/npm/reveal.js@5.0.4/plugin/notes/notes.esm.js')).default;
                const Search = (await import('https://cdn.jsdelivr.net/npm/reveal.js@5.0.4/plugin/search/search.esm.js')).default;
                const Zoom = (await import('https://cdn.jsdelivr.net/npm/reveal.js@5.0.4/plugin/zoom/zoom.esm.js')).default;

                mainPage.classList.add('hidden');
                presentationView.classList.remove('hidden');

                // Load content
                const content = await loadWeekContent(weekParam);
                document.getElementById('slide-content').textContent = content;

                // Initialize reveal.js
                const deck = new Reveal({{
                    hash: true,
                    controls: true,
                    progress: true,
                    center: false,
                    transition: 'slide',
                    backgroundTransition: 'fade',
                    width: 1400,
                    height: 900,
                    margin: 0.02,
                    minScale: 0.1,
                    maxScale: 2.5,
                    markdown: {{
                        smartypants: true,
                        breaks: true
                    }},
                    highlight: {{
                        highlightOnLoad: true
                    }},
                    plugins: [Markdown, Highlight, Notes, Search, Zoom]
                }});

                await deck.initialize();

                // Apply theme
                updateTheme(currentTheme);

                // Apply custom styling
                setTimeout(() => {{
                    applyCustomStyling();
                }}, 100);

                // Update page title
                document.title = `Week ${{weekParam}} - HCI/HMI Lecture`;

                // Add back button
                addBackButton();

                // Add drawing functionality
                addDrawingFeature(deck);
            }} catch (error) {{
                console.error('Error loading presentation:', error);
                showMainPage();
            }}
        }}

        async function loadWeekContent(week) {{
            if (!week) {{
                return `# HCI/HMI Lecture

Welcome to HCI/HMI Lecture slides.

---

## Available Weeks

{" ".join([f"- Week {w['number']}: {w['title']}" for w in weeks])}

Please go back to select a week.`;
            }}

            try {{
                // Try both formats: weekXX and weekXX-description
                let response = await fetch(`/slides/week${{week.padStart(2, '0')}}/slides.md`);
                if (!response.ok) {{
                    // Try with description format by scanning slides directory
                    const slidesResponse = await fetch('/slides/');
                    if (slidesResponse.ok) {{
                        const slidesContent = await slidesResponse.text();
                        const weekPattern = new RegExp(`week${{week.padStart(2, '0')}}-[^"]*`, 'g');
                        const match = slidesContent.match(weekPattern);
                        if (match && match[0]) {{
                            response = await fetch(`/slides/${{match[0]}}/slides.md`);
                        }}
                    }}
                }}
                if (!response.ok) {{
                    throw new Error(`Week ${{week}} not found`);
                }}
                return await response.text();
            }} catch (error) {{
                return `# Week ${{week}} - Not Available

This week's content is not yet available.

---

## Error Details

${{error.message}}

Please check back later or contact the instructor.

---

## Available Weeks

{" ".join([f"- [Week {w['number']}: {w['title']}](?week={w['number']})" for w in weeks])}`;
            }}
        }}

        function applyCustomStyling() {{
            const slides = document.querySelectorAll('.reveal .slides section');

            slides.forEach((slide, index) => {{
                const slideContent = slide.textContent.trim();

                if (
                    slideContent.startsWith('목차') ||
                    slideContent.includes('Table of Contents') ||
                    slideContent.includes('다음 주차 예고') ||
                    slideContent.includes('정리') ||
                    slideContent.includes('Q&A') ||
                    slide.querySelector('h1:only-child') ||
                    (slide.children.length === 1 && slide.children[0].tagName === 'H1') ||
                    // 섹션 제목 슬라이드 - H1 태그만 있는 경우
                    (slide.children.length === 1 && slide.querySelector('h1') &&
                     slide.querySelector('h1').textContent.trim().length > 0 &&
                     !slide.querySelector('h2, h3, p, ul, ol, div, img, pre, code'))
                ) {{
                    slide.style.textAlign = 'center';
                    slide.style.display = 'flex';
                    slide.style.flexDirection = 'column';
                    slide.style.justifyContent = 'center';
                    slide.style.height = '100%';
                }}
            }});
        }}

        function addBackButton() {{
            const backButton = document.createElement('button');
            backButton.innerHTML = '← 메인으로';
            backButton.style.cssText = `
                position: fixed;
                bottom: 20px;
                left: 20px;
                z-index: 1000;
                background: rgba(42, 85, 153, 0.9);
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 30px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.4s ease;
                box-shadow: 0 4px 15px rgba(42, 85, 153, 0.3);
                backdrop-filter: blur(10px);
                opacity: 0.3;
                transform: translateX(-10px);
            `;

            backButton.addEventListener('mouseover', () => {{
                backButton.style.background = 'rgba(42, 85, 153, 1)';
                backButton.style.transform = 'translateX(0) translateY(-2px)';
                backButton.style.boxShadow = '0 6px 20px rgba(42, 85, 153, 0.4)';
                backButton.style.opacity = '1';
            }});

            backButton.addEventListener('mouseout', () => {{
                backButton.style.background = 'rgba(42, 85, 153, 0.9)';
                backButton.style.transform = 'translateX(-10px)';
                backButton.style.boxShadow = '0 4px 15px rgba(42, 85, 153, 0.3)';
                backButton.style.opacity = '0.3';
            }});

            backButton.addEventListener('click', () => {{
                window.location.href = '/';
            }});

            document.body.appendChild(backButton);
        }}

        function addDrawingFeature(deck) {{
            let isDrawing = false;
            let drawingMode = false;
            let currentTool = 'pen';
            let currentColor = '#ff0000';
            let currentSize = 3;
            let canvas, ctx;
            let drawingData = new Map(); // Store drawings per slide

            // Create canvas overlay
            function createCanvas() {{
                canvas = document.createElement('canvas');
                canvas.id = 'drawing-canvas';
                canvas.style.cssText = `
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    z-index: 100;
                    pointer-events: none;
                    display: none;
                `;

                const presentationDiv = document.querySelector('.reveal');
                presentationDiv.appendChild(canvas);

                ctx = canvas.getContext('2d');

                // Set canvas size
                function resizeCanvas() {{
                    const rect = presentationDiv.getBoundingClientRect();
                    canvas.width = rect.width;
                    canvas.height = rect.height;
                    ctx.lineCap = 'round';
                    ctx.lineJoin = 'round';
                }}

                resizeCanvas();
                window.addEventListener('resize', resizeCanvas);

                return canvas;
            }}

            // Create drawing toolbar
            function createToolbar() {{
                const toolbar = document.createElement('div');
                toolbar.id = 'drawing-toolbar';
                toolbar.style.cssText = `
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    z-index: 1001;
                    background: rgba(0, 0, 0, 0.8);
                    padding: 10px;
                    border-radius: 10px;
                    display: none;
                    flex-direction: column;
                    gap: 10px;
                    backdrop-filter: blur(10px);
                `;

                // Drawing toggle button
                const toggleBtn = document.createElement('button');
                toggleBtn.innerHTML = '✏️';
                toggleBtn.title = 'Toggle Drawing (D)';
                toggleBtn.style.cssText = `
                    background: ${{drawingMode ? '#ff4444' : '#4CAF50'}};
                    color: white;
                    border: none;
                    padding: 8px;
                    border-radius: 5px;
                    cursor: pointer;
                    font-size: 16px;
                `;

                // Pen tool
                const penBtn = document.createElement('button');
                penBtn.innerHTML = '🖊️';
                penBtn.title = 'Pen Tool';
                penBtn.style.cssText = `
                    background: ${{currentTool === 'pen' ? '#2196F3' : '#666'}};
                    color: white;
                    border: none;
                    padding: 8px;
                    border-radius: 5px;
                    cursor: pointer;
                    font-size: 14px;
                `;

                // Eraser tool
                const eraserBtn = document.createElement('button');
                eraserBtn.innerHTML = '🧽';
                eraserBtn.title = 'Eraser Tool';
                eraserBtn.style.cssText = `
                    background: ${{currentTool === 'eraser' ? '#2196F3' : '#666'}};
                    color: white;
                    border: none;
                    padding: 8px;
                    border-radius: 5px;
                    cursor: pointer;
                    font-size: 14px;
                `;

                // Color picker
                const colorPicker = document.createElement('input');
                colorPicker.type = 'color';
                colorPicker.value = currentColor;
                colorPicker.title = 'Color';
                colorPicker.style.cssText = `
                    width: 30px;
                    height: 30px;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                `;

                // Size slider
                const sizeSlider = document.createElement('input');
                sizeSlider.type = 'range';
                sizeSlider.min = '1';
                sizeSlider.max = '20';
                sizeSlider.value = currentSize;
                sizeSlider.title = 'Brush Size';
                sizeSlider.style.cssText = `
                    width: 80px;
                `;

                // Clear button
                const clearBtn = document.createElement('button');
                clearBtn.innerHTML = '🗑️';
                clearBtn.title = 'Clear Drawing (C)';
                clearBtn.style.cssText = `
                    background: #FF5722;
                    color: white;
                    border: none;
                    padding: 8px;
                    border-radius: 5px;
                    cursor: pointer;
                    font-size: 14px;
                `;

                // Event listeners
                toggleBtn.addEventListener('click', toggleDrawingMode);
                penBtn.addEventListener('click', () => setTool('pen'));
                eraserBtn.addEventListener('click', () => setTool('eraser'));
                colorPicker.addEventListener('change', (e) => {{
                    currentColor = e.target.value;
                }});
                sizeSlider.addEventListener('input', (e) => {{
                    currentSize = parseInt(e.target.value);
                }});
                clearBtn.addEventListener('click', clearCurrentSlide);

                toolbar.appendChild(toggleBtn);
                toolbar.appendChild(penBtn);
                toolbar.appendChild(eraserBtn);
                toolbar.appendChild(colorPicker);
                toolbar.appendChild(sizeSlider);
                toolbar.appendChild(clearBtn);

                document.body.appendChild(toolbar);

                return {{ toolbar, toggleBtn, penBtn, eraserBtn }};
            }}

            function toggleDrawingMode() {{
                drawingMode = !drawingMode;
                if (drawingMode) {{
                    canvas.style.display = 'block';
                    canvas.style.pointerEvents = 'all';
                    toolbar.toggleBtn.style.background = '#ff4444';
                    toolbar.toggleBtn.innerHTML = '❌';
                    loadCurrentSlideDrawing();
                }} else {{
                    canvas.style.display = 'none';
                    canvas.style.pointerEvents = 'none';
                    toolbar.toggleBtn.style.background = '#4CAF50';
                    toolbar.toggleBtn.innerHTML = '✏️';
                    saveCurrentSlideDrawing();
                }}
                updateToolbarVisibility();
            }}

            function setTool(tool) {{
                currentTool = tool;
                toolbar.penBtn.style.background = tool === 'pen' ? '#2196F3' : '#666';
                toolbar.eraserBtn.style.background = tool === 'eraser' ? '#2196F3' : '#666';
            }}

            function updateToolbarVisibility() {{
                const toolbarDiv = document.getElementById('drawing-toolbar');
                toolbarDiv.style.display = drawingMode ? 'flex' : 'none';
            }}

            function getCurrentSlideIndex() {{
                return deck.getState().indexh + '-' + deck.getState().indexv;
            }}

            function saveCurrentSlideDrawing() {{
                const slideIndex = getCurrentSlideIndex();
                const imageData = canvas.toDataURL();
                drawingData.set(slideIndex, imageData);
            }}

            function loadCurrentSlideDrawing() {{
                const slideIndex = getCurrentSlideIndex();
                ctx.clearRect(0, 0, canvas.width, canvas.height);

                if (drawingData.has(slideIndex)) {{
                    const img = new Image();
                    img.onload = () => {{
                        ctx.drawImage(img, 0, 0);
                    }};
                    img.src = drawingData.get(slideIndex);
                }}
            }}

            function clearCurrentSlide() {{
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                const slideIndex = getCurrentSlideIndex();
                drawingData.delete(slideIndex);
            }}

            // Drawing functions
            function startDrawing(e) {{
                if (!drawingMode) return;
                isDrawing = true;

                const rect = canvas.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;

                ctx.beginPath();
                ctx.moveTo(x, y);

                if (currentTool === 'eraser') {{
                    ctx.globalCompositeOperation = 'destination-out';
                    ctx.lineWidth = currentSize * 3;
                }} else {{
                    ctx.globalCompositeOperation = 'source-over';
                    ctx.strokeStyle = currentColor;
                    ctx.lineWidth = currentSize;
                }}
            }}

            function draw(e) {{
                if (!drawingMode || !isDrawing) return;

                const rect = canvas.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;

                ctx.lineTo(x, y);
                ctx.stroke();
            }}

            function stopDrawing() {{
                if (!drawingMode) return;
                isDrawing = false;
                ctx.beginPath();
            }}

            // Initialize components
            createCanvas();
            const toolbar = createToolbar();

            // Add event listeners
            canvas.addEventListener('mousedown', startDrawing);
            canvas.addEventListener('mousemove', draw);
            canvas.addEventListener('mouseup', stopDrawing);
            canvas.addEventListener('mouseout', stopDrawing);

            // Touch events for mobile
            canvas.addEventListener('touchstart', (e) => {{
                e.preventDefault();
                const touch = e.touches[0];
                const mouseEvent = new MouseEvent('mousedown', {{
                    clientX: touch.clientX,
                    clientY: touch.clientY
                }});
                canvas.dispatchEvent(mouseEvent);
            }});

            canvas.addEventListener('touchmove', (e) => {{
                e.preventDefault();
                const touch = e.touches[0];
                const mouseEvent = new MouseEvent('mousemove', {{
                    clientX: touch.clientX,
                    clientY: touch.clientY
                }});
                canvas.dispatchEvent(mouseEvent);
            }});

            canvas.addEventListener('touchend', (e) => {{
                e.preventDefault();
                const mouseEvent = new MouseEvent('mouseup', {{}});
                canvas.dispatchEvent(mouseEvent);
            }});

            // Keyboard shortcuts
            document.addEventListener('keydown', (e) => {{
                if (e.target.tagName === 'INPUT') return; // Don't interfere with inputs

                switch(e.key.toLowerCase()) {{
                    case 'd':
                        e.preventDefault();
                        toggleDrawingMode();
                        break;
                    case 'c':
                        if (drawingMode && e.ctrlKey) {{
                            e.preventDefault();
                            clearCurrentSlide();
                        }}
                        break;
                    case 'p':
                        if (drawingMode) {{
                            e.preventDefault();
                            setTool('pen');
                        }}
                        break;
                    case 'e':
                        if (drawingMode) {{
                            e.preventDefault();
                            setTool('eraser');
                        }}
                        break;
                }}
            }});

            // Handle slide changes
            deck.on('slidechanged', (event) => {{
                if (drawingMode) {{
                    saveCurrentSlideDrawing();
                    setTimeout(() => loadCurrentSlideDrawing(), 100);
                }}
            }});

            // Save drawings before leaving
            window.addEventListener('beforeunload', () => {{
                if (drawingMode) {{
                    saveCurrentSlideDrawing();
                }}
            }});
        }}
    </script>
</body>
</html>'''

    return html_content

def main():
    """Main function to generate index.html"""

    # Get script directory and project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    slides_dir = project_root / "slides"

    print(f"🔍 Scanning weeks in: {slides_dir}")

    # Scan for weeks
    weeks = scan_weeks_directory(slides_dir)

    if not weeks:
        print("❌ No weeks found in slides directory!")
        return

    print(f"✅ Found {len(weeks)} weeks:")
    for week in weeks:
        status = []
        if week['has_slides']:
            status.append("📄")
        if week['has_code']:
            status.append("💻")
        if week['has_images']:
            status.append("🖼️")
        status_str = "".join(status) if status else "📋"
        print(f"   Week {week['number']}: {week['title']} {status_str}")

    # Generate index.html
    print(f"🏗️  Generating index.html...")
    html_content = generate_index_html(weeks)

    # Write index.html
    index_path = project_root / "src" / "index.html"
    try:
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"✅ Successfully generated: {index_path}")
        print(f"📊 Generated {len(weeks)} lecture cards")
    except Exception as e:
        print(f"❌ Failed to write index.html: {e}")
        return

    # Generate summary report
    print(f"\\n📋 Summary:")
    print(f"   - Total weeks: {len(weeks)}")
    print(f"   - Weeks with slides: {sum(1 for w in weeks if w['has_slides'])}")
    print(f"   - Weeks with code: {sum(1 for w in weeks if w['has_code'])}")
    print(f"   - Weeks with images: {sum(1 for w in weeks if w['has_images'])}")
    print(f"\\n🚀 Ready to serve at: http://localhost:5173")

if __name__ == "__main__":
    main()