@echo off
:menu
cls
echo ===================================================
echo               CoAgent Master Task Menu
echo ===================================================
echo 1. Run Troubleshooting Module
echo 2. Run Fuel Calculator Module
echo 3. Run Proposal Generator
echo 4. Run Script Generator
echo 5. Run SEO and Website Tool
echo 6. Run Badge Generator
echo 7. Sync / Pull Latest Changes from GitHub
echo 8. Exit
echo ===================================================
echo.

set /p choice="Select an option (1-8): "

if "%choice%"=="1" python "%~dp0..\modules\co_troubleshoot.py" & pause & goto menu
if "%choice%"=="2" python "%~dp0..\modules\co_fuelcalc.py" & pause & goto menu
if "%choice%"=="3" python "%~dp0..\modules\co_proposal.py" & pause & goto menu
if "%choice%"=="4" python "%~dp0..\modules\co_scriptgen.py" & pause & goto menu
if "%choice%"=="5" python "%~dp0..\modules\co_seo.py" & pause & goto menu
if "%choice%"=="6" python "%~dp0..\modules\co_badge.py" & pause & goto menu
if "%choice%"=="7" git -C "%~dp0.." pull & pause & goto menu
if "%choice%"=="8" exit

goto menu