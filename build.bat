@echo off
chcp 65001 >nul
title Build - Excel Editor

echo.
echo ============================================
echo   Excel Editor Platform - Build Script
echo ============================================
echo.

REM ────────────────────────────────────────────
REM  Detect Python: prefer project .venv
REM ────────────────────────────────────────────
if exist ".venv\Scripts\python.exe" (
    set PYTHON=.venv\Scripts\python.exe
    set PIP=.venv\Scripts\pip.exe
    echo [INFO] Using project virtualenv: .venv\
) else (
    set PYTHON=python
    set PIP=pip
    echo [INFO] Using system Python
)

%PYTHON% --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.8+ and add to PATH.
    pause
    exit /b 1
)
echo [OK] Python found:
%PYTHON% --version
echo.

REM ────────────────────────────────────────────
REM  Step 1 - Install dependencies
REM ────────────────────────────────────────────
echo [Step 1/4] Installing dependencies...
%PIP% install flask pyinstaller --quiet --disable-pip-version-check
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies. Check your network.
    pause
    exit /b 1
)
echo [OK] Dependencies ready.
echo.

REM ────────────────────────────────────────────
REM  Step 2 - Clean old build artifacts
REM ────────────────────────────────────────────
echo [Step 2/4] Cleaning old build files...
if exist "build"  rmdir /s /q "build"  2>nul
if exist "dist\Excel_Editor.exe" del /q "dist\Excel_Editor.exe" 2>nul
echo [OK] Clean done.
echo.

REM ────────────────────────────────────────────
REM  Step 3 - Run PyInstaller
REM ────────────────────────────────────────────
echo [Step 3/4] Packaging (may take 1~3 minutes on first run)...
echo.
%PYTHON% -m PyInstaller "Excel在线编辑平台.spec" --noconfirm --clean

if errorlevel 1 (
    echo.
    echo [ERROR] Build FAILED. See messages above for details.
    pause
    exit /b 1
)

REM ────────────────────────────────────────────
REM  Step 4 - Create output directories & README
REM ────────────────────────────────────────────
echo [Step 4/4] Setting up dist folder structure...

if not exist "dist\logs"   mkdir "dist\logs"
if not exist "dist\output" mkdir "dist\output"

REM Write README (plain ASCII to avoid encoding issues)
(
echo Excel Editor Platform - README
echo ================================
echo.
echo HOW TO START:
echo   Double-click "Excel_Editor.exe"
echo   The browser will open automatically.
echo   Close the console window to stop the server.
echo.
echo FOLDERS:
echo   logs\    Server logs (new file each run)
echo   output\  Excel files exported from the platform
echo.
echo NOTES:
echo   - No Python installation required on target PC
echo   - Internet connection needed for CDN resources
echo     (TailwindCSS / Iconify / xlsx.js)
echo   - Uploaded files are processed locally in the browser
echo   - Exported files are also saved to output\ as backup
) > "dist\README.txt"

REM ────────────────────────────────────────────
REM  Done
REM ────────────────────────────────────────────
echo.
echo ============================================
echo   BUILD SUCCESSFUL
echo ============================================
echo.
echo   Executable : dist\Excel_Editor.exe
echo   Logs       : dist\logs\
echo   Exports    : dist\output\
echo   README     : dist\README.txt
echo.
echo   Copy the entire dist\ folder to any Windows PC to use.
echo.
pause
