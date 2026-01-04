@echo off
REM ================================================
REM One-click package Tkinter GUI program - Nuitka version (with ICO icon)
REM ================================================

REM Your Python script filename (modify here)
set SCRIPT_NAME=gui_assistant.py

REM Your program icon file (modify here)
set ICON_FILE=..\keyboard_5643.ico

REM Check if icon file exists
if not exist "%ICON_FILE%" (
    echo [ERROR] Icon file "%ICON_FILE%" not found. Please place it in the correct path or modify ICON_FILE.
    pause
    exit /b 1
)

REM Check if Nuitka is installed
pip show nuitka >nul 2>nul
if errorlevel 1 (
    echo [INFO] Nuitka not installed, installing...
    pip install nuitka
)

REM Package command
python -m nuitka ^
    --standalone ^
    --onefile ^
    --enable-plugin=tk-inter ^
    --windows-console-mode=disable ^
    --lto=yes ^
    --windows-icon-from-ico="%ICON_FILE%" ^
    "%SCRIPT_NAME%"

REM Packaging completion prompt
echo.
echo ==========================================
echo [OK] Packaging completed!
echo Output file is located in dist\%~nSCRIPT_NAME%.exe
echo ==========================================
pause
