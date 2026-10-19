@echo off
setlocal EnableExtensions
cd /d "%~dp0"

if not "%~2"=="" goto :usage

if /i "%~1"=="--counters" goto :counters
if /i "%~1"=="--portraits" goto :portraits
if not "%~1"=="" goto :usage

call :selectMode
if errorlevel 1 exit /b 1

cls

if "%MODE%"=="1" goto :counters
if "%MODE%"=="2" goto :portraits
exit /b 1


:selectMode
set "MODE_FILE=%TEMP%\update-mode-%RANDOM%.tmp"

powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "$selected=0; $items=@('1] Counters','2] Portraits'); function Draw { [Console]::Clear(); [Console]::WriteLine('Press number keys to select, then Enter to run. Esc to exit.'); [Console]::WriteLine(''); [Console]::WriteLine('Select update mode:'); foreach($item in $items) { $number=$item.Substring(0,1); if($selected -eq [int]$number) { [Console]::ForegroundColor='Green' }; [Console]::WriteLine('['+$item); [Console]::ResetColor() } }; Draw; while($true) { $key=[Console]::ReadKey($true); if($key.KeyChar -eq '1' -or $key.KeyChar -eq '2') { $selected=[int]$key.KeyChar.ToString(); Draw } elseif($key.Key -eq 'Enter' -and $selected -ne 0) { [IO.File]::WriteAllText($env:MODE_FILE,$selected.ToString()); break } elseif($key.Key -eq 'Escape') { [IO.File]::WriteAllText($env:MODE_FILE,'0'); break } }"

if not exist "%MODE_FILE%" exit /b 0
set /p "MODE="<"%MODE_FILE%"
del /q "%MODE_FILE%" >nul 2>&1

if "%MODE%"=="0" exit /b 0
exit /b 0


:counters
echo Updating counters.json...

rem Add your counters update commands here.

goto :done


:portraits
echo Updating hero portraits...

rem Add your hero portrait update commands here.

goto :done


:done
echo.
echo Update finished.
pause
exit /b 0


:usage
echo Usage:
echo   update.bat --counters
echo   update.bat --portraits
echo   update.bat
exit /b 2