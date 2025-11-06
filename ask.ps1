#!/usr/bin/env pwsh
# Quick launcher for CyberSamantha (fast mode)
# Usage: .\ask.ps1 "your question here" [-Banner]

param(
    [Parameter(Mandatory=$true)]
    [string]$Question,
    
    [Parameter(Mandatory=$false)]
    [switch]$Banner
)

if ($Banner) {
    python cybersamatha.py --question $Question --quiet --banner
} else {
    python cybersamatha.py --question $Question --quiet
}
