@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "PROJECT_DIR=%SCRIPT_DIR:~0,-1%"
for %%I in ("%PROJECT_DIR%\..") do set "PROJECT_DIR=%%~fI"
set "PROJECT_DIR_WSL=%PROJECT_DIR:\=/%"
set "PROJECT_DIR_WSL=/mnt/c%PROJECT_DIR_WSL:~2%"

set "DEFAULT_MEDIAMTX_PATH=/home/kirataiki/apps/mediamtx"

if /I "%~1"=="__run__" goto :run
if /I "%~1"=="--help" goto :usage
if /I "%~1"=="/?" goto :usage

start "CameraDiary - MediaMTX WSL" cmd /k ""%~f0" __run__ %*"
exit /b 0

:run
shift

set "WSL_DISTRO=%CAMERADIARY_WSL_DISTRO%"
if not "%~1"=="" set "WSL_DISTRO=%~1"

set "MEDIAMTX_PATH=%CAMERADIARY_MEDIAMTX_PATH%"
if "%MEDIAMTX_PATH%"=="" set "MEDIAMTX_PATH=%CAMERADIARY_MEDIAMTX_DIR%"
if not "%~2"=="" set "MEDIAMTX_PATH=%~2"
if "%MEDIAMTX_PATH%"=="" set "MEDIAMTX_PATH=%DEFAULT_MEDIAMTX_PATH%"

title CameraDiary - MediaMTX WSL
set "LAUNCHER_SH=%PROJECT_DIR_WSL%/scripts/start_mediamtx_wsl.sh"

echo ========================================
echo CameraDiary MediaMTX Launcher
echo ========================================
if not "%WSL_DISTRO%"=="" (
  echo WSL distro: %WSL_DISTRO%
  echo MediaMTX path: %MEDIAMTX_PATH%
  echo Log output:
  echo ----------------------------------------
  wsl.exe -d "%WSL_DISTRO%" -- bash "%LAUNCHER_SH%" "%MEDIAMTX_PATH%"
) else (
  echo WSL distro: default
  echo MediaMTX path: %MEDIAMTX_PATH%
  echo Log output:
  echo ----------------------------------------
  wsl.exe -- bash "%LAUNCHER_SH%" "%MEDIAMTX_PATH%"
)

set "EXIT_CODE=%ERRORLEVEL%"
echo ----------------------------------------
if "%EXIT_CODE%"=="0" (
  echo MediaMTX exited normally.
) else (
  echo MediaMTX exited with code %EXIT_CODE%.
)
echo This window will remain open. Close it manually.
exit /b %EXIT_CODE%

:usage
echo Usage:
echo   start_mediamtx_wsl.bat [wsl_distro] [mediamtx_dir]
echo.
echo Examples:
echo   start_mediamtx_wsl.bat
echo   start_mediamtx_wsl.bat Ubuntu
echo   start_mediamtx_wsl.bat Ubuntu /home/kirataiki/apps/mediamtx
echo   start_mediamtx_wsl.bat Ubuntu /home/kirataiki/apps/mediamtx_v1.17.1_linux_amd64
echo.
echo Optional environment variables:
echo   CAMERADIARY_WSL_DISTRO
echo   CAMERADIARY_MEDIAMTX_PATH
echo   CAMERADIARY_MEDIAMTX_DIR
exit /b 0
