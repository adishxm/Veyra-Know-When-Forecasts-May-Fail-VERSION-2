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
start "HEXARK-Backend" cmd /k "title HEXARK Backend [Port 8000] && python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload"

echo  [*] Waiting for backend to initialize...
ping 127.0.0.1 -n 4 >nul

:: --- Start Frontend Dev Server ---
echo.
echo  ===================================================================
echo   Starting Veyra Dashboard Frontend [port 5173]...
echo  ===================================================================
start "HEXARK-Frontend" cmd /k "title HEXARK Frontend [Port 5173] && cd frontend && npm run dev"

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
echo  ^|                                                                 ^|
echo  ^|   Backend:    http://127.0.0.1:8000                             ^|
echo  ^|   Frontend:   http://127.0.0.1:5173                             ^|
echo  ^|   API Docs:   http://127.0.0.1:8000/docs                        ^|
echo  ^|                                                                 ^|
echo  ^|   Press any key in this window to stop all servers...           ^|
echo  ^|                                                                 ^|
echo  +-----------------------------------------------------------------+
echo.
pause >nul

:: --- Shutdown Servers ---
echo.
echo  [*] Shutting down servers...
taskkill /FI "WINDOWTITLE eq HEXARK-Backend*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq HEXARK-Frontend*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq HEXARK Backend*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq HEXARK Frontend*" /F >nul 2>&1
echo  [OK] All servers stopped.
echo.
ping 127.0.0.1 -n 2 >nul
