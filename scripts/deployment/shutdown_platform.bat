@echo off
REM Graceful Shutdown CLI - Windows Batch Interface
REM DUAL COPILOT Compliance: Visual Indicators + Anti-Recursion Protection

echo ==========================================
echo  GRACEFUL SHUTDOWN CLI
echo  Enhanced Analytics Intelligence Platform
echo ==========================================
echo.
echo Time: %date% %time%
echo Workspace: %cd%
echo.

echo 🔄 SHUTDOWN OPTIONS:
echo.
echo 1. Standard Graceful Shutdown (Recommended)
echo 2. Force Shutdown (Skip warnings)
echo 3. Quick Shutdown (Skip state preservation)
echo 4. Check Platform Status
echo 5. Exit (Cancel)
echo.

set /p choice="Enter your choice (1-5): "

if %choice%==1 (
    echo.
    echo 🔄 Executing Standard Graceful Shutdown...
    echo ⚠️  This will stop the 24/7 monitoring system gracefully
    echo 💾 System state will be preserved for restart
    echo.
    set /p confirm="Continue? (y/N): "
    if /i "%confirm%"=="y" (
        Q:/python_venv/.venv_clean/Scripts/python.exe graceful_shutdown.py
    ) else (
        echo ❌ Shutdown cancelled
    )
)

if %choice%==2 (
    echo.
    echo ⚠️  Executing Force Shutdown...
    echo 🚨 This will force shutdown even with warnings
    echo.
    set /p confirm="Are you sure? (y/N): "
    if /i "%confirm%"=="y" (
        Q:/python_venv/.venv_clean/Scripts/python.exe graceful_shutdown.py --force
    ) else (
        echo ❌ Shutdown cancelled
    )
)

if %choice%==3 (
    echo.
    echo ⚡ Executing Quick Shutdown...
    echo 🔄 Skipping state preservation for faster shutdown
    echo.
    set /p confirm="Continue? (y/N): "
    if /i "%confirm%"=="y" (
        Q:/python_venv/.venv_clean/Scripts/python.exe graceful_shutdown.py --skip-state
    ) else (
        echo ❌ Shutdown cancelled
    )
)

if %choice%==4 (
    echo.
    echo 📊 Checking Platform Status...
    echo.
    Q:/python_venv/.venv_clean/Scripts/python.exe graceful_shutdown.py --status
    echo.
)

if %choice%==5 (
    echo.
    echo 👋 Shutdown cancelled by user
    echo.
    goto end
)

echo.
echo ==========================================
echo  Shutdown operation complete
echo ==========================================
echo.

:end
echo Press any key to exit...
pause >nul
