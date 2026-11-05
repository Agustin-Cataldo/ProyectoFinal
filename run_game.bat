@echo off
title Clockwork Requiem
echo =====================================================================
echo  INICIANDO: CLOCKWORK REQUIEM
echo  (Hack and Slash Roguelike 2D - Dark Steampunk)
echo =====================================================================
cd /d "%~dp0"

py main.py
if %ERRORLEVEL% EQU 0 goto fin

echo.
echo [AVISO] 'py' no respondio o fallo. Intentando con 'python'...
python main.py
if %ERRORLEVEL% EQU 0 goto fin

echo.
echo =====================================================================
echo  [ERROR AL INICIAR EL JUEGO]
echo  1. Asegurate de tener Python 3.9+ instalado en la computadora.
echo  2. Asegurate de haber ejecutado 'instalar_dependencias.bat'.
echo =====================================================================
pause

:fin
