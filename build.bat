@echo off
REM =====================================================
REM Build script for Windows
REM =====================================================

echo ========================================
echo 🚀 UDA Auto Grader - Build Script
echo    Platform: Windows
echo ========================================

REM Change to script directory
cd /d "%~dp0"

REM Check Python
echo.
echo 📦 Kiem tra Python...
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python khong duoc cai dat!
    echo    Vui long tai Python tu: https://www.python.org/downloads/
    pause
    exit /b 1
)

python --version
echo    ✅ Python OK

REM Install dependencies
echo.
echo 📦 Cai dat dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo ❌ Loi cai dat dependencies!
    pause
    exit /b 1
)

REM Run build script
echo.
echo 🔨 Bat dau build...
python build.py

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo ✅ BUILD THANH CONG!
    echo ========================================
    echo.
    echo 📦 File output: %cd%\dist\UDA_Auto_Grader.exe
    echo.
    echo 📋 De chay ung dung:
    echo    dist\UDA_Auto_Grader.exe
) else (
    echo.
    echo ❌ BUILD THAT BAI!
)

echo.
pause
