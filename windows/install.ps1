#Requires -Version 5.1
<#
.SYNOPSIS
  Install screen-speak for Windows (region OCR + local Piper TTS).

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File .\windows\install.ps1
#>
param(
  [switch]$SkipWinget,
  [switch]$SkipHotkeys,
  [string]$InstallDir = $(Join-Path $env:LOCALAPPDATA "screen-speak")
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path

function Write-Step([string]$Message) {
  Write-Host "==> $Message" -ForegroundColor Cyan
}

function Test-Command([string]$Name) {
  return [bool](Get-Command $Name -ErrorAction SilentlyContinue)
}

function Install-WingetPackage([string]$Id, [string]$Name) {
  if ($SkipWinget) { return }
  if (-not (Test-Command "winget")) {
    Write-Warning "winget not found; install $Name manually if missing."
    return
  }
  Write-Step "winget: $Name ($Id)"
  & winget install --id $Id -e --accept-package-agreements --accept-source-agreements --disable-interactivity
  # 0 = ok, -1978335189 = already installed
  if ($LASTEXITCODE -and $LASTEXITCODE -ne -1978335189 -and $LASTEXITCODE -ne -1978335135) {
    Write-Warning "winget exited $LASTEXITCODE for $Id (continuing)"
  }
}

function Refresh-Path {
  $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" +
              [System.Environment]::GetEnvironmentVariable("Path", "User")
}

function Resolve-Python {
  Refresh-Path
  foreach ($name in @("python", "python3")) {
    $cmd = Get-Command $name -ErrorAction SilentlyContinue
    if ($cmd -and $cmd.Source -notmatch "WindowsApps\\python") {
      return $cmd.Source
    }
  }
  $py = Get-Command py -ErrorAction SilentlyContinue
  if ($py) {
    $out = & py -3 -c "import sys; print(sys.executable)" 2>$null
    if ($out) { return $out.Trim() }
  }
  return $null
}

Write-Step "Install directory: $InstallDir"
New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $InstallDir "voices") | Out-Null

Install-WingetPackage "Python.Python.3.12" "Python 3.12"
Install-WingetPackage "UB-Mannheim.TesseractOCR" "Tesseract OCR"
Install-WingetPackage "Gyan.FFmpeg" "FFmpeg (ffplay)"
if (-not $SkipHotkeys) {
  Install-WingetPackage "AutoHotkey.AutoHotkey" "AutoHotkey"
}

$PythonExe = Resolve-Python
if (-not $PythonExe) {
  throw "Python not found on PATH. Install Python 3 from python.org (check 'Add to PATH'), then re-run."
}
Write-Step "Using Python: $PythonExe"

Write-Step "Copy scripts"
Copy-Item -Force (Join-Path $Root "screen_speak.py") (Join-Path $InstallDir "screen_speak.py")
Copy-Item -Force (Join-Path $Root "screen_speak_stop.py") (Join-Path $InstallDir "screen_speak_stop.py")
Copy-Item -Force (Join-Path $Root "screen_speak_prep.py") (Join-Path $InstallDir "screen_speak_prep.py")
Copy-Item -Force (Join-Path $Root "ScreenSpeak.ahk") (Join-Path $InstallDir "ScreenSpeak.ahk")
Copy-Item -Force (Join-Path $Root "requirements.txt") (Join-Path $InstallDir "requirements.txt")

Write-Step "Python packages (piper-tts, pillow, pytesseract)"
& $PythonExe -m pip install --upgrade pip
& $PythonExe -m pip install -r (Join-Path $InstallDir "requirements.txt")

$VoiceDir = Join-Path $InstallDir "voices"
Write-Step "Download Piper voice en_GB-northern_english_male-medium"
& $PythonExe -m piper.download_voices en_GB-northern_english_male-medium --data-dir $VoiceDir

Write-Step "Write launchers"
$SpeakBat = @"
@echo off
set SCREEN_SPEAK_VOICE_DIR=$VoiceDir
set SCREEN_SPEAK_VOICE=en_GB-northern_english_male-medium
"$PythonExe" "%~dp0screen_speak.py" %*
"@
$StopBat = @"
@echo off
"$PythonExe" "%~dp0screen_speak_stop.py" %*
"@
Set-Content -Path (Join-Path $InstallDir "screen-speak.bat") -Value $SpeakBat -Encoding ASCII
Set-Content -Path (Join-Path $InstallDir "screen-speak-stop.bat") -Value $StopBat -Encoding ASCII

Write-Step "Add install dir to user PATH"
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if (-not $userPath) { $userPath = "" }
if ($userPath -notlike "*$InstallDir*") {
  [Environment]::SetEnvironmentVariable("Path", ($userPath.TrimEnd(";") + ";" + $InstallDir), "User")
  $env:Path += ";$InstallDir"
}

$StartMenu = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\screen-speak"
New-Item -ItemType Directory -Force -Path $StartMenu | Out-Null
$Wsh = New-Object -ComObject WScript.Shell
$sc = $Wsh.CreateShortcut((Join-Path $StartMenu "Speak selection.lnk"))
$sc.TargetPath = Join-Path $InstallDir "screen-speak.bat"
$sc.WorkingDirectory = $InstallDir
$sc.Save()
$sc2 = $Wsh.CreateShortcut((Join-Path $StartMenu "Stop speaking.lnk"))
$sc2.TargetPath = Join-Path $InstallDir "screen-speak-stop.bat"
$sc2.WorkingDirectory = $InstallDir
$sc2.Save()

if (-not $SkipHotkeys) {
  Write-Step "Register AutoHotkey hotkeys at login"
  $Startup = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\Startup"
  $AhkSrc = Join-Path $InstallDir "ScreenSpeak.ahk"
  $AhkLink = Join-Path $Startup "ScreenSpeak.ahk"
  Copy-Item -Force $AhkSrc $AhkLink

  $AhkExe = $null
  foreach ($p in @(
      (Join-Path ${env:ProgramFiles} "AutoHotkey\v2\AutoHotkey64.exe"),
      (Join-Path ${env:ProgramFiles} "AutoHotkey\AutoHotkey.exe"),
      (Join-Path ${env:LocalAppData} "Programs\AutoHotkey\AutoHotkey64.exe")
    )) {
    if (Test-Path $p) { $AhkExe = $p; break }
  }
  if ($AhkExe) {
    Start-Process -FilePath $AhkExe -ArgumentList "`"$AhkLink`""
    Write-Host "Hotkeys active: Ctrl+Shift+PrintScreen (speak), Ctrl+Shift+Backspace (stop)"
  } else {
    Write-Warning "AutoHotkey not found; open $AhkLink manually after installing AHK."
  }
}

Write-Step "Self-check"
& $PythonExe (Join-Path $InstallDir "screen_speak.py") --check

Write-Host ""
Write-Host "Done. Installed to $InstallDir" -ForegroundColor Green
Write-Host "  Speak:  Ctrl+Shift+PrintScreen   (or Start Menu → screen-speak)"
Write-Host "  Stop:   Ctrl+Shift+Backspace"
Write-Host "Open a new terminal if PATH was just updated."
