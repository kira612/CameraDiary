@echo off
setlocal

set "WSL_DISTRO=%~1"
set "MEDIAMTX_BIN=%~2"
set "MEDIAMTX_CONFIG=%~3"

if "%MEDIAMTX_BIN%"=="" set "MEDIAMTX_BIN=/home/kirataiki/apps/vendor/mediamtx/mediamtx"
if "%MEDIAMTX_CONFIG%"=="" set "MEDIAMTX_CONFIG=/home/kirataiki/apps/config/mediamtx.yml"

if "%WSL_DISTRO%"=="" (
  wsl -- "%MEDIAMTX_BIN%" "%MEDIAMTX_CONFIG%"
) else (
  wsl -d "%WSL_DISTRO%" -- "%MEDIAMTX_BIN%" "%MEDIAMTX_CONFIG%"
)
