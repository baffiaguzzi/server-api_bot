@echo off
cd /d "%~dp0"
python -m telegram_bot.telegram_bot
echo.
echo Press anywhere to exit...
pause > nul