@echo off
REM === CoAI Agent Master Script ===
REM Diagnostics + Repair + Python modules + STATUS.md + GitHub Sync
REM Includes safeguard: auto-stage + auto-commit before pull

cd /d "%~dp0"

echo [CoAI Agent] Starting master run...

:: Ensure logs directory exists
if not exist logs mkdir logs

:: === Diagnostics ===
echo [%date% %time%] Checking Python installation... >> logs\diagnostic.log
python --version >> logs\diagnostic.log 2>&1

echo [%date% %time%] Checking port conflicts (80, 3306)... >> logs\diagnostic.log
netstat -ano | findstr :80 >> logs\diagnostic.log
netstat -ano | findstr :3306 >> logs\diagnostic.log

:: === Real Repair Routines ===
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :80') do (
    echo [%date% %time%] Killing PID %%a (port 80 conflict) >> logs\repair.log
    taskkill /PID %%a /F
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3306') do (
    echo [%date% %time%] Killing PID %%a (port 3306 conflict) >> logs\repair.log
    taskkill /PID %%a /F
)

:: Restart Apache/MySQL (requires Admin, adjust service names!)
echo [%date% %time%] Restarting Apache/MySQL... >> logs\repair.log
net stop Apache
net start Apache
net stop mysql
net start mysql

:: === Python Module Hooks ===
echo Running Python modules...

python scripts\co_troubleshoot.py >> logs\diagnostic.log 2>&1
python scripts\co_fuelcalc.py >> logs\diagnostic.log 2>&1
python scripts\co_proposal.py >> logs\diagnostic.log 2>&1
python scripts\co_scriptgen.py >> logs\diagnostic.log 2>&1
python scripts\co_seo.py >> logs\diagnostic.log 2>&1
python scripts\co_badge.py >> logs\diagnostic.log 2>&1

echo === Python modules executed ===

:: === STATUS.md Auto-Update ===
echo # Agent Status > STATUS.md
echo Last run: %date% %time% >> STATUS.md

findstr /C:"Port conflict detected" logs\diagnostic.log >nul
if %errorlevel%==0 (
    echo Status: Issues detected >> STATUS.md
) else (
    echo Status: Healthy >> STATUS.md
)

echo === STATUS.md updated ===

:: === Git Safeguard: Auto-stage + Auto-commit ===
if exist logs\seo.log git add logs\seo.log
git add STATUS.md logs\diagnostic.log logs\repair.log co_check_agent.bat
git add scripts\*.py
git commit -m "Auto-commit: agent run updates" || echo No changes to commit

:: === Git Sync Automation ===
git pull origin main --rebase
git push origin main

echo === CoAI Agent master sync complete ===
pause
