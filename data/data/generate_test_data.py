import os
import pandas as pd
import numpy as np
import json
import random
from datetime import datetime, timedelta

def ensure_directory(directory):
    """Создает директорию, если она не существует"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Создана директория {directory}")

def generate_tourism_data():
    """Генерирует тестовые данные о туризме"""
    years = list(range(2010, 2023))
    base_tourists = 500  # тыс. чел.
    growth_rate = 0.15   # 15% роста в год
    
    tourists = [base_tourists * (1 + growth_rate) ** i for i in range(len(years))]
    
    # Добавим некоторую случайность
    tourists = [t * random.uniform(0.9, 1.1) for t in tourists]
    
    # Округлим до целых чисел
    tourists = [round(t) for t in tourists]
    
    df = pd.DataFrame({
        'Год': years,
        'Количество туристов, тыс. чел.': tourists
    })
    
    ensure_directory('Туризм')
    df.to_excel('Туризм/Турпоток.xlsx', index=False)
    print("Сгенерированы данные о туризме")

def generate_water_level_data():
    """Генерирует тестовые данные об уровне воды"""
    years = list(range(2010, 2023))
    base_level = 456  # см
    
    # Генерируем данные с некоторой случайностью и трендом
    levels = [base_level + random.uniform(-20, 20) + (i - len(years) // 2) * 0.5 for i in range(len(years))]
    
    # Округлим до целых чисел
    levels = [round(l) for l in levels]
    
    df = pd.DataFrame({
        'Год': years,
        'Уровень, см': levels
    })
    
    ensure_directory('Экология')
    df.to_excel('Экология/Уровень воды.xlsx', index=False)
    print("Сгенерированы данные об уровне воды")

def generate_fish_catch_data():
    """Генерирует тестовые данные о вылове рыбы"""
    years = list(range(2010, 2023))
    fish_types = ['Омуль', 'Сиг', 'Хариус', 'Осетр', 'Другие']
    
    # Базовые значения вылова для каждого вида рыбы
    base_catch = {
        'Омуль': 200,
        'Сиг': 150,
        'Хариус': 100,
        'Осетр': 50,
        'Другие': 180
    }
    
    # Создаем пустой DataFrame
    df = pd.DataFrame()
    
    # Для каждого года и вида рыбы генерируем данные
    for year in years:
        for fish in fish_types:
            # Базовый вылов с некоторой случайностью
            catch = base_catch[fish] * random.uniform(0.8, 1.2)
            
            # Добавляем тренд (уменьшение вылова со временем для некоторых видов)
            if fish in ['Омуль', 'Осетр']:
                catch *= 1 - 0.03 * (year - 2010)
            
            # Округляем до целых
            catch = round(catch)
            
            # Добавляем запись в DataFrame
            df = pd.concat([df, pd.DataFrame({
                'Год': [year],
                'Вид': [fish],
                'Вылов, тонн': [catch]
            })])
    
    # Сбрасываем индекс
    df = df.reset_index(drop=True)
    
    ensure_directory('Леса и животные')
    df.to_excel('Леса и животные/Вылов рыбы.xlsx', index=False)
    print("Сгенерированы данные о вылове рыбы")

def generate_air_quality_data():
    """Генерирует тестовые данные о качестве воздуха"""
    # Создаем даты каждые 3 часа за последний год
    start_date = datetime(2022, 1, 1)
    end_date = datetime(2022, 12, 31)
    
    # Генерируем даты с шагом в 3 часа
    dates = []
    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date)
        current_date += timedelta(hours=3)
    
    # Базовое значение PM2.5
    base_pm25 = 15  # мкг/м³
    
    # Генерируем значения с сезонными колебаниями, случайностью и суточными колебаниями
    values = []
    for date in dates:
        # Сезонный компонент (зимой выше)
        seasonal = 10 * np.sin(np.pi * (date.month - 1) / 6)
        
        # Суточный компонент (утром и вечером выше)
        daily = 5 * np.sin(np.pi * date.hour / 12)
        
        # Случайный компонент
        random_comp = random.uniform(-5, 5)
        
        # Итоговое значение
        value = max(1, base_pm25 + seasonal + daily + random_comp)
        values.append(round(value, 1))
    
    # Создаем DataFrame
    df = pd.DataFrame({
        'Дата/время': [d.strftime("%d.%m.%Y %H:%M:%S") for d in dates],
        'Значение': values
    })
    
    ensure_directory('Экология/Атмосфера')
    df.to_csv('Экология/Атмосфера/PM2,5.csv', index=False, sep=';')
    print("Сгенерированы данные о качестве воздуха")

def generate_simple_geojson(output_path, content):
    """Генерирует простой GeoJSON-файл"""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(content, f, ensure_ascii=False)
    print(f"Создан файл {output_path}")

def generate_geographic_data():
    """Генерирует тестовые географические данные"""
    ensure_directory('География')
    
    # Создаем простой GeoJSON для Байкальского региона
    baikal_region = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "id": 0,
                "properties": {"name": "Байкальская природная территория"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[104.3, 51.5], [104.3, 55.5], [110.5, 55.5], [110.5, 51.5], [104.3, 51.5]]]
                }
            }
        ]
    }
    generate_simple_geojson('География/baikal_simply.geojson', baikal_region)
    
    # Создаем GeoJSON для заповедников
    zapovedniki = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "id": 0,
                "properties": {"name": "Баргузинский заповедник"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[108.5, 54.0], [108.5, 54.5], [109.5, 54.5], [109.5, 54.0], [108.5, 54.0]]]
                }
            },
            {
                "type": "Feature",
                "id": 1,
                "properties": {"name": "Байкальский заповедник"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[105.5, 51.5], [105.5, 52.0], [106.5, 52.0], [106.5, 51.5], [105.5, 51.5]]]
                }
            }
        ]
    }
    generate_simple_geojson('География/zapovedniki.geojson', zapovedniki)
    
    # Создаем GeoJSON для городов
    cities = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "id": 0,
                "properties": {"name": "Иркутск"},
                "geometry": {
                    "type": "Point",
                    "coordinates": [104.3, 52.3]
                }
            },
            {
                "type": "Feature",
                "id": 1,
                "properties": {"name": "Улан-Удэ"},
                "geometry": {
                    "type": "Point",
                    "coordinates": [107.6, 51.8]
                }
            },
            {
                "type": "Feature",
                "id": 2,
                "properties": {"name": "Северобайкальск"},
                "geometry": {
                    "type": "Point",
                    "coordinates": [109.3, 55.6]
                }
            },
            {
                "type": "Feature",
                "id": 3,
                "properties": {"name": "Листвянка"},
                "geometry": {
                    "type": "Point",
                    "coordinates": [104.8, 51.9]
                }
            }
        ]
    }
    generate_simple_geojson('География/city_points.geojson', cities)

def generate_earthquake_data():
    """Генерирует тестовые данные о землетрясениях"""
    ensure_directory('Землетрясения')
    
    # Создаем список для хранения объектов землетрясений
    features = []
    
    # Генерируем данные с 1923 по 2023 год
    start_year = 1923
    end_year = 2023
    
    # Для каждого года генерируем случайное количество землетрясений
    for year in range(start_year, end_year + 1):
        # Больше землетрясений в последние годы (лучше мониторинг)
        num_earthquakes = random.randint(1, 3) if year < 1970 else random.randint(3, 8)
        
        for i in range(num_earthquakes):
            # Генерируем дату
            month = random.randint(1, 12)
            day = random.randint(1, 28)
            date_str = f"{year}-{month:02d}-{day:02d}"
            
            # Генерируем магнитуду (более сильные редки)
            magnitude = round(random.uniform(2.0, 5.5), 1)
            
            # Генерируем координаты в регионе Байкала
            longitude = random.uniform(104.0, 110.0)
            latitude = random.uniform(51.5, 55.5)
            
            # Создаем объект землетрясения
            feature = {
                "type": "Feature",
                "id": len(features),
                "properties": {
                    "date": date_str,
                    "mag": magnitude
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [longitude, latitude]
                }
            }
            
            features.append(feature)
    
    # Создаем GeoJSON объект
    earthquakes = {
        "type": "FeatureCollection",
        "features": features
    }
    
    generate_simple_geojson('Землетрясения/earthquakes_BR_1923-2023.geojson', earthquakes)

def generate_fire_data():
    """Генерирует тестовые данные о пожарах"""
    ensure_directory('Пожары')
    
    # Создаем список для хранения объектов пожаров
    features = []
    
    # Генерируем данные с 2011 по 2021 год
    start_year = 2011
    end_year = 2021
    
    # Месяцы с высоким риском пожаров
    high_risk_months = [5, 6, 7, 8]  # май-август
    
    # Для каждого года генерируем пожары
    for year in range(start_year, end_year + 1):
        # Больше пожаров в летние месяцы
        for month in range(1, 13):
            # Определяем количество пожаров в зависимости от месяца
            if month in high_risk_months:
                num_fires = random.randint(20, 50)  # больше в высокий сезон
            else:
                num_fires = random.randint(0, 10)
            
            for i in range(num_fires):
                # Генерируем день
                day = random.randint(1, 28)
                date_str = f"{year}-{month:02d}-{day:02d}"
                
                # Генерируем координаты в регионе Байкала
                # Пожары чаще случаются в лесистых районах
                longitude = random.uniform(104.0, 110.0)
                latitude = random.uniform(51.5, 55.5)
                
                # Создаем объект пожара
                feature = {
                    "type": "Feature",
                    "id": len(features),
                    "properties": {
                        "date": date_str
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [longitude, latitude]
                    }
                }
                
                features.append(feature)
    
    # Создаем GeoJSON объект
    fires = {
        "type": "FeatureCollection",
        "features": features
    }
    
    generate_simple_geojson('Пожары/fires_BR_2011-2021.geojson', fires)

def generate_all_test_data():
    """Генерирует все тестовые данные"""
    generate_tourism_data()
    generate_water_level_data()
    generate_fish_catch_data()
    generate_air_quality_data()
    generate_geographic_data()
    generate_earthquake_data()
    generate_fire_data()
    print("\nВсе тестовые данные сгенерированы успешно!")

if __name__ == "__main__":
    print("Генерация тестовых данных для дашборда Байкальской природной территории...")
    generate_all_test_data() 