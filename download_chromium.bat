@echo off
setlocal enabledelayedexpansion

:: Устанавливаем переменные
set CHROMIUM_URL=https://github.com/Hibbiki/chromium-win64/releases/download/v137.0.7151.104-r1453031/chrome.sync.7z
set OUTPUT=chromium.7z
set DIR=chromium

:: Скачиваем Chromium
echo Downloading Chromium...
powershell -Command "Invoke-WebRequest -Uri '%CHROMIUM_URL%' -OutFile '%OUTPUT%'"
if %errorlevel% neq 0 (
    echo Error downloading Chromium.
    exit /b 1
)

:: Создаем папку для извлечения
if not exist "%DIR%" mkdir "%DIR%"

:: Разархивируем с помощью WinRAR
echo Using WinRAR for extraction...
"WinRARPortable\WinRARPortable.exe" x "%OUTPUT%" "%DIR%\"
if %errorlevel% neq 0 (
    echo Error extracting Chromium with WinRAR.
    exit /b 1
)

:: Удаляем архив
del "%OUTPUT%"

echo Script completed successfully.
