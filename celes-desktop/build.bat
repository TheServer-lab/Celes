@echo off
setlocal
set "DIR=%~dp0"

echo ── Celes Desktop Build ──────────────────────────────
echo.

:: Step 1 — Install dependencies
echo [1/3] Installing dependencies...
py -3.13 -m pip install -r "%DIR%requirements.txt"
if errorlevel 1 (
    echo ERROR: pip install failed.
    pause & exit /b 1
)

:: Step 2 — Clean old build
echo [2/3] Cleaning previous build...
if exist "%DIR%dist\Celes.exe" del /f /q "%DIR%dist\Celes.exe"
if exist "%DIR%build" rmdir /s /q "%DIR%build"

:: Step 3 — Build exe (pass full paths so working dir doesn't matter)
echo [3/3] Building Celes.exe...
py -3.13 -m PyInstaller "%DIR%celes-desktop.spec" --distpath "%DIR%dist" --workpath "%DIR%build" --clean --noconfirm

if errorlevel 1 (
    echo.
    echo ERROR: Build failed. See output above.
    pause & exit /b 1
)

echo.
echo ── Build complete! ──────────────────────────────────
echo Output: %DIR%dist\Celes.exe
echo.
pause