@echo off
setlocal

set PYTHONPATH=src

echo Running runtime invariant tests...
python tests\run_runtime_invariants.py 2>&1
if errorlevel 1 exit /b %errorlevel%

echo.
echo Running hosted Tk tests...
python guitests\test_runtime_hosted.py 2>&1
if errorlevel 1 exit /b %errorlevel%

echo.
echo All TkMachina tests passed.
