@echo off
chcp 65001 >nul
echo.
echo ========================================
echo      Starting Daily Eat Frontend Service
echo ========================================
echo.

cd frontend
echo Starting Vue development server...
echo Frontend URL: http://localhost:5173
echo.
echo Press Ctrl+C to stop the server
echo.

npm run dev
