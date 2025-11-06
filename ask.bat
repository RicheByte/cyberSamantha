@echo off
REM Quick launcher for CyberSamantha (fast mode)
REM Usage: ask.bat "your question here" [--banner]

if "%~1"=="" (
    echo Usage: ask.bat "your question here" [--banner]
    echo Example: ask.bat "What is XSS?"
    echo Example: ask.bat "What is XSS?" --banner
    exit /b 1
)

if "%~2"=="--banner" (
    python cybersamatha.py --question "%~1" --quiet --banner
) else (
    python cybersamatha.py --question "%~1" --quiet
)
