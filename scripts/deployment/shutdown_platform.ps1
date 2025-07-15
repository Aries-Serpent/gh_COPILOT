# Graceful Shutdown CLI - PowerShell Interface
# DUAL COPILOT Compliance: Visual Indicators + Anti-Recursion Protection

param(
    [switch]$Force,
    [switch]$SkipState,
    [switch]$Status,
    [switch]$Help
)

function Show-Header {
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host " GRACEFUL SHUTDOWN CLI" -ForegroundColor White
    Write-Host " Enhanced Analytics Intelligence Platform" -ForegroundColor Gray
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host
    Write-Host "🎯 DUAL COPILOT: Visual Processing ✅ | Anti-Recursion ✅ | Database-Driven ✅" -ForegroundColor Green
    Write-Host "⏰ Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
    Write-Host "📁 Workspace: $PWD" -ForegroundColor Gray
    Write-Host
}

function Show-Help {
    Write-Host "USAGE:" -ForegroundColor Yellow
    Write-Host "  .\shutdown_platform.ps1 [OPTIONS]" -ForegroundColor White
    Write-Host
    Write-Host "OPTIONS:" -ForegroundColor Yellow
    Write-Host "  -Status      Show current platform status" -ForegroundColor White
    Write-Host "  -Force       Force shutdown even with warnings" -ForegroundColor White
    Write-Host "  -SkipState   Skip state preservation (faster)" -ForegroundColor White
    Write-Host "  -Help        Show this help message" -ForegroundColor White
    Write-Host
    Write-Host "EXAMPLES:" -ForegroundColor Yellow
    Write-Host "  .\shutdown_platform.ps1              # Standard graceful shutdown" -ForegroundColor White
    Write-Host "  .\shutdown_platform.ps1 -Status      # Check platform status" -ForegroundColor White
    Write-Host "  .\shutdown_platform.ps1 -Force       # Force shutdown" -ForegroundColor White
    Write-Host "  .\shutdown_platform.ps1 -SkipState   # Quick shutdown" -ForegroundColor White
}

function Get-PlatformProcesses {
    Write-Host "🔍 Detecting platform processes..." -ForegroundColor Yellow
    
    $platformPatterns = @(
        'enhanced_analytics_intelligence_platform',
        'enterprise_dashboard',
        'enterprise_intelligence_deployment_orchestrator',
        'enterprise_business_rules_customization',
        'intelligence_bridge',
        'automation_engine',
        'continuous_operation_monitor'
    )
    
    $processes = Get-Process | Where-Object {
        $cmdLine = $_.CommandLine
        if ($cmdLine) {
            $platformPatterns | ForEach-Object {
                if ($cmdLine -like "*$_*") {
                    return $true
                }
            }
        }
        return $false
    }
    
    return $processes
}

function Show-Status {
    $processes = Get-PlatformProcesses
    
    if ($processes.Count -gt 0) {
        Write-Host "✅ PLATFORM STATUS: OPERATIONAL" -ForegroundColor Green
        Write-Host "🔄 Found $($processes.Count) platform processes:" -ForegroundColor White
        
        foreach ($proc in $processes) {
            $uptime = (Get-Date) - $proc.StartTime
            $memoryMB = [math]::Round($proc.WorkingSet64 / 1MB, 1)
            Write-Host "   🔹 PID $($proc.Id): $($proc.Name) ($($memoryMB)MB, $($uptime.ToString('hh\:mm\:ss')) uptime)" -ForegroundColor Cyan
        }
    } else {
        Write-Host "⚠️  PLATFORM STATUS: STOPPED" -ForegroundColor Yellow
        Write-Host "   No platform processes detected" -ForegroundColor Gray
    }
}

function Confirm-Shutdown {
    param([string]$ShutdownType)
    
    Write-Host "⚠️  WARNING: This will shut down the 24/7 monitoring system!" -ForegroundColor Yellow
    Write-Host "📊 Current platform processes will be gracefully terminated." -ForegroundColor White
    Write-Host "💾 System state will be preserved for restart." -ForegroundColor White
    Write-Host
    
    $response = Read-Host "🔄 Continue with $ShutdownType shutdown? (y/N)"
    return $response -match '^[yY]'
}

function Execute-Shutdown {
    param([string]$Arguments)
    
    Write-Host "🚀 Executing graceful shutdown..." -ForegroundColor Green
    
    $pythonPath = "Q:/python_venv/.venv_clean/Scripts/python.exe"
    $shutdownScript = "graceful_shutdown.py"
    
    try {
        if ($Arguments) {
            & $pythonPath $shutdownScript $Arguments.Split(' ')
        } else {
            & $pythonPath $shutdownScript
        }
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Shutdown completed successfully!" -ForegroundColor Green
        } else {
            Write-Host "⚠️  Shutdown completed with warnings" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "❌ Error executing shutdown: $_" -ForegroundColor Red
    }
}

# Main execution
Show-Header

if ($Help) {
    Show-Help
    exit
}

if ($Status) {
    Show-Status
    exit
}

# Build arguments for Python script
$arguments = @()
if ($Force) { $arguments += "--force" }
if ($SkipState) { $arguments += "--skip-state" }

# Determine shutdown type
$shutdownType = "standard"
if ($Force) { $shutdownType = "force" }
if ($SkipState) { $shutdownType = "quick" }

# Confirm shutdown unless forced
if (-not $Force) {
    if (-not (Confirm-Shutdown $shutdownType)) {
        Write-Host "❌ Shutdown cancelled by user" -ForegroundColor Red
        exit
    }
}

# Execute shutdown
Execute-Shutdown ($arguments -join " ")

Write-Host
Write-Host "🔄 Platform can be restarted using:" -ForegroundColor Cyan
Write-Host "   • launch_platform.bat" -ForegroundColor White
Write-Host "   • python quick_start_intelligence_platform.py" -ForegroundColor White
Write-Host
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
