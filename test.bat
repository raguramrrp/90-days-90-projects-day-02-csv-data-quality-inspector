@echo off
setlocal

echo ======================================================================
echo    Running Automated Test Suite - Dataset Quality & Profiling Engine
echo ======================================================================

if not exist .venv\Scripts\pytest.exe (
    echo [ERROR] Virtual environment or pytest not found.
    echo Please run setup.bat first.
    exit /b 1
)

echo Executing pytest suite across parser, validator, profiler, quality engine and reports...
echo.

.\.venv\Scripts\pytest -v --tb=short

if %errorlevel% neq 0 (
    echo.
    echo [FAIL] One or more automated tests failed.
    exit /b %errorlevel%
)

echo.
echo [PASS] All automated tests passed successfully!
exit /b 0
