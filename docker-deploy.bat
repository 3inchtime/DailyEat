@echo off
chcp 65001 >nul
echo.
echo ==========================================
echo     Daily Eat Docker Deployment Script
echo ==========================================
echo.

REM Check Docker installation
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker not installed, please install Docker first
    pause
    exit /b 1
)

REM Check Docker Compose installation
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker Compose not installed, please install Docker Compose first
    pause
    exit /b 1
)

REM Create environment file if not exists
if not exist .env (
    echo Creating environment file...
    copy .env.example .env
    echo WARNING: Please edit .env file to set production passwords and configuration
    echo Especially SECRET_KEY and database passwords
)

REM Choose deployment mode
echo.
echo Please choose deployment mode:
echo 1) Development environment
echo 2) Production environment
set /p choice="Enter your choice (1-2): "

if "%choice%"=="1" (
    echo Starting development environment...
    docker-compose up --build -d
) else if "%choice%"=="2" (
    echo Starting production environment...
    docker-compose -f docker-compose.prod.yml up --build -d
) else (
    echo Invalid choice
    pause
    exit /b 1
)

echo.
echo Waiting for services to start...
timeout /t 10 /nobreak >nul

REM Check service status
echo.
echo Checking service status...
if "%choice%"=="1" (
    docker-compose ps
) else (
    docker-compose -f docker-compose.prod.yml ps
)

echo.
echo ==========================================
echo            Deployment Complete!
echo ==========================================
echo.
echo Access URLs:
echo    Frontend App: http://localhost
echo    Backend API: http://localhost:8000
echo    Admin Panel: http://localhost:8000/admin
echo    API Docs: http://localhost:8000/docs
echo.
echo Default Account:
echo    Username: admin
echo    Password: admin
echo.
echo Management Commands:
echo    View logs: docker-compose logs -f
echo    Stop services: docker-compose down
echo    Restart services: docker-compose restart
echo.
pause
