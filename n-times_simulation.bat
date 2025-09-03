@echo off
:: Change directory to TurnSimulation (relative to batch file)
cd /d "%~dp0TurnSimulation"

:: Create Logs folder if it doesn't exist
if not exist "Logs" mkdir "Logs"

:: Enable delayed expansion
setlocal EnableDelayedExpansion

set SEED_BASE=42

for /l %%x in (1, 1, 100) do (
    echo [%%x/100] Running simulation...

    set /a CURRENT_SEED=SEED_BASE + %%x

    echo CURRENT_SEED=!CURRENT_SEED!
    python battle_fully_commented.py !CURRENT_SEED! > "Logs/simulation_log_%%x.txt" 2>&1

    echo Completed (Seed: !CURRENT_SEED!)
)

echo All 100 simulations finished!
pause