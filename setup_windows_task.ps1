# ==============================================================================
# PowerShell Script to register Windows Scheduled Task for Daily CS Papers
# Runs every day at 7:00 AM IST with missed-start catch-up enabled.
# ==============================================================================

$TaskName = "DailyCSPapersDigest"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ActionScript = Join-Path $ScriptDir "run_workflow.bat"

Write-Host "Registering Scheduled Task: $TaskName" -ForegroundColor Cyan
Write-Host "Target Script: $ActionScript" -ForegroundColor Gray

# 1. Action: execute batch script
$Action = New-ScheduledTaskAction -Execute $ActionScript -WorkingDirectory $ScriptDir

# 2. Trigger: Daily at 7:00 AM
$Trigger = New-ScheduledTaskTrigger -Daily -At 7:00AM

# 3. Settings: Enable catch-up (StartWhenAvailable) so if laptop was off at 7:00 AM, it runs when turned on!
$Settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Minutes 30)

# 4. Register Task
try {
    # Unregister existing if present
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
    
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Description "Daily automated CS research papers digest email to s.sindhu210506@gmail.com"
    Write-Host "`n[SUCCESS] Task '$TaskName' registered successfully!" -ForegroundColor Green
    Write-Host "Scheduled to run daily at 7:00 AM IST." -ForegroundColor Green
    Write-Host "Catch-up enabled: If your laptop is turned off at 7:00 AM, it will automatically run when you turn it on." -ForegroundColor Yellow
} catch {
    Write-Host "`n[ERROR] Failed to register scheduled task: $_" -ForegroundColor Red
    Write-Host "Tip: Run PowerShell as Administrator to register scheduled tasks." -ForegroundColor Yellow
}
