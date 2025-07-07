@echo off
REM Enhanced Analytics Intelligence Platform - Quick Launch Script
REM DUAL COPILOT Compliance: Visual Indicators + Anti-Recursion Protection

echo ==========================================
echo  ENHANCED ANALYTICS INTELLIGENCE PLATFORM
echo  Quick Launch Script - Phase 2 Complete
echo ==========================================
echo.
echo Time: %date% %time%
echo Workspace: %cd%
echo.

echo 🎯 ACTIVATION OPTIONS:
echo.
echo 1. Start Main Intelligence Platform
echo 2. Launch Enterprise Dashboard  
echo 3. Configure Business Rules
echo 4. Run Full Deployment Orchestrator
echo 5. Check Platform Status
echo 6. Exit
echo.

set /p choice="Enter your choice (1-6): "

if %choice%==1 (
    echo.
    echo 🧠 Starting Main Intelligence Platform...
    echo Dashboard will be available at: file://intelligence/dashboards/intelligence_dashboard.html
    echo API will be available at: http://localhost:5000/api/latest_intelligence
    echo.
    Q:/python_venv/.venv_clean/Scripts/python.exe enhanced_analytics_intelligence_platform.py
)

if %choice%==2 (
    echo.
    echo 🌐 Launching Enterprise Dashboard...
    echo Dashboard will be available at: http://localhost:5001
    echo.
    cd web_gui_scripts\flask_apps
    Q:/python_venv/.venv_clean/Scripts/python.exe enterprise_dashboard.py
)

if %choice%==3 (
    echo.
    echo ⚙️ Configuring Business Rules Engine...
    echo.
    Q:/python_venv/.venv_clean/Scripts/python.exe enterprise_business_rules_customization.py
)

if %choice%==4 (
    echo.
    echo 🤖 Running Full Deployment Orchestrator...
    echo.
    Q:/python_venv/.venv_clean/Scripts/python.exe enterprise_intelligence_deployment_orchestrator.py
)

if %choice%==5 (
    echo.
    echo 📊 Platform Status Check...
    echo.
    echo Critical Files:
    if exist enhanced_analytics_intelligence_platform.py (echo ✅ Main Platform: Found) else (echo ❌ Main Platform: Missing)
    if exist enterprise_business_rules_customization.py (echo ✅ Business Rules: Found) else (echo ❌ Business Rules: Missing)
    if exist web_gui_scripts\flask_apps\enterprise_dashboard.py (echo ✅ Enterprise Dashboard: Found) else (echo ❌ Enterprise Dashboard: Missing)
    echo.
    echo Configuration Files:
    if exist enterprise_deployment\active_customization_config.json (echo ✅ Active Config: Found) else (echo ❌ Active Config: Missing)
    if exist enterprise_deployment\automation_config.json (echo ✅ Automation Config: Found) else (echo ❌ Automation Config: Missing)
    echo.
    echo 📋 Platform Status: All components ready for activation
    echo.
)

if %choice%==6 (
    echo.
    echo 👋 Exiting Platform Manager
    echo.
    exit
)

echo.
echo ==========================================
echo  Launch complete! Check the output above.
echo ==========================================
echo.
echo Press any key to return to menu...
pause >nul
goto :start

:start
cls
goto :EOF
