@echo off
cd /d "%~dp0"
title HEXARK - Veyra Sentinel Launcher
cls

:: --- Display Fastfetch Dashboard ---
python scripts\banner.py

:: --- Start Backend Server ---
echo  ===================================================================
echo   Starting Veyra Sentinel Backend [port 8000]...
echo  ===================================================================
start "HEXARK-Backend" cmd /c "title HEXARK-Backend && python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload"

echo  [*] Waiting for backend to initialize...
ping 127.0.0.1 -n 4 >nul

:: --- Start Frontend Dev Server ---
echo.
echo  ===================================================================
echo   Starting Veyra Dashboard Frontend [port 5173]...
echo  ===================================================================
start "HEXARK-Frontend" cmd /c "title HEXARK-Frontend && cd frontend && npm run dev"

echo  [*] Waiting for frontend to initialize...
ping 127.0.0.1 -n 5 >nul

:: --- Open Dashboard in Browser ---
echo.
echo  ===================================================================
echo   Opening Veyra Dashboard in your browser...
echo  ===================================================================
start "" "http://127.0.0.1:5173/Veyra-Know-When-Forecasts-May-Fail/"

echo.
echo  +-----------------------------------------------------------------+
echo  ^|                                                                 ^|
echo  ^|   VEYRA SENTINEL is now running!                                ^|
echo  ^|   Press any key in this window to stop all servers...           ^|
echo  ^|                                                                 ^|
echo  +-----------------------------------------------------------------+
echo.
pause >nul

:: --- Shutdown Servers ---
echo.
echo  [*] Shutting down servers and closing terminals...
taskkill /FI "WINDOWTITLE eq HEXARK-Backend*" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq HEXARK-Frontend*" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq HEXARK Backend*" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq HEXARK Frontend*" /T /F >nul 2>&1
powershell -NoProfile -Command "Get-NetTCPConnection -LocalPort 8000,5173 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }" >nul 2>&1
echo  [OK] All servers and spawned terminals closed.
echo.
ping 127.0.0.1 -n 2 >nul
