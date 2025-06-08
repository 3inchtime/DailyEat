@echo off
chcp 65001 >nul
echo.
echo ========================================
echo      Starting Frontend and Backend Services
echo ========================================
echo.

echo Starting backend service...
start "Daily Eat Backend" cmd /k "cd backend && venv\Scripts\activate.bat && python manage.py runserver 127.0.0.1:8000"

echo Waiting for backend to start...
timeout /t 3 /nobreak >nul

echo Starting frontend service...
start "Daily Eat Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo Services started successfully!
echo.
echo Frontend URL: http://localhost:5173
echo Backend URL: http://127.0.0.1:8000
echo Admin Panel: http://127.0.0.1:8000/admin
echo.
echo Test Account: fooduser / 12345678
echo Admin Account: admin / admin
echo.
echo Closing this window will not stop services, press Ctrl+C in each service window to stop
pause
