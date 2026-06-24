@echo off
chcp 65001 >nul
echo.
echo ═══════════════════════════════════════════════════════════
echo   ALGORITMOS DE BÚSQUEDA — BFS / DFS / UCS / A*
echo ═══════════════════════════════════════════════════════════
echo.
echo [1] Ejecutar programa principal
echo [2] Ejecutar pruebas unitarias
echo [3] Salir
echo.
set /p opcion="→ Elige una opción: "

if "%opcion%"=="1" (
    python src/main.py
)
if "%opcion%"=="2" (
    python -m pytest tests/ -v --tb=short 2>nul || python -m unittest discover -s tests -v
)
if "%opcion%"=="3" (
    exit
)
pause
