@echo off
REM Quick launcher for CyberSamantha (fast mode)
REM Usage: ask.bat "your question here"

if "%~1"=="" (
    echo Usage: ask.bat "your question here"
    echo Example: ask.bat "What is XSS?"
    exit /b 1
)

python cybersamatha.py --question "%~1" --quiet
