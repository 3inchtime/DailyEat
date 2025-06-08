@echo off
chcp 65001 >nul
echo.
echo ========================================
echo    Daily Eat Project Windows Setup
echo ========================================
echo.

REM Check Python installation
echo [1/10] Checking Python environment...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not installed or not in PATH
    echo Please install Python 3.8+ and add to system PATH
    pause
    exit /b 1
)
echo SUCCESS: Python environment check passed

REM Check Node.js installation
echo.
echo [2/10] Checking Node.js environment...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js not installed or not in PATH
    echo Please install Node.js 16+ and add to system PATH
    pause
    exit /b 1
)
echo SUCCESS: Node.js environment check passed

REM Check MySQL service
echo.
echo [3/10] Checking MySQL service...
sc query mysql >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: MySQL service not running
    echo Please ensure MySQL is installed and started
    echo Continuing installation, but database needs manual configuration...
) else (
    echo SUCCESS: MySQL service is running
)

REM Create backend virtual environment
echo.
echo [4/10] Setting up backend Python virtual environment...
cd backend
if not exist venv (
    python -m venv venv
    echo SUCCESS: Virtual environment created
) else (
    echo SUCCESS: Virtual environment already exists
)

REM Activate virtual environment and install dependencies
echo.
echo [5/10] Installing backend dependencies...
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Backend dependencies installation failed
    pause
    exit /b 1
)
echo SUCCESS: Backend dependencies installed

REM Create MySQL database
echo.
echo [6/10] Creating MySQL database...
python create_mysql_db.py
if %errorlevel% neq 0 (
    echo WARNING: Database creation failed, please manually create database daily_eat_db
)

REM Run database migrations
echo.
echo [7/10] Running database migrations...
python manage.py migrate
if %errorlevel% neq 0 (
    echo ERROR: Database migration failed
    pause
    exit /b 1
)
echo SUCCESS: Database migration completed

REM Setup initial data
echo.
echo [8/10] Setting up initial data...
python manage_data.py setup
echo SUCCESS: Initial data setup completed

REM Return to root directory and setup frontend
cd ..
echo.
echo [9/10] Installing frontend dependencies...
cd frontend
call npm install
if %errorlevel% neq 0 (
    echo ERROR: Frontend dependencies installation failed
    pause
    exit /b 1
)
echo SUCCESS: Frontend dependencies installed

REM Installation completed
cd ..
echo.
echo [10/10] Installation completed!
echo.
echo ========================================
echo        Installation Successful!
echo ========================================
echo.
echo Project Information:
echo    Backend URL: http://127.0.0.1:8000
echo    Frontend URL: http://localhost:5173
echo    Database: MySQL (daily_eat_db)
echo.
echo Test Accounts:
echo    Username: fooduser
echo    Password: 12345678
echo    Admin: admin / admin
echo.
echo Start Commands:
echo    Start Backend: run_backend.bat
echo    Start Frontend: run_frontend.bat
echo    Start Both: run_all.bat
echo.
echo For more information, please check README.md
echo.
pause
