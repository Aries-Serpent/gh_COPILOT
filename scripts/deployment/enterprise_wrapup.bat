@echo off
REM 🚀 ENTERPRISE CHAT SESSION WRAP-UP BATCH SCRIPT
REM Windows Batch Interface for Enterprise Wrap-Up CLI

echo.
echo ==========================================
echo 🚀 ENTERPRISE CHAT SESSION WRAP-UP CLI
echo ==========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Set default values
set MODE=standard
set WORKSPACE=%cd%
set FORCE_CLEANUP=false
set VALIDATE_ONLY=false

REM Parse command line arguments
:parse_args
if "%~1"=="" goto end_parse
if /i "%~1"=="--mode" (
    set MODE=%~2
    shift
    shift
    goto parse_args
)
if /i "%~1"=="--workspace" (
    set WORKSPACE=%~2
    shift
    shift
    goto parse_args
)
if /i "%~1"=="--force-cleanup" (
    set FORCE_CLEANUP=true
    shift
    goto parse_args
)
if /i "%~1"=="--validate-only" (
    set VALIDATE_ONLY=true
    shift
    goto parse_args
)
if /i "%~1"=="--help" (
    goto show_help
)
shift
goto parse_args

:end_parse

REM Display configuration
echo 📊 WRAP-UP CONFIGURATION:
echo    Mode: %MODE%
echo    Workspace: %WORKSPACE%
echo    Force Cleanup: %FORCE_CLEANUP%
echo    Validate Only: %VALIDATE_ONLY%
echo.

REM Change to workspace directory
cd /d "%WORKSPACE%"

REM Build Python command
set PYTHON_CMD=python enterprise_chat_wrapup_cli.py --mode %MODE% --workspace "%WORKSPACE%"

if /i "%FORCE_CLEANUP%"=="true" (
    set PYTHON_CMD=%PYTHON_CMD% --force-cleanup
)

if /i "%VALIDATE_ONLY%"=="true" (
    set PYTHON_CMD=%PYTHON_CMD% --validate-only
)

REM Execute wrap-up
echo 🚀 EXECUTING ENTERPRISE WRAP-UP...
echo Command: %PYTHON_CMD%
echo.

%PYTHON_CMD%

REM Check exit code
if %errorlevel% equ 0 (
    echo.
    echo ✅ ENTERPRISE WRAP-UP COMPLETED SUCCESSFULLY
    echo.
) else (
    echo.
    echo ❌ ENTERPRISE WRAP-UP FAILED WITH ERROR CODE: %errorlevel%
    echo.
)

REM Instruction set suggestions
echo 🎯 INSTRUCTION SET SUGGESTIONS:
echo.
python intelligent_instruction_orchestrator.py --task-type session_management --capabilities cleanup validation --analytics 2>nul
if %errorlevel% neq 0 (
    echo    Instruction orchestrator not available
    echo    Using default instruction sets for session management
)

echo.
echo 📊 WRAP-UP PROCESS COMPLETE
echo Check generated reports for detailed results
echo.

pause
goto :eof

:show_help
echo.
echo 🚀 ENTERPRISE CHAT SESSION WRAP-UP CLI
echo.
echo Usage: %~nx0 [OPTIONS]
echo.
echo Options:
echo   --mode MODE           Wrap-up mode: standard, enterprise, emergency, full
echo   --workspace PATH      Workspace root directory
echo   --force-cleanup       Force cleanup of all processes
echo   --validate-only       Run validation only (no cleanup)
echo   --help               Show this help message
echo.
echo Examples:
echo   %~nx0 --mode standard
echo   %~nx0 --mode enterprise --workspace "C:\Projects\MyProject"
echo   %~nx0 --mode emergency --force-cleanup
echo   %~nx0 --validate-only
echo.
goto :eof
