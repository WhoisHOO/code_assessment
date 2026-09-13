@echo off
rem Launch the local study UI (daily SRS review, flashcards, quiz,
rem timed problems). Opens the browser at http://127.0.0.1:8765/
setlocal
cd /d "%~dp0"
where python >nul 2>nul
if %errorlevel%==0 (
    python -m quiz.server %*
) else (
    py -m quiz.server %*
)
endlocal
