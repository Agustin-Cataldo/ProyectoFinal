@echo off
title Bateria de Pruebas - Clockwork Requiem
echo =====================================================================
echo  EJECUTANDO BATERIA INTEGRAL DE PRUEBAS DEL MOTOR
echo =====================================================================
cd /d "%~dp0"

py tests\test_integrity.py
py tests\test_new_enemies.py
py tests\test_pause_menu.py
py tests\test_user_fixes.py
py tests\test_gameplay_flow.py
py tests\audit_all_systems.py

echo.
echo =====================================================================
echo  PRUEBAS FINALIZADAS
echo =====================================================================
pause
