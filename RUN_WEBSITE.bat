@echo off
cd /d "%~dp0"
title Enterprise Sales Intelligence Website
if exist "venv\Scripts\python.exe" (
  call "venv\Scripts\activate.bat"
) else (
  echo No local venv found. Using your default Python environment.
)
python -m streamlit --version >nul 2>&1
if errorlevel 1 (
  echo Streamlit is not installed. Installing project requirements...
  python -m pip install -r requirements.txt
  if errorlevel 1 (
    echo.
    echo Installation failed. Check your Python/pip setup and try again.
    pause
    exit /b 1
  )
)
echo.
echo Starting the website. Keep this window open while using it.
echo If the browser does not open, visit http://localhost:8501
python -m streamlit run app.py
pause
