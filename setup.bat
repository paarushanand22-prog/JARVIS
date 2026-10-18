@echo off
echo ========================================================
echo JARVIS Initial Setup Script
echo ========================================================
echo.
echo Step 1: Installing Python Requirements...
pip install -r requirements.txt
echo.
echo Step 2: Downloading required AI Models via Ollama...
echo (This may take a while depending on your internet speed)
echo.
echo Pulling llama3.2 (Fast Router / General AI - ~2GB)
ollama pull llama3.2
echo.
echo Pulling llama3.1 (System / Tool Calling AI - ~4.7GB)
ollama pull llama3.1
echo.
echo Pulling qwen2.5-coder (Coding AI - ~4.2GB)
ollama pull qwen2.5-coder
echo.
echo ========================================================
echo Setup Complete! 
echo To start JARVIS, run: python jarvis.py
echo ========================================================
pause
