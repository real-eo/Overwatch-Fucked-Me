@echo off
setlocal EnableExtensions
cd /d "%~dp0"

if not "%~2"=="" goto :usage

if /i "%~1"=="--dev" goto :dev
if /i "%~1"=="--release" goto :release
if not "%~1"=="" goto :usage

call :selectMode
if errorlevel 1 exit /b 1

if "%MODE%"=="0" exit /b 0

cls

if "%MODE%"=="1" goto :dev
if "%MODE%"=="2" goto :release
exit /b 1


:selectMode
set "MODE_FILE=%TEMP%\run-mode-%RANDOM%.tmp"

powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "$selected=2; $items=@('1] Python (dev)','2] Release'); function Draw { [Console]::Clear(); [Console]::WriteLine('Press number keys to select, then Enter to run. Esc to exit.'); [Console]::WriteLine(''); [Console]::WriteLine('Select run mode:'); foreach($item in $items) { $number=$item.Substring(0,1); if($selected -eq [int]$number) { [Console]::ForegroundColor='Green' }; [Console]::WriteLine('['+$item); [Console]::ResetColor() } }; Draw; while($true) { $key=[Console]::ReadKey($true); if($key.KeyChar -eq '1' -or $key.KeyChar -eq '2') { $selected=[int]$key.KeyChar.ToString(); Draw } elseif($key.Key -eq 'Enter') { [IO.File]::WriteAllText($env:MODE_FILE,$selected.ToString()); break } elseif($key.Key -eq 'Escape') { [IO.File]::WriteAllText($env:MODE_FILE,'0'); break } }"

if not exist "%MODE_FILE%" exit /b 0
set /p "MODE="<"%MODE_FILE%"
del /q "%MODE_FILE%" >nul 2>&1

exit /b 0


:dev
echo Running in Python development mode...
python main.py
goto :done


:release
echo Running Release build...
start "" "%~dp0dist\Overwatch-Fucked-Me.exe"
goto :done


:done
echo.
echo Run finished.
pause
exit /b 0


:usage
echo Usage:
echo   run.bat --dev
echo   run.bat --release
echo   run.bat
exit /b 2