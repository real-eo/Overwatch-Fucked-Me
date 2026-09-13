@echo off

REM Check if "--dev" argument is provided
set "DEV_MODE=false"
for %%A in (%*) do (
    if "%%A"=="--dev" (
        set "DEV_MODE=true"
    )
)

REM If in dev mode, run the Python script directly
if "%DEV_MODE%"=="true" (
    echo Running in development mode...
    python main.py

REM Otherwise, run the compiled EXE
) else (
    cd "%~dp0dist"
    start "" "Overwatch Fucked Me.exe"
)
