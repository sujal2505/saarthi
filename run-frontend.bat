@echo off
set "PATH=C:\Program Files\nodejs;%PATH%"
cd /d "%~dp0apps\web"
npm run dev
