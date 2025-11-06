#!/usr/bin/env pwsh
# Quick launcher for CyberSamantha (fast mode)
# Usage: .\ask.ps1 "your question here"

param(
    [Parameter(Mandatory=$true)]
    [string]$Question
)

python cybersamatha.py --question $Question --quiet
