@echo off
title Celery Worker
cd /d "%~dp0"
call .venv\Scripts\activate.bat
echo Starting Celery worker ...
celery -A src.celery_tasks.c_app worker --pool=solo -l info
pause
