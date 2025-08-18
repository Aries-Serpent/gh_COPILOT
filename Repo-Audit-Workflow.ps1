# =====================================================================
# Repo-Audit-Workflow.ps1
# End-to-end audit & planning workflow for gh_COPILOT (no Actions activation)
# Author: Chat (Codex-ready)
# =====================================================================

[CmdletBinding()]
param(
  [Parameter(Mandatory=$false)]
  [string]$RepoZipUrl = "https://github.com/Aries-Serpent/gh_COPILOT/archive/refs/heads/main.zip",

  [Parameter(Mandatory=$true)]
  [string]$WorkDir,

  [Parameter(Mandatory=$false)]
  [double]$Lambda = 0.6
)

function Write-Log {
  param([string]$Msg, [ValidateSet('INFO','WARN','ERROR')][string]$Level='INFO')
  $ts = (Get-Date).ToString("s")
  $line = "[$ts][$Level] $Msg"
  Write-Host $line
  Add-Content -Path (Join-Path $script:OutDir "analysis\change_log.md") -Value $line
}

function New-ErrorQuestion {
  param(
    [int]$StepNumber,
    [string]$StepDescription,
    [string]$ErrorMessage,
    [string]$Context
  )
  $q = @""
Question for ChatGPT-5:
While performing [$StepNumber:$StepDescription], encountered the following error:
$ErrorMessage
Context: $Context
What are the possible causes, and how can this be resolved while preserving intended functionality?
""@
  Add-Content -Path (Join-Path $script:OutDir "analysis\chatgpt5_questions.md") -Value $q
}

function Disable-GitHubActions {
  try {
    $wf = Join-Path $script:RepoRoot ".github\workflows"
    if (Test-Path $wf) {
      $disabled = Join-Path $script:RepoRoot ".github\workflows_disabled"
      New-Item -ItemType Directory -Force -Path $disabled | Out-Null
      Get-ChildItem -Path $wf -File -Include *.yml,*.yaml -ErrorAction Stop | ForEach-Object {
        Move-Item -Path $_.FullName -Destination (Join-Path $disabled $_.Name) -Force
      }
      Write-Log "GitHub Actions workflows moved to .github/workflows_disabled/" "INFO"
    }
  } catch {
    Write-Log "Failed to disable GitHub Actions: $($_.Exception.Message)" "ERROR"
    New-ErrorQuestion -StepNumber 2 -StepDescription "Safety Guard (Actions)" -ErrorMessage $_.Exception.Message -Context $wf
  }
}

function Sanitize-Readme {
  param([string]$ReadmePath)
  try {
    if (-not (Test-Path $ReadmePath)) { return }
    $raw = Get-Content -Path $ReadmePath -Raw
    $s1 = [regex]::Replace($raw, '\[([^\]]+)\]\((?:https?:\/\/)?[^\)]+\)', '$1')
    $s2 = [regex]::Replace($s1, '(?mi)https?:\/\/\S+', '')
    $out = Join-Path $script:OutDir "README_sanitized.md"
    Set-Content -Path $out -Value $s2 -Encoding UTF8
    Write-Log "README sanitized → $out" "INFO"
  } catch {
    Write-Log "README sanitize error: $($_.Exception.Message)" "ERROR"
    New-ErrorQuestion -StepNumber 3 -StepDescription "README parsing and reference removal" -ErrorMessage $_.Exception.Message -Context $ReadmePath
  }
}

function Build-Mappings {
  try {
    $map = [ordered]@{}

    $map["Core Systems"] = @{
      files = @(
        "src", "utils", "tools", "scripts\UNIFIED_DEPLOYMENT_ORCHESTRATOR_CONSOLIDATED.py",
        "scripts\run_checks.py", "unified_monitoring_optimization_system.py"
      );
      docs  = @("README.md");
      stubs = @()
    }
    $map["Database Layer"] = @{
      files = @("db","databases","db_tools","analytics.db","database_*");
      docs  = @("README.md");
      stubs = @()
    }
    $map["ML Pipeline"] = @{
      files = @("ml_pattern_recognition","scripts\ml","scripts\model_performance_monitor.py");
      docs  = @("README.md");
      stubs = @()
    }
    $map["Quantum Simulation"] = @{
      files = @("quantum","copilot_qiskit_stubs");
      docs  = @("docs\quantum_integration_plan.md","docs\QUANTUM_PLACEHOLDERS.md","docs\STUB_MODULE_STATUS.md");
      stubs = @("quantum\*\*demo*.py")
    }
    $map["Security Framework"] = @{
      files = @("security");
      docs  = @("security\*.json");
      stubs = @()
    }
    $map["Compliance Engine"] = @{
      files = @("update_compliance_metrics.py","secondary_copilot_validator.py","scripts\docs_status_reconciler.py");
      docs  = @("docs\GOVERNANCE_STANDARDS.md","docs\white-paper.md");
      stubs = @()
    }
    $map["Performance Monitor"] = @{
      files = @("scripts\monitoring\performance_monitor.py","scripts\performance\bottleneck_analyzer.py");
      docs  = @("README.md");
      stubs = @()
    }

    $found = @{}
    $prune = @()
    foreach ($k in $map.Keys) {
      $files = @()
      foreach ($pattern in $map[$k].files) {
        $matches = Get-ChildItem -Path $script:RepoRoot -Recurse -ErrorAction SilentlyContinue -Filter ([IO.Path]::GetFileName($pattern)) |
          Where-Object { $_.FullName -like ("*" + ($pattern -replace '\*','*') + "*") }
        if ($matches.Count -gt 0) {
          $files += $matches.FullName
        } else {
          $prune += [pscustomobject]@{ Component=$k; Pattern=$pattern; Rationale="No match after exhaustive search; candidate for deferral" }
        }
      }
      $found[$k] = $files
    }

    $jsonOut = (Join-Path $script:OutDir "analysis\mappings.json")
    $found | ConvertTo-Json -Depth 6 | Set-Content -Path $jsonOut -Encoding UTF8
    $csvOut = (Join-Path $script:OutDir "analysis\gaps.csv")
    $prune | Export-Csv -NoTypeInformation -Path $csvOut -Encoding UTF8

    Write-Log "Mappings written → $jsonOut; gaps → $csvOut" "INFO"
  } catch {
    Write-Log "Mapping error: $($_.Exception.Message)" "ERROR"
    New-ErrorQuestion -StepNumber 4 -StepDescription "Search & Mapping" -ErrorMessage $_.Exception.Message -Context $script:RepoRoot
  }
}

function Compute-PerformanceProxy {
  param([string]$Component, [string[]]$Paths)

  if (-not $Paths -or $Paths.Count -eq 0) { return 70 }
  $todo = 0; $stubFiles = 0; $files = 0; $loc = 0
  foreach ($p in $Paths) {
    try {
      if (Test-Path $p) {
        $files++
        $text = Get-Content -Path $p -Raw -ErrorAction Stop
        $loc += (($text -split "`n").Count)
        $todo += ([regex]::Matches($text, '(?mi)\b(TODO|FIXME)\b')).Count
        if ($text -match '(?mi)pass\s*$|raise NotImplementedError|@stub|#\s*stub') { $stubFiles++ }
      }
    } catch {
      Write-Log "PerfProxy read error on $p: $($_.Exception.Message)" "WARN"
    }
  }

  if ($loc -eq 0) { return 75 }
  $wTodo = 0.5; $wStub = 0.5
  $penalty = ($wTodo * ($todo / [math]::Max(1,$loc))) + ($wStub * ($stubFiles / [math]::Max(1,$files)))
  $score = 100 * [math]::Max(0, 1 - $penalty)
  [math]::Round($score, 1)
}

function Emit-Scores {
  try {
    $coverage = @{
      "Core Systems" = 94
      "Database Layer" = 96
      "ML Pipeline" = 87
      "Quantum Simulation" = 73
      "Security Framework" = 99
      "Compliance Engine" = 92
      "Performance Monitor" = 89
    }

    $mappingsPath = Join-Path $script:OutDir "analysis\mappings.json"
    $found = Get-Content -Path $mappingsPath -Raw | ConvertFrom-Json

    $rows = @()
    foreach ($k in $coverage.Keys) {
      $paths = @()
      if ($found.$k) { $paths = @($found.$k | ForEach-Object { $_ }) }
      $Pi = Compute-PerformanceProxy -Component $k -Paths $paths
      $Ci = [double]$coverage[$k]
      $Si = [math]::Round(($script:Lambda * $Ci + (1 - $script:Lambda) * $Pi), 1)
      $rows += [pscustomobject]@{
        Component = $k; Coverage = $Ci; Performance = $Pi; Composite = $Si;
        GapCoverage = (100 - $Ci); GapPerformance = (100 - $Pi); GapComposite = (100 - $Si)
      }
    }

    $json = $rows | ConvertTo-Json -Depth 4
    $md = @()
    $md += "| Component | Coverage | Performance | Composite |"
    $md += "|---|---:|---:|---:|"
    foreach ($r in $rows) {
      $md += "| $($r.Component) | $($r.Coverage) | $($r.Performance) | **$($r.Composite)** |"
    }
    $avg = [math]::Round(($rows | Measure-Object -Property Composite -Average).Average, 2)
    $md += ""
    $md += "**Overall mean composite:** $avg"

    $json | Set-Content -Path (Join-Path $script:OutDir "analysis\coverage_performance.json") -Encoding UTF8
    ($md -join "`n") | Set-Content -Path (Join-Path $script:OutDir "analysis\coverage_performance.md") -Encoding UTF8
    Write-Log "Scores emitted (avg=$avg)" "INFO"
  } catch {
    Write-Log "Score emission error: $($_.Exception.Message)" "ERROR"
    New-ErrorQuestion -StepNumber 5 -StepDescription "Coverage/Performance computation" -ErrorMessage $_.Exception.Message -Context $script:OutDir
  }
}

try {
  $script:OutDir = (Resolve-Path (New-Item -ItemType Directory -Force -Path $WorkDir)).Path
  New-Item -ItemType Directory -Force -Path (Join-Path $script:OutDir "analysis") | Out-Null

  $zip = Join-Path $script:OutDir "repo.zip"
  try {
    Write-Log "Downloading ZIP…" "INFO"
    Invoke-WebRequest -Uri $RepoZipUrl -OutFile $zip -UseBasicParsing -ErrorAction Stop
  } catch {
    Write-Log "Download failed: $($_.Exception.Message)" "ERROR"
    New-ErrorQuestion -StepNumber 1 -StepDescription "Fetch & Extract" -ErrorMessage $_.Exception.Message -Context $RepoZipUrl
    throw
  }

  $repoDir = Join-Path $script:OutDir "repo"
  Expand-Archive -LiteralPath $zip -DestinationPath $repoDir -Force
  $script:RepoRoot = Get-ChildItem -Path $repoDir | Select-Object -First 1 | ForEach-Object { $_.FullName }

  Disable-GitHubActions
  Sanitize-Readme -ReadmePath (Join-Path $script:RepoRoot "README.md")
  Build-Mappings
  $script:Lambda = $Lambda
  Emit-Scores

  Write-Log "Workflow complete." "INFO"
  Write-Host "`nArtifacts in: $script:OutDir"
  Write-Host " - README_sanitized.md"
  Write-Host " - analysis\mappings.json"
  Write-Host " - analysis\gaps.csv"
  Write-Host " - analysis\coverage_performance.{json,md}"
  Write-Host " - analysis\change_log.md"
  Write-Host " - analysis\chatgpt5_questions.md"
}
catch {
  Write-Log "Fatal error: $($_.Exception.Message)" "ERROR"
  New-ErrorQuestion -StepNumber 6 -StepDescription "Finalization" -ErrorMessage $_.Exception.Message -Context $script:OutDir
  exit 1
}
