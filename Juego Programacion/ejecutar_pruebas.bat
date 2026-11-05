@echo off
title Bateria de Pruebas - Steam and Blade: Elemental Odyssey
echo =====================================================================
echo  EJECUTANDO BATERIA INTEGRAL DE PRUEBAS DEL MOTOR
echo =====================================================================
cd /d "%~dp0"

py test_integrity.py
py test_new_enemies.py
py test_pause_menu.py
py audit_all_systems.py

echo.
echo =====================================================================
echo  PRUEBAS FINALIZADAS
echo =====================================================================
pause
