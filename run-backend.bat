@echo off
cd /d "%~dp0apps\api"
".venv\Scripts\python.exe" -m uvicorn app.main:app --reload --port 8000
