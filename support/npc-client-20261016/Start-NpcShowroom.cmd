@echo off
if not exist "%~dp0player\NpcArtShowroom.exe" (
  echo NPC showroom player is missing. Keep this launcher beside the player folder.
  pause
  exit /b 1
)
start "" "%~dp0player\NpcArtShowroom.exe" -screen-fullscreen 0 -screen-width 1440 -screen-height 900
