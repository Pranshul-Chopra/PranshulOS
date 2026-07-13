@echo off
:: PranshulOS — Full Release Build Script
:: Run this from the repo root (where main.py lives).
:: Requires: Python 3.11 venv (venv311), Node.js, npm
::
:: Output: release\PranshulOS Setup 2.1.0.exe  (installer)
::         release\PranshulOS 2.1.0.exe         (portable)

setlocal enabledelayedexpansion

echo.
echo ========================================
echo  PranshulOS Build
echo ========================================
echo.

:: ── Step 1: Activate Python 3.11 venv ────────────────────────────────────────
echo [1/4] Activating Python 3.11 venv...
if not exist "venv311\Scripts\activate.bat" (
    echo ERROR: venv311 not found. Run setup first:
    echo   py -3.11 -m venv venv311
    echo   venv311\Scripts\activate
    echo   pip install -r requirements.txt pyinstaller
    pause & exit /b 1
)
call venv311\Scripts\activate.bat

:: ── Step 2: Build Flask exe with PyInstaller ──────────────────────────────────
echo [2/4] Building Flask backend with PyInstaller...
if exist flask-dist rmdir /s /q flask-dist
pyinstaller flask.spec --noconfirm
if errorlevel 1 (
    echo ERROR: PyInstaller build failed.
    pause & exit /b 1
)
echo Flask backend built → flask-dist\

:: ── Step 3: Install Electron dependencies ────────────────────────────────────
echo [3/4] Installing Electron dependencies...
cd electron
call npm install --silent
if errorlevel 1 (
    echo ERROR: npm install failed.
    cd ..
    pause & exit /b 1
)

:: ── Step 4: Package with electron-builder ────────────────────────────────────
echo [4/4] Packaging with electron-builder...
call npm run build
if errorlevel 1 (
    echo ERROR: electron-builder failed.
    cd ..
    pause & exit /b 1
)
cd ..

echo.
echo ========================================
echo  Build complete!
echo  Output: release\
echo ========================================
echo.
pause
