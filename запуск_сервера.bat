@echo off
chcp 65001 > nul
title Тактическая онлайн-карта Arma 3 Altis
echo ======================================================
echo    Запуск тактической онлайн-карты Arma 3 Altis...
echo    Папка: %~dp0
echo ======================================================
echo.

cd /d "%~dp0сервер"

:: Не запускаем второй экземпляр, если сайт уже работает
powershell -NoProfile -ExecutionPolicy Bypass -Command "try { $r = Invoke-WebRequest -UseBasicParsing http://localhost:3000 -TimeoutSec 2; if ($r.StatusCode -eq 200) { exit 0 } } catch {}; exit 1"
if %ERRORLEVEL% equ 0 (
    echo [OK] Сайт уже запущен. Открываю карту...
    start "" http://localhost:3000
    goto :end
)

:: Проверяем локальный встроенный node.exe
if exist "%~dp0сервер\node.exe" (
    echo [OK] Запуск через встроенный автономный Node.js...
    start "" cmd /c "timeout /t 2 /nobreak > nul & start http://localhost:3000"
    "%~dp0сервер\node.exe" server.js
    goto :end
)

:: Проверяем системный node
where node >nul 2>nul
if %ERRORLEVEL% equ 0 (
    echo [OK] Запуск через системный Node.js...
    start "" cmd /c "timeout /t 2 /nobreak > nul & start http://localhost:3000"
    node server.js
    goto :end
)

echo.
echo [!] ОШИБКА: Node.js не найден на компьютере!
echo Установите Node.js с официального сайта (LTS версия): https://nodejs.org/
echo.
start https://nodejs.org/
pause

:end
