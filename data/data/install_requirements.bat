@echo off
echo Установка необходимых пакетов для дашборда Байкальской природной территории...
echo.
echo Установка базовых пакетов...
pip install dash==2.13.0 dash-bootstrap-components==1.5.0 dash-bootstrap-templates==1.0.8 plotly==5.18.0 pandas==2.0.3 numpy==1.24.3 scikit-learn==1.3.0 openpyxl==3.1.2 xlrd==2.0.1

echo.
echo Попытка установки географических пакетов...
echo (Примечание: эти пакеты могут вызывать ошибки на Windows. Если установка не удается, дашборд все равно запустится с ограниченной функциональностью.)
pip install fiona==1.9.4 geopandas==0.13.2

echo.
echo Установка завершена. Теперь вы можете запустить дашборд, выполнив run_dashboard.bat
echo.
echo Если возникли проблемы с установкой географических пакетов, вы можете установить их через conda:
echo conda install -c conda-forge geopandas
echo.
pause 