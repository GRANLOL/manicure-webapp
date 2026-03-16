@echo off
setlocal

if exist ".\.venv\Scripts\python.exe" (
    ".\.venv\Scripts\python.exe" scripts\backup_database.py
) else (
    python scripts\backup_database.py
)

endlocal
