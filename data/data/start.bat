@echo off
echo.
echo =======================================
echo  Запуск дашборда Байкальской природной территории
echo =======================================
echo.

:menu
echo Выберите режим запуска:
echo.
echo 1. Полная версия дашборда (с картами, если доступны geopandas и fiona)
echo 2. Упрощенная версия дашборда (без зависимости от geopandas)
echo 3. Сгенерировать тестовые данные
echo 4. Исправить проблему с геоданными
echo 5. Выход
echo.

set /p choice="Введите номер [1-5]: "

if "%choice%"=="1" goto full
if "%choice%"=="2" goto simple
if "%choice%"=="3" goto generate
if "%choice%"=="4" goto fix_geo
if "%choice%"=="5" goto end

echo.
echo Неверный выбор. Пожалуйста, попробуйте снова.
echo.
goto menu

:full
echo.
echo Запуск полной версии дашборда...
echo.
echo ВАЖНО: Если вы увидите ошибку 'module fiona has no attribute path', 
echo        вернитесь в меню и выберите опцию 4 для исправления проблемы
echo        или запустите упрощенную версию (опция 2)
echo.
start cmd /k python app.py
goto end

:simple
echo.
echo Запуск упрощенной версии дашборда...
echo.
start cmd /k python app_simple.py
goto end

:generate
echo.
echo Генерация тестовых данных...
echo.
python generate_test_data.py
echo.
echo Данные сгенерированы. Нажмите любую клавишу для возврата в меню...
pause > nul
goto menu

:fix_geo
echo.
echo Исправление проблем с геоданными...
echo.
echo 1) Обновление библиотек geopandas и fiona...
python -m pip install --upgrade geopandas pyogrio
echo.
echo 2) Регенерация географических данных...
python -c "import generate_test_data; generate_test_data.generate_geographic_data(); generate_test_data.generate_earthquake_data(); generate_test_data.generate_fire_data()"
echo.
echo Географические данные обновлены. Запуск упрощенной версии дашборда рекомендуется.
echo Нажмите любую клавишу для возврата в меню...
pause > nul
goto menu

:end
echo.
echo Дашборд доступен в браузере. Для завершения работы закройте окно браузера и окно команд.
echo. 