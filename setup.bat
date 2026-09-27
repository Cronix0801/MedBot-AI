@echo off
echo ========================================================
echo   Setting up MedBot AI Healthcare System
echo ========================================================

:: Check for Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python is not found in your PATH. Please install Python 3.10+ from python.org.
    pause
    exit /b 1
)

:: Create virtual environment if it does not exist
if not exist venv (
    echo [1/3] Creating virtual environment (venv)...
    python -m venv venv
) else (
    echo [1/3] Virtual environment already exists.
)

:: Install dependencies
echo [2/3] Installing dependencies from requirements.txt...
call .\venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt

:: Train model if not present
if not exist models\medbot_model.pkl (
    echo [3/3] Training MedBot AI model...
    python src\train.py
) else (
    echo [3/3] Model already exists at models\medbot_model.pkl.
)

echo.
echo ========================================================
echo   Setup completed successfully!
echo   Run 'run.bat' to start the application.
echo ========================================================
pause
