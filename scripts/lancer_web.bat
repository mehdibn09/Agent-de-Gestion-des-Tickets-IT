@echo off
pushd "%~dp0.."
if not exist ".venv\Scripts\python.exe" (
 echo Lancez d'abord scripts\setup.bat
 popd
 exit /b 1
)
start "TicketAssist API" ".venv\Scripts\python.exe" -m ticket_agent serve
start "TicketAssist Interface" ".venv\Scripts\python.exe" -m ticket_agent ui
popd
