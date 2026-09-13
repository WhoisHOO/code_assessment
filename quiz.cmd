@echo off
rem Windows launcher for the quiz CLI. All arguments pass through:
rem   quiz.cmd -l java -n 5 -d medium
setlocal
cd /d "%~dp0"
where python >nul 2>nul
if %errorlevel%==0 (
    python -m quiz %*
) else (
    py -m quiz %*
)
endlocal
