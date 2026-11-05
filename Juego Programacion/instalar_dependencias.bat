@echo off
title Instalador de Dependencias - Steam and Blade: Elemental Odyssey
echo =====================================================================
echo  INSTALANDO DEPENDENCIAS (Pygame-ce)
echo =====================================================================
cd /d "%~dp0"

echo [1/2] Verificando e instalando con 'py'...
py -m pip install -r requirements.txt
if %ERRORLEVEL% EQU 0 goto exito

echo.
echo [2/2] 'py' no respondio, intentando con 'python'...
python -m pip install -r requirements.txt
if %ERRORLEVEL% EQU 0 goto exito

echo.
echo =====================================================================
echo  [ERROR] No se pudo instalar automaticamente.
echo  Verifica tener Python 3.9 o superior instalado y anadido al PATH.
echo =====================================================================
pause
exit /b 1

:exito
echo.
echo =====================================================================
echo  [EXITO] Dependencias instaladas correctamente.
echo  Ya puedes iniciar el juego ejecutando 'run_game.bat'.
echo =====================================================================
pause
