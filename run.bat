@echo off
echo ========================================================
echo   Starting MedBot AI Healthcare System...
echo ========================================================

if not exist venv (
    echo [ERROR] Virtual environment not found. Running setup first...
    call setup.bat
)

call .\venv\Scripts\activate

:: Ensure model exists
if not exist models\medbot_model.pkl (
    echo Model not found. Training model first...
    python src\train.py
)

echo Starting Flask server...
echo Open your browser at http://127.0.0.1:5000
python src\app.py
pause
