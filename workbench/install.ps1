<#
.SYNOPSIS
  One-step setup for the local agent workbench on Windows.

.DESCRIPTION
  1. Checks Python 3.10+.
  2. Installs the workbench and its optional helpers (PDF parsing, key storage) for the current user.
  3. Checks for Ollama. If it is missing, asks before installing it with winget.
  4. Pulls the recommended local model(s) for the chosen task profile.
  5. Sets up the bundled skills and runs the doctor.
  Nothing is sent to a cloud provider. Cloud keys stay optional (python -m lawb keys set ...).

.PARAMETER Profile
  coding, math, literature, general, all, or none. Default: coding.

.PARAMETER Cloud
  Also install the official Anthropic and OpenAI SDKs (cloud stays off until you add a key).

.PARAMETER DryRun
  Print each step without changing anything.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File install.ps1 -Profile literature
#>
param(
  [ValidateSet("coding", "math", "literature", "general", "all", "none")]
  [string]$Profile = "coding",
  [switch]$Cloud,
  [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path

function Step($text) { Write-Host "`n==> $text" -ForegroundColor Cyan }
function Run($exe, [string[]]$argv) {
  Write-Host "    $exe $($argv -join ' ')"
  if (-not $DryRun) {
    & $exe @argv
    if ($LASTEXITCODE -ne 0) { throw "$exe failed with exit code $LASTEXITCODE" }
  }
}

Step "Checking Python 3.10 or later"
$python = $null
foreach ($candidate in @("py", "python")) {
  if (Get-Command $candidate -ErrorAction SilentlyContinue) {
    $args3 = @()
    if ($candidate -eq "py") { $args3 = @("-3") }
    $ver = & $candidate @args3 -c "import sys; print('%d.%d' % sys.version_info[:2])" 2>$null
    if ($ver -and [version]$ver -ge [version]"3.10") { $python = @($candidate) + $args3; break }
  }
}
if (-not $python) { throw "Python 3.10+ not found. Install it from https://www.python.org/downloads/ and re-run." }
Write-Host "    using $($python -join ' ') ($ver)"
$py = $python[0]; $pyArgs = @($python | Select-Object -Skip 1)

Step "Installing the workbench and helpers for the current user"
Run $py ($pyArgs + @("-m", "pip", "install", "--user", "--upgrade", $Root, "pymupdf", "pypdf", "keyring"))
if ($Cloud) { Run $py ($pyArgs + @("-m", "pip", "install", "--user", "--upgrade", "anthropic", "openai")) }

if ($Profile -ne "none") {
  Step "Checking Ollama (local model server)"
  if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
    $answer = if ($DryRun) { "n" } else { Read-Host "Ollama is not installed. Install it now with winget? [y/N]" }
    if ($answer -match '^[Yy]') {
      Run "winget" @("install", "--id", "Ollama.Ollama", "-e", "--accept-source-agreements", "--accept-package-agreements")
      Write-Host "    Ollama installed. If the next step cannot find it, open a new terminal and re-run."
    } else {
      Write-Host "    Skipped. Install Ollama from https://ollama.com/download, then run: python -m lawb models install --task $Profile"
    }
  }
  if (Get-Command ollama -ErrorAction SilentlyContinue) {
    Step "Pulling the recommended model(s) for: $Profile"
    $mArgs = $pyArgs + @("-m", "lawb", "models", "install", "--task", $Profile)
    if ($DryRun) { $mArgs += "--dry-run" }
    & $py @mArgs
  }
}

Step "Setting up the bundled skills"
Run $py ($pyArgs + @("-m", "lawb", "setup"))

Step "Checking the environment"
& $py @($pyArgs + @("-m", "lawb", "doctor"))

Write-Host "`nDone. Try: python -m lawb skills list    and    python -m lawb models recommend" -ForegroundColor Green
