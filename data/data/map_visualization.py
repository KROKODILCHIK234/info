import os
import traceback
import warnings

# Подавление предупреждений
warnings.filterwarnings('ignore')

try:
    import plotly.express as px
    import plotly.graph_objects as go
    import geopandas as gpd
    import pandas as pd
    import json
    from shapely.geometry import shape
    
    # Проверяем, что geopandas доступен
    DEPENDENCIES_AVAILABLE = True
    print("Зависимости для карт успешно импортированы.")
except ImportError as e:
    print(f"Ошибка импорта зависимостей в map_visualization.py: {e}")
    DEPENDENCIES_AVAILABLE = False

def create_placeholder_map(message="Карта недоступна"):
    """Создает заглушку для карты при ошибках."""
    try:
        import plotly.graph_objects as go
        fig = go.Figure()
        fig.add_annotation(
            text=message,
            showarrow=False,
            font=dict(size=20, color="#6c757d")
        )
        fig.update_layout(
            height=800,
            paper_bgcolor="#f8f9fa",
            plot_bgcolor="#f8f9fa"
        )
        return fig
    except ImportError:
        # Если даже plotly недоступен, вернем None
        return None

def create_simple_map():
    """
    Создает простую карту Байкальского региона без использования геоданных.
    Используется как запасной вариант, если geopandas недоступен.
    """
    try:
        # Координаты основных городов
        cities = {
            'Иркутск': {'lat': 52.3, 'lon': 104.3},
            'Улан-Удэ': {'lat': 51.8, 'lon': 107.6},
            'Северобайкальск': {'lat': 55.6, 'lon': 109.3},
            'Листвянка': {'lat': 51.9, 'lon': 104.8},
            'Ольхон': {'lat': 53.2, 'lon': 107.4},
            'Байкальск': {'lat': 51.5, 'lon': 104.1}
        }
        
        # Создаем базовую карту
        fig = go.Figure()
        
        # Добавляем города как маркеры
        fig.add_trace(go.Scattermapbox(
            lat=[city['lat'] for city in cities.values()],
            lon=[city['lon'] for city in cities.values()],
            mode='markers+text',
            marker=dict(size=12, color='#dc3545', symbol='circle'),
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
            line=dict(width=3, color='#007bff'),
            fill='toself',
            fillcolor='rgba(0, 123, 255, 0.3)',
            name='Озеро Байкал'
        ))
        
        # Добавляем основные реки (упрощенно)
        rivers = [
            {
                'name': 'р. Селенга',
                'lats': [52.2, 52.0, 51.8, 51.5],
                'lons': [106.0, 106.5, 107.0, 107.5]
            },
            {
                'name': 'р. Ангара',
                'lats': [51.9, 52.3, 52.5, 52.7],
                'lons': [104.8, 104.3, 103.8, 103.3]
            }
        ]
        
        for river in rivers:
            fig.add_trace(go.Scattermapbox(
                lat=river['lats'],
                lon=river['lons'],
                mode='lines',
                line=dict(width=2, color='#0db7ed'),
                name=river['name']
            ))
        
        # Настраиваем вид карты
        fig.update_layout(
            mapbox=dict(
                style="carto-positron",
                center=dict(lat=53.5, lon=108),
                zoom=5
            ),
            height=800,
            margin={"r": 0, "t": 30, "l": 0, "b": 0},
            paper_bgcolor="#f8f9fa",
            font=dict(color="#343a40"),
            legend=dict(
                bgcolor="#f8f9fa",
                bordercolor="#007bff",
                borderwidth=2,
                font=dict(size=12, color="#343a40"),
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            )
        )
        
        return fig
    except Exception as e:
        print(f"Ошибка при создании простой карты: {e}")
        return create_placeholder_map("Ошибка при создании карты")

def create_detailed_map():
    """
    Создает интерактивную карту Байкальской природной территории
    с отображением городов и других географических объектов.
    
    Вместо использования fiona.path, применяет альтернативные методы.
    """
    if not DEPENDENCIES_AVAILABLE:
        return create_simple_map()
    
    try:
        # Проверяем наличие файлов географических данных
        if not os.path.exists('География/baikal_simply.geojson'):
            print("Файл baikal_simply.geojson не найден")
            return create_simple_map()
        
        # Загружаем данные о регионе без использования gpd.read_file
        try:
            # Альтернативный вариант загрузки геоданных без прямого использования fiona.path
            with open('География/baikal_simply.geojson', 'r', encoding='utf-8') as f:
                baikal_geojson = json.load(f)
            
            # Создаем базовую карту
            fig = px.choropleth_mapbox(
                geojson=baikal_geojson,
                locations=[i for i in range(len(baikal_geojson['features']))],
                color_discrete_sequence=["rgba(0, 123, 255, 0.3)"],  # Синий цвет для Байкала
                mapbox_style="carto-positron",
                zoom=5,
                center={"lat": 53.5, "lon": 108},
                opacity=0.3,
                featureidkey='id'
            )
            
            # Добавляем города, если доступны
            if os.path.exists('География/city_points.geojson'):
                try:
                    with open('География/city_points.geojson', 'r', encoding='utf-8') as f:
                        city_points_geojson = json.load(f)
                    
                    city_lats = []
                    city_lons = []
                    city_names = []
                    
                    for feature in city_points_geojson['features']:
                        geom = feature['geometry']
                        if geom['type'] == 'Point':
                            city_lons.append(geom['coordinates'][0])
                            city_lats.append(geom['coordinates'][1])
                            city_names.append(feature['properties'].get('name', 'Город'))
                    
                    fig.add_trace(
                        go.Scattermapbox(
                            lat=city_lats,
                            lon=city_lons,
                            text=city_names,
                            mode='markers+text',
                            marker=dict(size=12, color='#dc3545', symbol='circle'),
                            textposition="top center",
                            name='Города'
                        )
                    )
                except Exception as e:
                    print(f"Ошибка при добавлении городов: {e}")
            
            # Настройка карты
            fig.update_layout(
                title="Карта Байкальской природной территории",
                height=800,
                margin={"r": 0, "t": 30, "l": 0, "b": 0},
                paper_bgcolor="#f8f9fa",
                font=dict(color="#343a40"),
                legend=dict(
                    bgcolor="#f8f9fa",
                    bordercolor="#007bff",
                    borderwidth=2,
                    font=dict(size=12, color="#343a40"),
                    yanchor="top",
                    y=0.99,
                    xanchor="left",
                    x=0.01
                )
            )
            
            return fig
        
        except Exception as e:
            print(f"Ошибка при загрузке географических данных: {e}")
            return create_simple_map()
    
    except Exception as e:
        print(f"Ошибка при создании карты: {e}")
        traceback.print_exc()
        return create_simple_map()

def create_earthquake_heatmap():
    """
    Создает тепловую карту сейсмической активности в регионе Байкала
    без использования fiona.path.
    """
    if not DEPENDENCIES_AVAILABLE:
        return create_simple_map()
    
    try:
        # Проверяем наличие файла данных о землетрясениях
        if not os.path.exists('Землетрясения/earthquakes_BR_1923-2023.geojson'):
            print("Файл earthquakes_BR_1923-2023.geojson не найден")
            return create_placeholder_map("Данные о землетрясениях недоступны")
        
        # Загружаем данные о землетрясениях без прямого использования gpd.read_file
        try:
            with open('Землетрясения/earthquakes_BR_1923-2023.geojson', 'r', encoding='utf-8') as f:
                eq_geojson = json.load(f)
            
            eq_lats = []
            eq_lons = []
            eq_mags = []
            
            for feature in eq_geojson['features']:
                geom = feature['geometry']
                if geom['type'] == 'Point':
                    eq_lons.append(geom['coordinates'][0])
                    eq_lats.append(geom['coordinates'][1])
                    eq_mags.append(feature['properties'].get('mag', 1))
            
            # Создаем тепловую карту
            fig = px.density_mapbox(
                lat=eq_lats,
                lon=eq_lons,
                z=eq_mags,
                radius=10,
                center={"lat": 53.5, "lon": 108},
                zoom=5,
                mapbox_style="carto-positron",
                title="Тепловая карта сейсмической активности",
                color_continuous_scale="Reds"
            )
            
            # Настройка карты
            fig.update_layout(
                height=600,
                margin={"r": 0, "t": 50, "l": 0, "b": 0},
                paper_bgcolor="#f8f9fa",
                font=dict(color="#343a40")
            )
            
            return fig
        
        except Exception as e:
            print(f"Ошибка при загрузке данных о землетрясениях: {e}")
            return create_placeholder_map(f"Ошибка при создании тепловой карты: {str(e)}")
    
    except Exception as e:
        print(f"Ошибка при создании тепловой карты землетрясений: {e}")
        traceback.print_exc()
        return create_placeholder_map(f"Ошибка при создании тепловой карты: {str(e)}")

if __name__ == "__main__":
    # This allows you to test the maps independently
    try:
        fig = create_detailed_map()
        # You can save the figure to an HTML file for viewing
        if DEPENDENCIES_AVAILABLE:
            from plotly.offline import plot
            plot(fig, filename='detailed_map.html')
            print("Карта сохранена в файл detailed_map.html")
        else:
            print("Невозможно сохранить карту из-за отсутствия необходимых зависимостей")
    except Exception as e:
        print(f"Ошибка при тестировании модуля: {e}")
        traceback.print_exc() 