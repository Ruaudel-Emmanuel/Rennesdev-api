@echo off
set PYTHON_EXE=C:\Users\Emmanuel\AppData\Local\Microsoft\WindowsApps\python3.9.exe

echo Running tests with: %PYTHON_EXE%
"%PYTHON_EXE%" -m pytest tests\api -v
pause