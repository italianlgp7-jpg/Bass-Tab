@echo off
REM ============================================================
REM  Bass Tab Generator - make a tab (Windows)
REM  Double-click this whenever you want a tab from a song.
REM ============================================================
title Bass Tab Generator

echo ============================================================
echo   Bass Tab Generator
echo ============================================================
echo.
echo  Tip: open the song on YouTube, copy the link from the address
echo       bar, then paste it below (right-click to paste).
echo.

set "URL="
set /p URL="Paste the YouTube link here and press Enter: "

if "%URL%"=="" (
  echo.
  echo You didn't paste a link. Closing.
  pause
  exit /b 1
)

echo.
echo Working on it... this can take a few minutes:
echo   - downloading the song
echo   - listening to ONLY the bass
echo   - writing out the tab
echo Please leave this window open until it finishes.
echo.

python -m bass_tab "%URL%" -o my_bass_tab.txt
if errorlevel 1 (
  echo.
  echo Hmm, something went wrong. Scroll up to read the message,
  echo or copy it to me and I'll help you fix it.
  pause
  exit /b 1
)

echo.
echo Saved! Opening your tab now (file name: my_bass_tab.txt).
start notepad my_bass_tab.txt
echo.
pause
