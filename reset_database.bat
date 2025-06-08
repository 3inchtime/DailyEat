@echo off
chcp 65001 >nul
echo.
echo ========================================
echo        Reset Daily Eat Database
echo ========================================
echo.
echo WARNING: This operation will delete all data!
echo.
set /p confirm="Confirm database reset? (y/N): "
if /i not "%confirm%"=="y" (
    echo Operation cancelled
    pause
    exit /b 0
)

cd backend
echo.
echo Activating Python virtual environment...
call venv\Scripts\activate.bat

echo.
echo Resetting database...
python create_mysql_db.py --reset

echo.
echo Running database migrations...
python manage.py migrate

echo.
echo Setting up initial data...
python manage_data.py setup

echo.
echo ========================================
echo        Database Reset Completed!
echo ========================================
echo.
echo Available Accounts:
echo    User: fooduser / 12345678
echo    Admin: admin / admin
echo.
pause
