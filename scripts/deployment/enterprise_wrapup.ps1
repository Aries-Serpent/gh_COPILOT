# 🚀 ENTERPRISE CHAT SESSION WRAP-UP POWERSHELL SCRIPT
# Advanced PowerShell Interface for Enterprise Wrap-Up CLI

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("standard", "enterprise", "emergency", "full")]
    [string]$Mode = "standard",
    
    [Parameter(Mandatory=$false)]
    [string]$Workspace = (Get-Location).Path,
    
    [Parameter(Mandatory=$false)]
    [switch]$ForceCleanup,
    
    [Parameter(Mandatory=$false)]
    [switch]$ValidateOnly,
    
    [Parameter(Mandatory=$false)]
    [switch]$GenerateReport,
    
    [Parameter(Mandatory=$false)]
    [switch]$ShowAnalytics,
    
    [Parameter(Mandatory=$false)]
    [switch]$Help
)

# Display help if requested
if ($Help) {
    Write-Host ""
    Write-Host "🚀 ENTERPRISE CHAT SESSION WRAP-UP CLI" -ForegroundColor Green
    Write-Host ""
    Write-Host "Usage: .\enterprise_wrapup.ps1 [OPTIONS]" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Parameters:" -ForegroundColor Yellow
    Write-Host "  -Mode             Wrap-up mode: standard, enterprise, emergency, full" -ForegroundColor White
    Write-Host "  -Workspace        Workspace root directory" -ForegroundColor White
    Write-Host "  -ForceCleanup     Force cleanup of all processes" -ForegroundColor White
    Write-Host "  -ValidateOnly     Run validation only (no cleanup)" -ForegroundColor White
    Write-Host "  -GenerateReport   Generate detailed wrap-up report" -ForegroundColor White
    Write-Host "  -ShowAnalytics    Display usage analytics" -ForegroundColor White
    Write-Host "  -Help             Show this help message" -ForegroundColor White
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Yellow
    Write-Host "  .\enterprise_wrapup.ps1 -Mode standard" -ForegroundColor Gray
    Write-Host "  .\enterprise_wrapup.ps1 -Mode enterprise -Workspace 'C:\Projects\MyProject'" -ForegroundColor Gray
    Write-Host "  .\enterprise_wrapup.ps1 -Mode emergency -ForceCleanup" -ForegroundColor Gray
    Write-Host "  .\enterprise_wrapup.ps1 -ValidateOnly -GenerateReport" -ForegroundColor Gray
    Write-Host ""
    exit 0
}

# Function to display banner
function Show-Banner {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host "🚀 ENTERPRISE CHAT SESSION WRAP-UP CLI" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host ""
}

# Function to check prerequisites
function Test-Prerequisites {
    Write-Host "🔍 CHECKING PREREQUISITES..." -ForegroundColor Yellow
    
    # Check Python
    try {
        $pythonVersion = python --version 2>$null
        if ($pythonVersion) {
            Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
        } else {
            throw "Python not found"
        }
    } catch {
        Write-Host "❌ ERROR: Python is not installed or not in PATH" -ForegroundColor Red
        Write-Host "Please install Python 3.8+ and try again" -ForegroundColor Red
        exit 1
    }
    
    # Check if CLI script exists
    $cliScript = Join-Path $Workspace "enterprise_chat_wrapup_cli.py"
    if (-not (Test-Path $cliScript)) {
        Write-Host "❌ ERROR: CLI script not found at $cliScript" -ForegroundColor Red
        exit 1
    } else {
        Write-Host "✅ CLI Script: Found" -ForegroundColor Green
    }
    
    # Check if orchestrator exists
    $orchestratorScript = Join-Path $Workspace "intelligent_instruction_orchestrator.py"
    if (Test-Path $orchestratorScript) {
        Write-Host "✅ Instruction Orchestrator: Available" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Instruction Orchestrator: Not available" -ForegroundColor Yellow
    }
    
    Write-Host ""
}

# Function to display configuration
function Show-Configuration {
    Write-Host "📊 WRAP-UP CONFIGURATION:" -ForegroundColor Cyan
    Write-Host "   Mode: $Mode" -ForegroundColor White
    Write-Host "   Workspace: $Workspace" -ForegroundColor White
    Write-Host "   Force Cleanup: $ForceCleanup" -ForegroundColor White
    Write-Host "   Validate Only: $ValidateOnly" -ForegroundColor White
    Write-Host "   Generate Report: $GenerateReport" -ForegroundColor White
    Write-Host "   Show Analytics: $ShowAnalytics" -ForegroundColor White
    Write-Host ""
}

# Function to execute wrap-up
function Invoke-EnterpriseWrapUp {
    # Change to workspace directory
    Set-Location $Workspace
    
    # Build Python command
    $pythonArgs = @(
        "enterprise_chat_wrapup_cli.py",
        "--mode", $Mode,
        "--workspace", $Workspace
    )
    
    if ($ForceCleanup) {
        $pythonArgs += "--force-cleanup"
    }
    
    if ($ValidateOnly) {
        $pythonArgs += "--validate-only"
    }
    
    if ($GenerateReport) {
        $pythonArgs += "--generate-report"
    }
    
    # Execute wrap-up
    Write-Host "🚀 EXECUTING ENTERPRISE WRAP-UP..." -ForegroundColor Green
    Write-Host "Command: python $($pythonArgs -join ' ')" -ForegroundColor Gray
    Write-Host ""
    
    $startTime = Get-Date
    
    try {
        & python @pythonArgs
        $exitCode = $LASTEXITCODE
        
        $endTime = Get-Date
        $duration = $endTime - $startTime
        
        Write-Host ""
        if ($exitCode -eq 0) {
            Write-Host "✅ ENTERPRISE WRAP-UP COMPLETED SUCCESSFULLY" -ForegroundColor Green
            Write-Host "⏱️  Duration: $($duration.TotalSeconds.ToString('F2')) seconds" -ForegroundColor Cyan
        } else {
            Write-Host "❌ ENTERPRISE WRAP-UP FAILED WITH ERROR CODE: $exitCode" -ForegroundColor Red
            Write-Host "⏱️  Duration: $($duration.TotalSeconds.ToString('F2')) seconds" -ForegroundColor Cyan
        }
        
        return $exitCode
        
    } catch {
        Write-Host "❌ CRITICAL ERROR: $($_.Exception.Message)" -ForegroundColor Red
        return 1
    }
}

# Function to show instruction suggestions
function Show-InstructionSuggestions {
    Write-Host "🎯 INSTRUCTION SET SUGGESTIONS:" -ForegroundColor Cyan
    Write-Host ""
    
    $orchestratorScript = Join-Path $Workspace "intelligent_instruction_orchestrator.py"
    
    if (Test-Path $orchestratorScript) {
        try {
            if ($ShowAnalytics) {
                Write-Host "📊 USAGE ANALYTICS:" -ForegroundColor Yellow
                & python $orchestratorScript --analytics 2>$null
            }
            
            Write-Host "🎯 RECOMMENDATIONS FOR SESSION MANAGEMENT:" -ForegroundColor Yellow
            & python $orchestratorScript --task-type "session_management" --capabilities "cleanup" "validation" "documentation" --generate-command 2>$null
            
        } catch {
            Write-Host "   Instruction orchestrator encountered an error" -ForegroundColor Yellow
            Write-Host "   Using default instruction sets for session management" -ForegroundColor Yellow
        }
    } else {
        Write-Host "   Instruction orchestrator not available" -ForegroundColor Yellow
        Write-Host "   Using default instruction sets for session management" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "   Default Instructions:" -ForegroundColor Gray
        Write-Host "   - COMPREHENSIVE_SESSION_INTEGRITY" -ForegroundColor Gray
        Write-Host "   - AUTONOMOUS_FILE_MANAGEMENT" -ForegroundColor Gray
        Write-Host "   - VISUAL_PROCESSING_INDICATORS" -ForegroundColor Gray
        Write-Host "   - ENTERPRISE_CONTEXT" -ForegroundColor Gray
    }
    
    Write-Host ""
}

# Function to display final summary
function Show-FinalSummary {
    Write-Host "📊 WRAP-UP PROCESS COMPLETE" -ForegroundColor Green
    Write-Host ""
    
    # Check for generated reports
    $reportFiles = Get-ChildItem -Path $Workspace -Filter "WRAPUP_REPORT_*.json" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    
    if ($reportFiles) {
        Write-Host "📄 Generated Reports:" -ForegroundColor Cyan
        Write-Host "   - $($reportFiles.Name)" -ForegroundColor White
        
        # Show brief report summary
        try {
            $reportContent = Get-Content $reportFiles.FullName | ConvertFrom-Json
            Write-Host ""
            Write-Host "📈 SUMMARY:" -ForegroundColor Cyan
            Write-Host "   Status: $($reportContent.status)" -ForegroundColor White
            Write-Host "   Duration: $($reportContent.duration_seconds) seconds" -ForegroundColor White
            Write-Host "   Errors: $($reportContent.errors_count)" -ForegroundColor White
            Write-Host "   Warnings: $($reportContent.warnings_count)" -ForegroundColor White
            Write-Host "   Completed Tasks: $($reportContent.completed_tasks)" -ForegroundColor White
        } catch {
            Write-Host "   Report generated but could not parse summary" -ForegroundColor Yellow
        }
    } else {
        Write-Host "📄 No detailed reports generated" -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "🎯 NEXT STEPS:" -ForegroundColor Cyan
    Write-Host "   1. Review generated reports for detailed results" -ForegroundColor White
    Write-Host "   2. Verify system integrity and cleanup" -ForegroundColor White
    Write-Host "   3. Update documentation if needed" -ForegroundColor White
    Write-Host "   4. Prepare for next session deployment" -ForegroundColor White
    Write-Host ""
}

# Main execution
try {
    Show-Banner
    Test-Prerequisites
    Show-Configuration
    
    $result = Invoke-EnterpriseWrapUp
    
    Show-InstructionSuggestions
    Show-FinalSummary
    
    if ($result -eq 0) {
        Write-Host "🏆 ENTERPRISE WRAP-UP COMPLETED WITH SUCCESS" -ForegroundColor Green
    } else {
        Write-Host "⚠️  ENTERPRISE WRAP-UP COMPLETED WITH WARNINGS" -ForegroundColor Yellow
    }
    
    exit $result
    
} catch {
    Write-Host ""
    Write-Host "❌ CRITICAL ERROR: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Stack Trace:" -ForegroundColor Red
    Write-Host $_.Exception.StackTrace -ForegroundColor Red
    exit 1
}
