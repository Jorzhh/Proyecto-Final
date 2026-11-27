@echo off
setlocal
title BioLab 3D - Proyecto Final

set "PROJECT_DIR=%~dp0"
set "PHP_BIN=C:\xampp\php\php.exe"

if not exist "%PROJECT_DIR%public\index.html" goto project_missing
if not exist "%PROJECT_DIR%node_modules\vite\bin\vite.js" goto frontend_dependencies_missing

echo Iniciando BioLab 3D desde:
echo %PROJECT_DIR%
echo.

if not exist "%PROJECT_DIR%api\index.php" goto frontend_only
if not exist "%PROJECT_DIR%api\vendor\autoload.php" goto frontend_only
if exist "%PHP_BIN%" goto php_ready
where.exe php >nul 2>&1
if errorlevel 1 goto frontend_only
set "PHP_BIN=php"

:php_ready
echo Iniciando API PHP local en el puerto 8086 ...
start "BioLab API REST - puerto 8086" /min "%PHP_BIN%" -S 127.0.0.1:8086 -t "%PROJECT_DIR%api" "%PROJECT_DIR%api\index.php"
goto start_frontend

:frontend_only
echo No se encontraron PHP/FlightPHP completos; se abrira la demo sin conexion.
echo MySQL y la API solo hacen falta para guardar datos o consultar fuentes en vivo.
echo.

:start_frontend
echo Iniciando Vite para el navegador en el puerto 3006 ...
start "BioLab Vite - puerto 3006" /min "%ComSpec%" /d /c "cd /d ""%PROJECT_DIR%"" && npm run dev"

echo Esperando a los servidores...
timeout /t 3 /nobreak >nul
start "" "http://localhost:3006"

echo.
echo El proyecto se abre en http://localhost:3006
echo MySQL no es necesario para recorrer la demo y el globo.
echo No abras public\index.html con doble clic.
echo Si el navegador no abre, copia la direccion y pegala manualmente.
echo.
pause
exit /b 0

:frontend_dependencies_missing
echo [ERROR] No se encontraron las dependencias de Vite en node_modules.
echo Instala Node.js y ejecuta corepack pnpm install desde esta carpeta.
pause
exit /b 1

:project_missing
echo [ERROR] No se encontro public\index.html en:
echo %PROJECT_DIR%
echo Verifica que la carpeta Proyecto Final este completa.
pause
exit /b 1
