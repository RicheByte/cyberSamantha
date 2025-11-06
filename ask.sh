#!/bin/bash
# Quick launcher for CyberSamantha (fast mode)
# Usage: ./ask.sh "your question here" [--banner]

if [ -z "$1" ]; then
    echo "Usage: ./ask.sh \"your question here\" [--banner]"
    echo "Example: ./ask.sh \"What is XSS?\""
    echo "Example: ./ask.sh \"What is XSS?\" --banner"
    exit 1
fi

if [ "$2" = "--banner" ]; then
    python cybersamatha.py --question "$1" --quiet --banner
else
    python cybersamatha.py --question "$1" --quiet
fi
