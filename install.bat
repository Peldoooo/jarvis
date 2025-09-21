@echo off
REM JARVIS Assistant Installation Script for Windows
REM This script installs all dependencies for JARVIS

echo 🤖 Installing JARVIS Assistant Dependencies...
echo ================================================

REM Check Python version
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is required but not installed.
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

echo ✅ Python is installed

REM Create virtual environment
echo 📦 Creating virtual environment...
python -m venv jarvis_env
call jarvis_env\Scripts\activate.bat

REM Upgrade pip
echo ⬆️ Upgrading pip...
python -m pip install --upgrade pip

REM Install Python dependencies
echo 🐍 Installing Python dependencies...
pip install -r requirements.txt

REM Create necessary directories
echo 📁 Creating directories...
if not exist "output" mkdir output
if not exist "output\photos" mkdir output\photos
if not exist "output\videos" mkdir output\videos
if not exist "output\screenshots" mkdir output\screenshots
if not exist "logs" mkdir logs
if not exist "config" mkdir config
if not exist "assets" mkdir assets

REM Copy environment file
if not exist ".env" (
    echo 📄 Creating environment file...
    copy .env.example .env
    echo ⚠️ Please edit .env file and add your OpenRouter API key!
)

echo.
echo 🎉 Installation complete!
echo ================================================
echo Next steps:
echo 1. Edit .env file and add your OpenRouter API key
echo 2. Activate virtual environment: jarvis_env\Scripts\activate.bat
echo 3. Run JARVIS: python main.py
echo.
echo For more information, see README.md
echo.
pause
