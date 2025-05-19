import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import warnings
import os
import traceback
import sys
from dash_bootstrap_templates import load_figure_template

# Подавление предупреждений
warnings.filterwarnings('ignore')

# Проверка наличия данных и генерация тестовых данных при необходимости
try:
    required_files = [
        'Туризм/Турпоток.xlsx',
        'Экология/Уровень воды.xlsx',
        'Леса и животные/Вылов рыбы.xlsx',
        'География/baikal_simply.geojson',
        'Землетрясения/earthquakes_BR_1923-2023.geojson'
    ]
    
    missing_files = [f for f in required_files if not os.path.exists(f)]
    if missing_files:
        print(f"Отсутствуют следующие файлы: {', '.join(missing_files)}")
        print("Запуск генерации тестовых данных...")
        
        try:
            import generate_test_data
            generate_test_data.generate_all_test_data()
            print("Тестовые данные успешно сгенерированы.")
        except Exception as e:
            print(f"Ошибка при генерации тестовых данных: {e}")
            print("Вы можете запустить generate_test_data.py вручную.")
except Exception as e:
    print(f"Ошибка при проверке наличия данных: {e}")

# Объявление заглушек для импортов, которые могут вызвать ошибки
try:
    import geopandas as gpd
    import json
    
    # Проверка, доступен ли fiona и имеет ли нужные атрибуты
    import fiona
    # Избегаем использования fiona.path
    GEODATA_AVAILABLE = True
    print("Библиотеки для работы с геоданными успешно импортированы.")
except ImportError as e:
    GEODATA_AVAILABLE = False
    print(f"ВНИМАНИЕ: библиотеки для геоданных не установлены: {str(e)}. Географические визуализации не будут доступны.")
except AttributeError as e:
    GEODATA_AVAILABLE = False
    print(f"ВНИМАНИЕ: ошибка атрибута в библиотеке геоданных: {str(e)}. Географические визуализации не будут доступны.")
except Exception as e:
    GEODATA_AVAILABLE = False
    print(f"ВНИМАНИЕ: ошибка при импорте библиотек геоданных: {e}. Географические визуализации не будут доступны.")

# Обеспечиваем доступность json даже если geopandas недоступен
if not GEODATA_AVAILABLE:
    try:
        import json
    except ImportError:
        print("ВНИМАНИЕ: модуль json не установлен. Необходим для обработки географических данных.")

# Попытка импорта модулей визуализации
try:
    # Импортируем только если geopandas доступен
    if GEODATA_AVAILABLE:
        try:
            from map_visualization import create_detailed_map, create_earthquake_heatmap
            MAP_MODULE_AVAILABLE = True
            print("Модуль карт успешно импортирован.")
        except Exception as e:
            MAP_MODULE_AVAILABLE = False
            print(f"ВНИМАНИЕ: Ошибка при импорте модуля map_visualization: {e}. Будут использованы заглушки для карт.")
    else:
        MAP_MODULE_AVAILABLE = False
        print("ВНИМАНИЕ: geopandas недоступен, модуль карт не будет импортирован.")
except Exception as e:
    MAP_MODULE_AVAILABLE = False
    print(f"ВНИМАНИЕ: Ошибка при проверке импорта модуля карт: {e}. Будут использованы заглушки для карт.")

try:
    from data_analysis import (
        load_and_prepare_tourism_data,
        load_and_prepare_water_data,
        load_and_prepare_fish_data,
        load_and_prepare_air_quality_data,
        load_and_prepare_earthquake_data,
        load_and_prepare_fire_data,
        create_combined_ecological_trends,
        create_tourism_forecast
    )
    DATA_ANALYSIS_MODULE_AVAILABLE = True
    print("Модуль анализа данных успешно импортирован.")
except ImportError:
    DATA_ANALYSIS_MODULE_AVAILABLE = False
    print("ВНИМАНИЕ: Модуль data_analysis недоступен. Будут использованы заглушки для анализа данных.")

# Функции-заглушки для случаев, когда модули недоступны
def create_placeholder_map():
    fig = go.Figure()
    fig.add_annotation(
        text="Карта недоступна: требуется установить geopandas и другие зависимости",
        showarrow=False,
        font=dict(size=20)
    )
    fig.update_layout(height=600)
    return fig

def create_placeholder_figure(title="Данные недоступны"):
    fig = go.Figure()
    fig.add_annotation(
        text=title,
        showarrow=False,
        font=dict(size=20)
    )
    fig.update_layout(height=400)
    return fig

# Функция для создания простой карты без geopandas
def create_simple_map():
    # Координаты основных городов
    cities = {
        'Иркутск': {'lat': 52.3, 'lon': 104.3},
        'Улан-Удэ': {'lat': 51.8, 'lon': 107.6},
        'Северобайкальск': {'lat': 55.6, 'lon': 109.3},
        'Листвянка': {'lat': 51.9, 'lon': 104.8}
    }
    
    # Создаем базовую карту
    fig = go.Figure()
    
    # Добавляем города как маркеры
    fig.add_trace(go.Scattermapbox(
        lat=[city['lat'] for city in cities.values()],
        lon=[city['lon'] for city in cities.values()],
        mode='markers+text',
        marker=dict(size=10, color='#d62728'),
        text=list(cities.keys()),
        textposition="top center",
        name='Города'
    ))
    
    # Примерный контур озера Байкал (упрощенно)
    baikal_lats = [51.5, 51.9, 53.5, 55.8, 55.4, 53.0, 51.5]
    baikal_lons = [104.3, 105.0, 107.0, 109.5, 109.0, 107.0, 104.3]
    
    fig.add_trace(go.Scattermapbox(
        lat=baikal_lats,
        lon=baikal_lons,
        mode='lines',
        line=dict(width=2, color='#46b3e6'),
        fill='toself',
        fillcolor='rgba(70, 179, 230, 0.3)',
        name='Озеро Байкал'
    ))
    
    # Настраиваем вид карты
    fig.update_layout(
        mapbox=dict(
            style="open-street-map",
            center=dict(lat=53.5, lon=108),
            zoom=5
        ),
        height=800,
        margin={"r": 0, "t": 30, "l": 0, "b": 0},
        title="Карта Байкальской природной территории"
    )
    
    return fig

# Load the stylesheets
app = dash.Dash(__name__, 
                external_stylesheets=[dbc.themes.COSMO],
                meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0'}],
                suppress_callback_exceptions=True
)
server = app.server

# Load figure template for consistent styling
load_figure_template("cosmo")

# Инициализация данных
tourism_data = pd.DataFrame()
water_level_data = pd.DataFrame()
fish_catch_data = pd.DataFrame()
air_quality_data = pd.DataFrame()
earthquake_data = None  # Может быть GeoDataFrame или None
fire_data = None  # Может быть GeoDataFrame или None

# Проверка доступности файлов данных
data_files_status = {
    "Туризм": False,
    "Уровень воды": False,
    "Вылов рыбы": False,
    "Качество воздуха": False,
    "Землетрясения": False,
    "Пожары": False,
    "География": False
}

# Try to preload data
try:
    # Проверка наличия папок и файлов
    if os.path.exists('Туризм') and os.path.exists('Туризм/Турпоток.xlsx'):
        if DATA_ANALYSIS_MODULE_AVAILABLE:
            tourism_data = load_and_prepare_tourism_data()
            if not tourism_data.empty:
                data_files_status["Туризм"] = True
        else:
            try:
                tourism_data = pd.read_excel('Туризм/Турпоток.xlsx')
                tourism_data['Год'] = tourism_data['Год'].astype(str)
                tourism_data['growth_rate'] = tourism_data['Количество туристов, тыс. чел.'].pct_change() * 100
                data_files_status["Туризм"] = True
            except Exception as e:
                print(f"Ошибка при загрузке данных туризма: {e}")
    
    if os.path.exists('Экология') and os.path.exists('Экология/Уровень воды.xlsx'):
        if DATA_ANALYSIS_MODULE_AVAILABLE:
            water_level_data = load_and_prepare_water_data()
            if not water_level_data.empty:
                data_files_status["Уровень воды"] = True
        else:
            try:
                water_level_data = pd.read_excel('Экология/Уровень воды.xlsx')
                data_files_status["Уровень воды"] = True
            except Exception as e:
                print(f"Ошибка при загрузке данных уровня воды: {e}")
    
    if os.path.exists('Леса и животные') and os.path.exists('Леса и животные/Вылов рыбы.xlsx'):
        if DATA_ANALYSIS_MODULE_AVAILABLE:
            fish_catch_data = load_and_prepare_fish_data()
            if not fish_catch_data.empty:
                data_files_status["Вылов рыбы"] = True
        else:
            try:
                fish_catch_data = pd.read_excel('Леса и животные/Вылов рыбы.xlsx')
                data_files_status["Вылов рыбы"] = True
            except Exception as e:
                print(f"Ошибка при загрузке данных вылова рыбы: {e}")
    
    if os.path.exists('Экология/Атмосфера') and os.path.exists('Экология/Атмосфера/PM2,5.csv'):
        if DATA_ANALYSIS_MODULE_AVAILABLE:
            try:
                air_quality_data = load_and_prepare_air_quality_data()
                if not air_quality_data.empty:
                    data_files_status["Качество воздуха"] = True
            except Exception as e:
                print(f"Ошибка при загрузке данных качества воздуха через модуль: {e}")
                # Пробуем загрузить самостоятельно
                try:
                    air_pm25 = pd.read_csv('Экология/Атмосфера/PM2,5.csv', delimiter=';')
                    
                    # Пробуем разные форматы дат
                    try:
                        # Сначала пытаемся с явным указанием формата DD.MM.YYYY
                        air_pm25['date'] = pd.to_datetime(air_pm25['Дата/время'], format="%d.%m.%Y %H:%M:%S", errors='coerce')
                    except Exception:
                        try:
                            # Затем пробуем автоопределение с dayfirst=True
                            air_pm25['date'] = pd.to_datetime(air_pm25['Дата/время'], dayfirst=True, errors='coerce')
                        except Exception:
                            # В крайнем случае используем mixed формат
                            air_pm25['date'] = pd.to_datetime(air_pm25['Дата/время'], format='mixed', dayfirst=True, errors='coerce')
                    
                    # Отбрасываем строки с недопустимыми датами
                    air_pm25 = air_pm25.dropna(subset=['date'])
                    
                    # Если есть данные после фильтрации, создаем итоговый DataFrame
                    if not air_pm25.empty:
                        air_pm25['month'] = air_pm25['date'].dt.month
                        air_pm25['year'] = air_pm25['date'].dt.year
                        air_quality_data = air_pm25.groupby(['year', 'month'])['Значение'].mean().reset_index()
                        air_quality_data['date'] = pd.to_datetime(air_quality_data[['year', 'month']].assign(day=1))
                        data_files_status["Качество воздуха"] = True
                    else:
                        print("После обработки дат нет допустимых строк в данных качества воздуха")
                except Exception as e:
                    print(f"Ошибка при ручной загрузке данных качества воздуха: {e}")
        else:
            try:
                air_pm25 = pd.read_csv('Экология/Атмосфера/PM2,5.csv', delimiter=';')
                
                # Пробуем разные форматы дат
                try:
                    # Сначала пытаемся с явным указанием формата DD.MM.YYYY
                    air_pm25['date'] = pd.to_datetime(air_pm25['Дата/время'], format="%d.%m.%Y %H:%M:%S", errors='coerce')
                except Exception:
                    try:
                        # Затем пробуем автоопределение с dayfirst=True
                        air_pm25['date'] = pd.to_datetime(air_pm25['Дата/время'], dayfirst=True, errors='coerce')
                    except Exception:
                        # В крайнем случае используем mixed формат
                        air_pm25['date'] = pd.to_datetime(air_pm25['Дата/время'], format='mixed', dayfirst=True, errors='coerce')
                
                # Отбрасываем строки с недопустимыми датами
                air_pm25 = air_pm25.dropna(subset=['date'])
                
                # Если есть данные после фильтрации, создаем итоговый DataFrame
                if not air_pm25.empty:
                    air_pm25['month'] = air_pm25['date'].dt.month
                    air_pm25['year'] = air_pm25['date'].dt.year
                    air_quality_data = air_pm25.groupby(['year', 'month'])['Значение'].mean().reset_index()
                    air_quality_data['date'] = pd.to_datetime(air_quality_data[['year', 'month']].assign(day=1))
                    data_files_status["Качество воздуха"] = True
                else:
                    print("После обработки дат нет допустимых строк в данных качества воздуха")
            except Exception as e:
                print(f"Ошибка при загрузке данных качества воздуха: {e}")
    
    # Geography data - only if geopandas is available
    if GEODATA_AVAILABLE:
        if os.path.exists('География'):
            try:
                if os.path.exists('География/baikal_simply.geojson'):
                    baikal_region = gpd.read_file('География/baikal_simply.geojson')
                    data_files_status["География"] = True
                else:
                    print("Файл с контурами Байкала не найден, создаю...")
                    import generate_test_data
                    generate_test_data.generate_geographic_data()
                    if os.path.exists('География/baikal_simply.geojson'):
                        baikal_region = gpd.read_file('География/baikal_simply.geojson')
                        data_files_status["География"] = True
                
                if os.path.exists('География/zapovedniki.geojson'):
                    zapovedniki = gpd.read_file('География/zapovedniki.geojson')
                if os.path.exists('География/city_points.geojson'):
                    city_points = gpd.read_file('География/city_points.geojson')
            except Exception as e:
                print(f"Ошибка при загрузке географических данных: {e}")
        else:
            print("Папка с географическими данными не найдена, создаю...")
            try:
                import generate_test_data
                generate_test_data.generate_geographic_data()
                
                if os.path.exists('География/baikal_simply.geojson'):
                    baikal_region = gpd.read_file('География/baikal_simply.geojson')
                    data_files_status["География"] = True
                if os.path.exists('География/zapovedniki.geojson'):
                    zapovedniki = gpd.read_file('География/zapovedniki.geojson')
                if os.path.exists('География/city_points.geojson'):
                    city_points = gpd.read_file('География/city_points.geojson')
            except Exception as e:
                print(f"Ошибка при создании географических данных: {e}")
    elif os.path.exists('География/baikal_simply.geojson'):
        # Если geopandas не доступен, но файлы есть, отметим это
        data_files_status["География"] = "Файлы доступны, но требуется geopandas"
    
    # Earthquake data - only if geopandas is available
    if GEODATA_AVAILABLE and os.path.exists('Землетрясения'):
        if DATA_ANALYSIS_MODULE_AVAILABLE:
            try:
                earthquake_data = load_and_prepare_earthquake_data()
                if earthquake_data is not None and not earthquake_data.empty:
                    data_files_status["Землетрясения"] = True
            except Exception as e:
                print(f"Ошибка при загрузке данных землетрясений через модуль анализа: {e}")
                # Пробуем загрузить напрямую, если модуль анализа не справился
                try:
                    if os.path.exists('Землетрясения/earthquakes_BR_1923-2023.geojson'):
                        earthquake_data = gpd.read_file('Землетрясения/earthquakes_BR_1923-2023.geojson')
                        earthquake_data['year'] = pd.to_datetime(earthquake_data['date']).dt.year
                        earthquake_data['decade'] = (earthquake_data['year'] // 10) * 10
                        data_files_status["Землетрясения"] = True
                    else:
                        print("Запуск генерации данных о землетрясениях...")
                        import generate_test_data
                        generate_test_data.generate_earthquake_data()
                        if os.path.exists('Землетрясения/earthquakes_BR_1923-2023.geojson'):
                            earthquake_data = gpd.read_file('Землетрясения/earthquakes_BR_1923-2023.geojson')
                            earthquake_data['year'] = pd.to_datetime(earthquake_data['date']).dt.year
                            earthquake_data['decade'] = (earthquake_data['year'] // 10) * 10
                            data_files_status["Землетрясения"] = True
                except Exception as e:
                    print(f"Ошибка при загрузке данных землетрясений напрямую: {e}")
        else:
            try:
                if os.path.exists('Землетрясения/earthquakes_BR_1923-2023.geojson'):
                    earthquake_data = gpd.read_file('Землетрясения/earthquakes_BR_1923-2023.geojson')
                    earthquake_data['year'] = pd.to_datetime(earthquake_data['date']).dt.year
                    earthquake_data['decade'] = (earthquake_data['year'] // 10) * 10
                    data_files_status["Землетрясения"] = True
                else:
                    print("Запуск генерации данных о землетрясениях...")
                    import generate_test_data
                    generate_test_data.generate_earthquake_data()
                    if os.path.exists('Землетрясения/earthquakes_BR_1923-2023.geojson'):
                        earthquake_data = gpd.read_file('Землетрясения/earthquakes_BR_1923-2023.geojson')
                        earthquake_data['year'] = pd.to_datetime(earthquake_data['date']).dt.year
                        earthquake_data['decade'] = (earthquake_data['year'] // 10) * 10
                        data_files_status["Землетрясения"] = True
            except Exception as e:
                print(f"Ошибка при загрузке данных землетрясений: {e}")
    
    # Fire data - only if geopandas is available
    if GEODATA_AVAILABLE and os.path.exists('Пожары'):
        if DATA_ANALYSIS_MODULE_AVAILABLE:
            try:
                fire_data = load_and_prepare_fire_data()
                if fire_data is not None and not fire_data.empty:
                    data_files_status["Пожары"] = True
            except Exception as e:
                print(f"Ошибка при загрузке данных пожаров через модуль анализа: {e}")
                # Пробуем загрузить напрямую, если модуль анализа не справился
                try:
                    if os.path.exists('Пожары/fires_BR_2011-2021.geojson'):
                        fire_data = gpd.read_file('Пожары/fires_BR_2011-2021.geojson', rows=1000)
                        fire_data['year'] = pd.to_datetime(fire_data['date']).dt.year
                        data_files_status["Пожары"] = True
                    else:
                        print("Запуск генерации данных о пожарах...")
                        import generate_test_data
                        generate_test_data.generate_fire_data()
                        if os.path.exists('Пожары/fires_BR_2011-2021.geojson'):
                            fire_data = gpd.read_file('Пожары/fires_BR_2011-2021.geojson', rows=1000)
                            fire_data['year'] = pd.to_datetime(fire_data['date']).dt.year
                            data_files_status["Пожары"] = True
                except Exception as e:
                    print(f"Ошибка при загрузке данных пожаров напрямую: {e}")
        else:
            try:
                if os.path.exists('Пожары/fires_BR_2011-2021.geojson'):
                    fire_data = gpd.read_file('Пожары/fires_BR_2011-2021.geojson', rows=1000)
                    fire_data['year'] = pd.to_datetime(fire_data['date']).dt.year
                    data_files_status["Пожары"] = True
                else:
                    print("Запуск генерации данных о пожарах...")
                    import generate_test_data
                    generate_test_data.generate_fire_data()
                    if os.path.exists('Пожары/fires_BR_2011-2021.geojson'):
                        fire_data = gpd.read_file('Пожары/fires_BR_2011-2021.geojson', rows=1000)
                        fire_data['year'] = pd.to_datetime(fire_data['date']).dt.year
                        data_files_status["Пожары"] = True
            except Exception as e:
                print(f"Ошибка при загрузке данных пожаров: {e}")
    
    # Данные успешно загружены (хотя бы частично)
    print("Статус загрузки данных:")
    for key, value in data_files_status.items():
        print(f"  {key}: {'Успешно' if value is True else value if isinstance(value, str) else 'Ошибка'}")
    
    data_loaded = True
except Exception as e:
    print(f"Общая ошибка загрузки данных: {e}")
    traceback.print_exc()
    data_loaded = False

# Create a color palette
colors = {
    'primary': '#1f77b4',
    'secondary': '#2ca02c',
    'tertiary': '#d62728',
    'quaternary': '#9467bd',
    'quinary': '#ff7f0e',
    'background': '#f8f9fa',
    'text': '#343a40',
    'water': '#46b3e6',
    'forest': '#2e8b57',
    'fire': '#ff5733'
}

# Define the layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Байкальская природная территория", className="text-center my-4", 
                    style={'color': colors['text'], 'font-weight': 'bold'}),
            html.H5("Интерактивный дашборд для анализа экологических, природных и социальных данных", 
                    className="text-center mb-4", style={'color': colors['text']})
        ], width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Навигация", style={'background-color': colors['primary'], 'color': 'white'}),
                dbc.CardBody([
                    dcc.Tabs(id='tabs', value='tab-map', children=[
                        dcc.Tab(label='Карта региона', value='tab-map'),
                        dcc.Tab(label='Экология', value='tab-ecology'),
                        dcc.Tab(label='Туризм', value='tab-tourism'),
                        dcc.Tab(label='Природные явления', value='tab-natural')
                    ], colors={
                        "border": colors['text'],
                        "primary": colors['primary'],
                        "background": colors['background']
                    })
                ])
            ], className="mb-4")
        ], width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            html.Div(id='tab-content')
        ], width=12)
    ]),
    
    html.Footer([
        html.Hr(),
        html.P("© 2023 Дашборд Байкальской природной территории", 
               className="text-center", style={'color': colors['text']})
    ], className="mt-4")
    
], fluid=True, style={'background-color': colors['background'], 'min-height': '100vh'})

# Callback to update tab content
@app.callback(
    Output('tab-content', 'children'),
    Input('tabs', 'value')
)
def render_content(tab):
    if tab == 'tab-map':
        return render_map_tab()
    elif tab == 'tab-ecology':
        return render_ecology_tab()
    elif tab == 'tab-tourism':
        return render_tourism_tab()
    elif tab == 'tab-natural':
        return render_natural_tab()

def render_map_tab():
    if not GEODATA_AVAILABLE:
        map_warning = "Географические библиотеки не установлены. Отображается упрощенная карта."
        if isinstance(data_files_status["География"], str):
            map_warning += " " + data_files_status["География"]
        
        return dbc.Card([
            dbc.CardBody([
                dbc.Alert(
                    map_warning,
                    color="warning"
                ),
                dcc.Graph(figure=create_simple_map())
            ])
        ])
    
    # Use the detailed map from the map_visualization module if available
    if MAP_MODULE_AVAILABLE:
        try:
            detailed_map = create_detailed_map()
        except Exception as e:
            print(f"Ошибка при создании карты через модуль визуализации: {e}")
            detailed_map = create_simple_map()
    else:
        # Простая карта если модуль недоступен
        try:
            # Проверяем наличие переменной baikal_region в локальной области видимости
            if 'baikal_region' in locals() or 'baikal_region' in globals():
                try:
                    baikal_geojson = json.loads(baikal_region.to_json())
                    
                    detailed_map = px.choropleth_mapbox(
                        geojson=baikal_geojson,
                        locations=baikal_region.index,
                        featureidkey="id",
                        center={"lat": 53.5, "lon": 108},
                        zoom=5,
                        mapbox_style="open-street-map",
                        opacity=0.3
                    )
                    
                    # Добавляем города, если они доступны
                    if 'city_points' in locals() or 'city_points' in globals():
                        detailed_map.add_scattermapbox(
                            lat=city_points.geometry.y,
                            lon=city_points.geometry.x,
                            text=city_points['name'],
                            mode='markers+text',
                            marker=dict(size=10, color=colors['primary']),
                            name='Города'
                        )
                    
                    detailed_map.update_layout(
                        height=800,
                        margin={"r": 0, "t": 30, "l": 0, "b": 0}
                    )
                except Exception as e:
                    print(f"Ошибка при создании карты из геоданных: {e}")
                    detailed_map = create_simple_map()
            else:
                print("Переменная baikal_region не найдена, создаем простую карту")
                detailed_map = create_simple_map()
        except Exception as e:
            print(f"Ошибка при создании простой карты: {e}")
            detailed_map = create_simple_map()
    
    return dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.H4("Карта Байкальской природной территории", className="card-title"),
                    html.P("Интерактивная карта региона с основными географическими объектами", className="card-text"),
                    dcc.Graph(figure=detailed_map, style={'height': '800px'})
                ], width=12)
            ]),
            dbc.Row([
                dbc.Col([
                    html.H5("Информация о регионе", className="mt-4"),
                    html.P([
                        """Байкальская природная территория включает озеро Байкал, водоохранную зону, особо охраняемые природные территории, 
                        прилегающие к озеру Байкал, а также прилегающую к озеру Байкал территорию шириной до 200 километров на запад и северо-запад от него.
                        Озеро Байкал — крупнейший природный резервуар пресной воды (23 тыс. куб. км), что составляет около 19% мировых запасов.
                        """
                    ])
                ], width=12)
            ])
        ])
    ])

def render_ecology_tab():
    panels = []
    
    # Статус доступных данных
    panels.append(
        dbc.Row([
            dbc.Col([
                html.H4("Экологические показатели", className="card-title"),
                html.P("Ключевые экологические индикаторы Байкальской природной территории", className="card-text"),
            ], width=12)
        ])
    )
    
    # Create water level plot if data is available
    if data_files_status["Уровень воды"]:
        try:
            water_fig = px.line(
                water_level_data, 
                x='Год', 
                y='Уровень, см', 
                title='Динамика изменения уровня воды в озере Байкал',
                labels={'Уровень, см': 'Уровень воды (см)', 'Год': 'Год'},
                markers=True,
                color_discrete_sequence=[colors['water']]
            )
            water_fig.update_layout(height=400, hovermode="x unified")
        except Exception as e:
            print(f"Ошибка при создании графика уровня воды: {e}")
            water_fig = create_placeholder_figure("Ошибка при отображении данных об уровне воды")
    else:
        water_fig = create_placeholder_figure("Данные об уровне воды недоступны")
    
    # Create fish catch plot if data is available
    if data_files_status["Вылов рыбы"]:
        try:
            fish_fig = px.bar(
                fish_catch_data,
                x='Год',
                y='Вылов, тонн',
                color='Вид',
                title='Вылов рыбы по видам',
                labels={'Вылов, тонн': 'Вылов (тонн)', 'Год': 'Год', 'Вид': 'Вид рыбы'},
                color_discrete_map={
                    'Омуль': colors['primary'],
                    'Сиг': colors['secondary'],
                    'Хариус': colors['tertiary'],
                    'Осетр': colors['quaternary'],
                    'Другие': colors['quinary']
                }
            )
            fish_fig.update_layout(height=400, hovermode="x unified")
        except Exception as e:
            print(f"Ошибка при создании графика вылова рыбы: {e}")
            fish_fig = create_placeholder_figure("Ошибка при отображении данных о вылове рыбы")
    else:
        fish_fig = create_placeholder_figure("Данные о вылове рыбы недоступны")
    
    panels.append(
        dbc.Row([
            dbc.Col([
                dcc.Graph(figure=water_fig)
            ], width=12, lg=6),
            dbc.Col([
                dcc.Graph(figure=fish_fig)
            ], width=12, lg=6)
        ])
    )
    
    # Create combined ecological trends if data is available
    if DATA_ANALYSIS_MODULE_AVAILABLE and data_files_status["Уровень воды"] and data_files_status["Вылов рыбы"]:
        try:
            combined_eco_fig = create_combined_ecological_trends()
            panels.append(
                dbc.Row([
                    dbc.Col([
                        dcc.Graph(figure=combined_eco_fig)
                    ], width=12)
                ])
            )
        except Exception as e:
            print(f"Ошибка при создании комбинированного графика: {e}")
    
    # Create air quality figure if data is available
    if data_files_status["Качество воздуха"]:
        try:
            air_fig = px.line(
                air_quality_data,
                x='date',
                y='Значение',
                title='Среднемесячная концентрация PM2.5 в атмосфере',
                labels={'Значение': 'Концентрация PM2.5 (мкг/м³)', 'date': 'Дата'},
                color_discrete_sequence=[colors['tertiary']]
            )
            air_fig.update_layout(height=400, hovermode="x unified")
            
            panels.append(
                dbc.Row([
                    dbc.Col([
                        dcc.Graph(figure=air_fig)
                    ], width=12)
                ])
            )
        except Exception as e:
            print(f"Ошибка при создании графика качества воздуха: {e}")
    
    return dbc.Card([
        dbc.CardBody(panels)
    ])

def render_tourism_tab():
    panels = []
    
    panels.append(
        dbc.Row([
            dbc.Col([
                html.H4("Туристическая активность", className="card-title"),
                html.P("Анализ туристического потока в Байкальском регионе", className="card-text"),
            ], width=12)
        ])
    )
    
    if not data_files_status["Туризм"]:
        panels.append(
            dbc.Row([
                dbc.Col([
                    dbc.Alert(
                        "Данные о туризме недоступны. Проверьте наличие файла 'Турпоток.xlsx' в папке 'Туризм'.",
                        color="warning"
                    ),
                    dcc.Graph(figure=create_placeholder_figure("Данные о туризме недоступны"))
                ], width=12)
            ])
        )
    else:
        try:
            # Create tourism plot
            tourism_fig = px.bar(
                tourism_data,
                x='Год',
                y='Количество туристов, тыс. чел.',
                title='Динамика туристического потока в регионе Байкала',
                labels={'Количество туристов, тыс. чел.': 'Количество туристов (тыс. чел.)', 'Год': 'Год'},
                color_discrete_sequence=[colors['primary']]
            )
            tourism_fig.update_layout(height=500, hovermode="x unified")
            
            # Create growth rate plot
            growth_fig = px.line(
                tourism_data.dropna(),
                x='Год',
                y='growth_rate',
                title='Темпы роста туристического потока (%)',
                labels={'growth_rate': 'Рост (% к предыдущему году)', 'Год': 'Год'},
                markers=True,
                color_discrete_sequence=[colors['tertiary']]
            )
            growth_fig.update_layout(height=500, hovermode="x unified")
            
            panels.append(
                dbc.Row([
                    dbc.Col([
                        dcc.Graph(figure=tourism_fig)
                    ], width=12, lg=6),
                    dbc.Col([
                        dcc.Graph(figure=growth_fig)
                    ], width=12, lg=6)
                ])
            )
            
            # Get tourism forecast if available
            if DATA_ANALYSIS_MODULE_AVAILABLE:
                try:
                    forecast_fig = create_tourism_forecast()
                    panels.append(
                        dbc.Row([
                            dbc.Col([
                                dcc.Graph(figure=forecast_fig)
                            ], width=12)
                        ])
                    )
                except Exception as e:
                    print(f"Ошибка при создании прогноза туризма: {e}")
        except Exception as e:
            print(f"Ошибка при отображении данных о туризме: {e}")
            panels.append(
                dbc.Row([
                    dbc.Col([
                        dbc.Alert(
                            f"Ошибка при отображении данных о туризме: {str(e)}",
                            color="danger"
                        ),
                        dcc.Graph(figure=create_placeholder_figure("Ошибка отображения данных о туризме"))
                    ], width=12)
                ])
            )
        
        panels.append(
            dbc.Row([
                dbc.Col([
                    html.H5("Развитие туризма в регионе", className="mt-4"),
                    html.P([
                        """Байкал является одним из наиболее популярных туристических направлений в России.
                        Регион предлагает различные виды туризма: экологический, спортивный, культурно-познавательный, 
                        лечебно-оздоровительный и другие. Основные туристические центры сосредоточены в Иркутской области и Республике Бурятия."""
                    ])
                ], width=12)
            ])
        )
    
    return dbc.Card([
        dbc.CardBody(panels)
    ])

def render_natural_tab():
    panels = []
    
    panels.append(
        dbc.Row([
            dbc.Col([
                html.H4("Природные явления", className="card-title"),
                html.P("Землетрясения и пожары в Байкальском регионе", className="card-text"),
            ], width=12)
        ])
    )
    
    # Нет географических библиотек - показываем предупреждение и предлагаем альтернативы
    if not GEODATA_AVAILABLE:
        panels.append(
            dbc.Row([
                dbc.Col([
                    dbc.Alert(
                        [
                            html.H5("Географические библиотеки не установлены"),
                            html.P("Для отображения данных о землетрясениях и пожарах требуется установка географических библиотек (geopandas)."),
                            html.P("Возможные решения:"),
                            html.Ul([
                                html.Li("Установите библиотеки через conda: conda install -c conda-forge geopandas"),
                                html.Li("Используйте упрощенную версию дашборда (запустите app_simple.py)")
                            ])
                        ],
                        color="warning"
                    ),
                    dcc.Graph(figure=create_placeholder_figure("Географические данные недоступны"))
                ], width=12)
            ])
        )
        return dbc.Card([dbc.CardBody(panels)])
    
    # Проверяем наличие данных о землетрясениях и генерируем их при необходимости
    if not data_files_status["Землетрясения"]:
        panels.append(
            dbc.Row([
                dbc.Col([
                    dbc.Alert(
                        [
                            html.H5("Данные о землетрясениях отсутствуют"),
                            html.P("Попытка автоматического создания тестовых данных...")
                        ],
                        color="info", 
                        id="earthquake-data-alert"
                    )
                ], width=12)
            ])
        )
        
        try:
            print("Генерация данных о землетрясениях...")
            import generate_test_data
            generate_test_data.generate_earthquake_data()
            print("Данные о землетрясениях созданы.")
            
            # Пробуем загрузить созданные данные
            if os.path.exists('Землетрясения/earthquakes_BR_1923-2023.geojson'):
                earthquake_data = gpd.read_file('Землетрясения/earthquakes_BR_1923-2023.geojson')
                earthquake_data['year'] = pd.to_datetime(earthquake_data['date']).dt.year
                earthquake_data['decade'] = (earthquake_data['year'] // 10) * 10
                data_files_status["Землетрясения"] = True
                print("Данные о землетрясениях успешно загружены после генерации.")
        except Exception as e:
            print(f"Ошибка при генерации данных о землетрясениях: {e}")
            panels.append(
                dbc.Row([
                    dbc.Col([
                        dbc.Alert(
                            f"Не удалось создать данные о землетрясениях: {str(e)}",
                            color="danger"
                        ),
                        dcc.Graph(figure=create_placeholder_figure("Данные о землетрясениях недоступны"))
                    ], width=12)
                ])
            )
    
    # Visualize earthquake data if available
    if data_files_status["Землетрясения"]:
        try:
            # Process earthquake data for visualization
            eq_by_decade = earthquake_data.groupby('decade').size().reset_index(name='count')
            
            # Create earthquake frequency plot
            eq_fig = px.bar(
                eq_by_decade,
                x='decade',
                y='count',
                title='Частота землетрясений по десятилетиям',
                labels={'count': 'Количество землетрясений', 'decade': 'Десятилетие'},
                color_discrete_sequence=[colors['tertiary']]
            )
            eq_fig.update_layout(height=400, hovermode="x unified")
            
            # Create earthquake magnitude plot
            eq_mag_fig = px.scatter(
                earthquake_data,
                x='date',
                y='mag',
                size='mag',
                color='mag',
                title='Магнитуда землетрясений по годам',
                labels={'mag': 'Магнитуда (ML)', 'date': 'Дата'},
                color_continuous_scale=px.colors.sequential.Reds
            )
            eq_mag_fig.update_layout(height=400, hovermode="closest")
            
            panels.append(
                dbc.Row([
                    dbc.Col([
                        dcc.Graph(figure=eq_fig)
                    ], width=12, lg=6),
                    dbc.Col([
                        dcc.Graph(figure=eq_mag_fig)
                    ], width=12, lg=6)
                ])
            )
            
            # Создаем тепловую карту землетрясений вручную, если модуль недоступен
            if not MAP_MODULE_AVAILABLE:
                try:
                    eq_heatmap = px.density_mapbox(
                        earthquake_data,
                        lat=earthquake_data.geometry.y,
                        lon=earthquake_data.geometry.x,
                        z='mag',
                        radius=10,
                        center=dict(lat=53.5, lon=108),
                        zoom=5,
                        mapbox_style="open-street-map",
                        title="Тепловая карта сейсмической активности"
                    )
                    eq_heatmap.update_layout(height=600, margin={"r": 0, "t": 30, "l": 0, "b": 0})
                    
                    panels.append(
                        dbc.Row([
                            dbc.Col([
                                dcc.Graph(figure=eq_heatmap)
                            ], width=12)
                        ])
                    )
                except Exception as e:
                    print(f"Ошибка при создании тепловой карты землетрясений: {e}")
            # Use the earthquake heatmap from the map_visualization module if available
            elif MAP_MODULE_AVAILABLE:
                try:
                    eq_heatmap = create_earthquake_heatmap()
                    panels.append(
                        dbc.Row([
                            dbc.Col([
                                dcc.Graph(figure=eq_heatmap)
                            ], width=12)
                        ])
                    )
                except Exception as e:
                    print(f"Ошибка при создании тепловой карты землетрясений через модуль: {e}")
                    try:
                        # Запасной вариант, если модуль не смог создать карту
                        eq_heatmap = px.density_mapbox(
                            earthquake_data,
                            lat=earthquake_data.geometry.y,
                            lon=earthquake_data.geometry.x,
                            z='mag',
                            radius=10,
                            center=dict(lat=53.5, lon=108),
                            zoom=5,
                            mapbox_style="open-street-map",
                            title="Тепловая карта сейсмической активности"
                        )
                        eq_heatmap.update_layout(height=600, margin={"r": 0, "t": 30, "l": 0, "b": 0})
                        
                        panels.append(
                            dbc.Row([
                                dbc.Col([
                                    dcc.Graph(figure=eq_heatmap)
                                ], width=12)
                            ])
                        )
                    except Exception as e2:
                        print(f"Ошибка при создании запасной тепловой карты: {e2}")
        except Exception as e:
            print(f"Ошибка при отображении данных о землетрясениях: {e}")
            panels.append(
                dbc.Row([
                    dbc.Col([
                        dbc.Alert(
                            f"Ошибка при отображении данных о землетрясениях: {str(e)}",
                            color="danger"
                        ),
                        dcc.Graph(figure=create_placeholder_figure("Ошибка при отображении данных о землетрясениях"))
                    ], width=12)
                ])
            )
    
    # Проверяем наличие данных о пожарах и генерируем их при необходимости
    if not data_files_status["Пожары"]:
        panels.append(
            dbc.Row([
                dbc.Col([
                    dbc.Alert(
                        [
                            html.H5("Данные о пожарах отсутствуют"),
                            html.P("Попытка автоматического создания тестовых данных...")
                        ],
                        color="info", 
                        id="fire-data-alert"
                    )
                ], width=12)
            ])
        )
        
        try:
            print("Генерация данных о пожарах...")
            import generate_test_data
            generate_test_data.generate_fire_data()
            print("Данные о пожарах созданы.")
            
            # Пробуем загрузить созданные данные
            if os.path.exists('Пожары/fires_BR_2011-2021.geojson'):
                fire_data = gpd.read_file('Пожары/fires_BR_2011-2021.geojson', rows=1000)
                fire_data['year'] = pd.to_datetime(fire_data['date']).dt.year
                data_files_status["Пожары"] = True
                print("Данные о пожарах успешно загружены после генерации.")
        except Exception as e:
            print(f"Ошибка при генерации данных о пожарах: {e}")
            panels.append(
                dbc.Row([
                    dbc.Col([
                        dbc.Alert(
                            f"Не удалось создать данные о пожарах: {str(e)}",
                            color="danger"
                        )
                    ], width=12)
                ])
            )
    
    # Process fire data for visualization if available
    if data_files_status["Пожары"]:
        try:
            fire_by_year = fire_data.groupby('year').size().reset_index(name='count')
            
            fires_fig = px.bar(
                fire_by_year,
                x='year',
                y='count',
                title='Количество пожаров по годам (выборка)',
                labels={'count': 'Количество пожаров', 'year': 'Год'},
                color_discrete_sequence=[colors['fire']]
            )
            fires_fig.update_layout(height=400, hovermode="x unified")
            
            panels.append(
                dbc.Row([
                    dbc.Col([
                        dcc.Graph(figure=fires_fig)
                    ], width=12)
                ])
            )
            
            # Добавляем тепловую карту пожаров
            try:
                fire_heatmap = px.density_mapbox(
                    fire_data,
                    lat=fire_data.geometry.y,
                    lon=fire_data.geometry.x,
                    z=None,
                    radius=8,
                    center=dict(lat=53.5, lon=108),
                    zoom=5,
                    mapbox_style="open-street-map",
                    title="Карта распределения пожаров"
                )
                fire_heatmap.update_layout(height=600, margin={"r": 0, "t": 30, "l": 0, "b": 0})
                
                panels.append(
                    dbc.Row([
                        dbc.Col([
                            dcc.Graph(figure=fire_heatmap)
                        ], width=12)
                    ])
                )
            except Exception as e:
                print(f"Ошибка при создании карты пожаров: {e}")
        except Exception as e:
            print(f"Ошибка при отображении данных о пожарах: {e}")
            panels.append(
                dbc.Row([
                    dbc.Col([
                        dbc.Alert(
                            f"Ошибка при отображении данных о пожарах: {str(e)}",
                            color="danger"
                        )
                    ], width=12)
                ])
            )
    
    return dbc.Card([
        dbc.CardBody(panels)
    ])

if __name__ == '__main__':
    try:
        print("Запуск дашборда Байкальской природной территории...")
        app.run_server(debug=True)
    except Exception as e:
        print(f"Ошибка при запуске приложения: {e}")
        traceback.print_exc() 