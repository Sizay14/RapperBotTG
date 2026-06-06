@echo off
:loop
cd /d "D:\RapperBot TG"
python rapbot.py
echo Бот перезапускается...
timeout /t 5
goto loop