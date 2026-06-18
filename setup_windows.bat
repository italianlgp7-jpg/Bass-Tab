@echo off
REM ============================================================
REM  Bass Tab Generator - First-time setup (Windows)
REM  Double-click this file ONCE to install everything.
REM ============================================================
title Bass Tab Generator - Setup

echo ============================================================
echo   Bass Tab Generator  -  First-time setup
echo ============================================================
echo.

REM --- Check that Python is installed ---
python --version >nul 2>&1
if errorlevel 1 (
  echo [X] Python was not found on your computer.
  echo.
  echo     Please do this first:
  echo       1. Go to  https://www.python.org/downloads/
  echo       2. Click the big yellow "Download Python" button.
  echo       3. Run the installer.
  echo       4. IMPORTANT: tick the box "Add Python to PATH" at the bottom.
  echo       5. Finish the install, then double-click this file again.
  echo.
  pause
  exit /b 1
)
echo [OK] Python is installed.
echo.

REM --- Install ffmpeg (needed to read audio) ---
echo [1/2] Installing ffmpeg (handles the audio)...
winget install --id Gyan.FFmpeg -e --accept-package-agreements --accept-source-agreements
if errorlevel 1 (
  echo     ^(If that step failed, the program may still work; we'll see.^)
)
echo.

REM --- Install the Python pieces ---
echo [2/2] Installing the program's parts. This can take several minutes
echo       and downloads a lot the first time - please be patient.
echo.
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if errorlevel 1 (
  echo.
  echo [X] Something went wrong while installing. Scroll up to read the error,
  echo     or send me the last few red lines and I'll help.
  pause
  exit /b 1
)

echo.
echo ============================================================
echo   All done! You can now double-click  make_tab.bat
echo   to turn a YouTube song into a bass tab.
echo ============================================================
pause
