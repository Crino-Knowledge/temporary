@echo off
if exist ".venv\Scripts\python.exe" (
    .venv\Scripts\python.exe -m py_compile build.py >nul 2>&1
    .venv\Scripts\python.exe build.py
) else (
    python build.py
)
pause
