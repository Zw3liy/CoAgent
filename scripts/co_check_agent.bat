@echo off
echo [Co Agent] Running diagnostic checks...

:: Check root directories
if not exist "C:\CoAgent\modules" mkdir C:\CoAgent\modules
if not exist "C:\CoAgent\logs" mkdir C:\CoAgent\logs
if not exist "C:\CoAgent\output" mkdir C:\CoAgent\output

:: Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python.
) else (
    echo [OK] Python detected.
)

:: Check modules
if exist "C:\CoAgent\modules\co_troubleshoot.py" (
    echo [OK] Troubleshoot module found.
) else (
    echo [WARN] co_troubleshoot.py missing.
)

if exist "C:\CoAgent\modules\co_fuelcalc.py" (
    echo [OK] FuelCalc module found.
) else (
    echo [WARN] co_fuelcalc.py missing.
)

if exist "C:\CoAgent\modules\co_proposal.py" (
    echo [OK] Proposal module found.
) else (
    echo [WARN] co_proposal.py missing.
)

if exist "C:\CoAgent\modules\co_scriptgen.py" (
    echo [OK] ScriptGen module found.
) else (
    echo [WARN] co_scriptgen.py missing.
)

echo [Co Agent] Diagnostics complete.
pause
