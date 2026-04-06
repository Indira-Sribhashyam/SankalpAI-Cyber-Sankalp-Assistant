@echo off
setlocal
echo ==============================================
echo Deploying SankalpAI Assistant to Cloudflare...
echo ==============================================

:: Check if venv exists
if not exist venv\Scripts\python.exe (
    echo Error: venv not found. Please run run_assistant.bat first.
    pause
    exit /b 1
)

:: Start the API server in the background using START to open a new minimised cmd window or same window
echo Starting FastAPI backend...
start "SankalpAI API Server" cmd /c "venv\Scripts\python.exe -m uvicorn assistant_api:app --host 0.0.0.0 --port 8000"

:: Wait a brief moment to ensure node starts
timeout /t 3 /nobreak >nul

:: Start Cloudflare tunnel
echo Starting Cloudflare Tunnel...
echo Look for the "trycloudflare.com" link in the output below!
echo.
cloudflared tunnel --url http://localhost:8000

endlocal
