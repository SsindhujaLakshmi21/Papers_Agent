@echo off
REM ==============================================================================
REM Run Daily CS Research Papers Digest Workflow
REM ==============================================================================

cd /d "%~dp0"
echo Starting Daily CS Papers Agent Workflow at %date% %time%...

python main.py

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Workflow exited with error code %ERRORLEVEL%
    exit /b %ERRORLEVEL%
)

echo [SUCCESS] Workflow finished successfully!
exit /b 0
