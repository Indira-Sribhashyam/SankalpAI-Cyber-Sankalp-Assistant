@echo off
setlocal

:: Check if venv exists and activate it
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo Virtual environment not found. Creating one...
    python -m venv venv
    call venv\Scripts\activate.bat
)

:: Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

:: Set placeholder GROQ API key for demo

:: Start FastAPI server
echo Starting Assistant...
uvicorn assistant_api:app --reload --port 8000

:: Pause if it crashes so user can see error
if %errorlevel% neq 0 pause
endlocal


