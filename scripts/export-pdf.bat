@echo off
setlocal enabledelayedexpansion

if "%1"=="" (
    echo Usage: export-pdf.bat [week_number]
    echo Example: export-pdf.bat 03
    echo.
    echo Available options:
    echo   Week number: 01, 02, 03, 04, 05, etc.
    echo.
    pause
    exit /b 1
)

set WEEK=%1

echo Exporting PDF for Week %WEEK%...
echo.

REM Auto-detect running development server port
echo Detecting development server...
set DEV_PORT=

REM Check common ports
for %%p in (5173 5174 3000 8080) do (
    curl -s http://localhost:%%p >nul 2>&1
    if !errorlevel! equ 0 (
        set DEV_PORT=%%p
        echo Found development server on port %%p
        goto :found_server
    )
)

echo Error: No development server found on common ports (5173, 5174, 3000, 8080)
echo Please start the development server first with: scripts\start-dev.bat
echo.
pause
exit /b 1

:found_server

REM Create pdf-exports directory if it doesn't exist
if not exist "pdf-exports" mkdir pdf-exports

echo Generating PDF... This may take a few moments.
node tools/export-pdf.mjs --week %WEEK% --port %DEV_PORT%

if %errorlevel% eq 0 (
    echo.
    echo ✓ PDF generated successfully!
    echo Check pdf-exports folder for week%WEEK%.pdf
) else (
    echo.
    echo ✗ PDF generation failed!
    echo Make sure:
    echo   1. Development server is running
    echo   2. Week %WEEK% content exists
    echo   3. All dependencies are installed
)

echo.
pause