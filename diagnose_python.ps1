# Diagnose Python PATH issue

Write-Host "=== User PATH ===" -ForegroundColor Cyan
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
$userPath -split ';' | Where-Object { $_ -like "*Python*" }

Write-Host "`n=== System PATH ===" -ForegroundColor Cyan
$systemPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
$systemPath -split ';' | Where-Object { $_ -like "*Python*" }

Write-Host "`n=== Current Session PATH ===" -ForegroundColor Cyan
$env:Path -split ';' | Where-Object { $_ -like "*Python*" }

Write-Host "`n=== Which python ===" -ForegroundColor Cyan
(Get-Command python).Source
(Get-Command python3).Source

Write-Host "`n=== Python Versions ===" -ForegroundColor Cyan
& python --version
& python3 --version
