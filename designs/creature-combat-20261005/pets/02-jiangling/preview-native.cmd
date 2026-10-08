@echo off
setlocal
set "JIANG_PY=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\pythonw.exe"
if exist "%JIANG_PY%" (
  start "" "%JIANG_PY%" -B "%~dp0tools\preview_native.py"
  exit /b
)
python -B "%~dp0tools\preview_native.py"
if errorlevel 1 pause
