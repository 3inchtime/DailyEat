@echo off
chcp 65001 >nul
echo.
echo ========================================
echo      Starting Daily Eat Backend Service
echo ========================================
echo.

cd backend
echo Activating Python virtual environment...
call venv\Scripts\activate.bat

echo Starting Django development server...
echo Backend URL: http://127.0.0.1:8000
echo Admin Panel: http://127.0.0.1:8000/admin
echo.
echo Press Ctrl+C to stop the server
echo.

python manage.py runserver 127.0.0.1:8000
