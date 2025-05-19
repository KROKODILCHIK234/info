@echo off
echo Запуск дашборда Байкальской природной территории...
echo.

REM Проверяем установлены ли необходимые пакеты
python -c "import dash" 2>nul
if %errorlevel% neq 0 (
    echo Необходимые пакеты не установлены.
    echo Запускаем установку пакетов...
    call install_requirements.bat
    echo.
)

REM Проверяем наличие папок с данными
echo Проверка наличия данных...
if not exist "Туризм\Турпоток.xlsx" (
    echo Данные о туризме не найдены.
    set DATA_MISSING=1
)
if not exist "Экология\Уровень воды.xlsx" (
    echo Данные об уровне воды не найдены.
    set DATA_MISSING=1
)
if not exist "Леса и животные\Вылов рыбы.xlsx" (
    echo Данные о вылове рыбы не найдены.
    set DATA_MISSING=1
)
if not exist "География\baikal_simply.geojson" (
    echo Географические данные не найдены.
    set DATA_MISSING=1
)
if not exist "Землетрясения\earthquakes_BR_1923-2023.geojson" (
    echo Данные о землетрясениях не найдены.
    set DATA_MISSING=1
)

REM Если хотя бы один файл данных отсутствует, генерируем тестовые данные
if defined DATA_MISSING (
    echo.
    echo Обнаружены отсутствующие данные. Генерируем тестовые данные...
    python generate_test_data.py
    echo.
)

REM Запускаем дашборд
echo Запуск дашборда...
python app.py

echo Дашборд доступен по адресу http://127.0.0.1:8050/
pause 