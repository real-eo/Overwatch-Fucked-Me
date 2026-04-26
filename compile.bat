@echo off
setlocal enableextensions

cd /d "%~dp0"

echo [1/5] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not available in PATH.
    exit /b 1
)

echo [2/5] Ensuring PyInstaller is installed...
python -m PyInstaller --version >nul 2>&1
if errorlevel 1 (
    python -m pip install --upgrade pyinstaller
    if errorlevel 1 (
        echo Failed to install PyInstaller.
        exit /b 1
    )
)

echo [3/5] Cleaning old build output...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

set "ICON=res/build assets/logo.ico"
if not exist "%ICON%" (
    echo Icon not found at: %ICON%
    exit /b 1
)

echo [4/5] Building standalone EXE...
python -m PyInstaller ^
    --noconfirm ^
    --clean ^
    compile.spec

if errorlevel 1 (
    echo Build failed.
    exit /b 1
)

echo [5/5] Done.
echo EXE created at: dist\Overwatch Fucked Me.exe
exit /b 0