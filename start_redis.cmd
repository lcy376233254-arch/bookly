@echo off
title Redis Server
cd /d "%~dp0Redis-8.8.0-Windows-x64-cygwin-with-Service"
echo Starting Redis on localhost:6379 ...
redis-server.exe redis.conf
pause
