@echo off
chcp 65001 >nul
setlocal EnableExtensions
for /F "delims=" %%E in ('echo prompt $E^| cmd') do set "ESC=%%E"
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
echo %ESC%[36m[ ] Updating counters.json...%ESC%[0m

echo %ESC%[36m[ ] Scraping all counters from counter data sources...%ESC%[0m
python src/scrape/counters.py
echo %ESC%[33m[§] Successfully scraped all counters to:%ESC%[0m "./out/scraped/*.json"

rem create a backup of the existing counters.json file
if exist "counters.json" (
    copy /y "counters.json" ".old/counters.json" >nul
    echo %ESC%[33m[§] Backed up existing "counters.json" to:%ESC%[0m ".old/counters.json"
)

echo %ESC%[36m[ ] Combining all counters into counters.json...%ESC%[0m
python src/create/counters.py --confirm --verbose=false

goto :done


:portraits
echo %ESC%[36m[ ] Updating hero portraits...

rem Add your hero portrait update commands here.
echo %ESC%[31m[!] (WIP) Not yet implemented!%ESC%[0m

goto :done


:done
echo %ESC%[32m[§] Update finished.%ESC%[0m
pause
exit /b 0


:usage
echo Usage:
echo   update.bat --counters
echo   update.bat --portraits
echo   update.bat
exit /b 2