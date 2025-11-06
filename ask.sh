#!/bin/bash
# Quick launcher for CyberSamantha (fast mode)
# Usage: ./ask.sh "your question here"

if [ -z "$1" ]; then
    echo "Usage: ./ask.sh \"your question here\""
    echo "Example: ./ask.sh \"What is XSS?\""
    exit 1
fi

python cybersamatha.py --question "$1" --quiet
