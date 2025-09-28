@echo off
echo Stopping Vite development server...

REM Kill vite processes by name
taskkill /f /im "node.exe" /fi "WINDOWTITLE eq Administrator:  C:\WINDOWS\system32\cmd.exe - vite*" 2>nul
taskkill /f /im "node.exe" /fi "COMMANDLINE eq *vite*" 2>nul

REM Alternative: Kill by port (assuming default vite port 5173)
netstat -ano | findstr :5173 > nul
if %errorlevel% == 0 (
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5173') do (
        taskkill /f /pid %%a 2>nul
    )
)

echo Development server stopped.
pause