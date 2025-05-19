import os
import traceback
import warnings

# Подавление предупреждений
warnings.filterwarnings('ignore')

# Проверка доступности необходимых библиотек
try:
    import pandas as pd
    import numpy as np
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    BASIC_DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    print(f"Ошибка импорта базовых зависимостей в data_analysis.py: {e}")
    BASIC_DEPENDENCIES_AVAILABLE = False

# Проверка доступности geopandas для геоданных
try:
    import geopandas as gpd
    GEODATA_DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    print(f"Ошибка импорта geopandas в data_analysis.py: {e}")
    GEODATA_DEPENDENCIES_AVAILABLE = False

# Проверка доступности scikit-learn для моделей прогнозирования
try:
    from sklearn.linear_model import LinearRegression
    SKLEARN_AVAILABLE = True
except ImportError as e:
    print(f"Ошибка импорта scikit-learn в data_analysis.py: {e}")
    SKLEARN_AVAILABLE = False

def create_placeholder_figure(title="Данные недоступны"):
    """Создает заглушку для графика при ошибках."""
    if not BASIC_DEPENDENCIES_AVAILABLE:
        print("Невозможно создать даже заглушку - не установлен plotly")
        return None
        
    fig = go.Figure()
    fig.add_annotation(
        text=title,
        showarrow=False,
        font=dict(size=20)
    )
    fig.update_layout(height=400)
    return fig

def load_and_prepare_tourism_data(filepath='Туризм/Турпоток.xlsx'):
    """
    Load and prepare tourism data for visualization.
    
    Returns:
        DataFrame: Prepared tourism data
    """
    if not BASIC_DEPENDENCIES_AVAILABLE:
        print("Не установлены необходимые библиотеки для загрузки данных туризма")
        return pd.DataFrame() if 'pd' in globals() else None
        
    try:
        if not os.path.exists(filepath):
            print(f"Файл данных туризма не найден: {filepath}")
            return pd.DataFrame()
            
        df = pd.read_excel(filepath)
        df['Год'] = df['Год'].astype(str)
        
        # Calculate year-over-year growth rate
        df['growth_rate'] = df['Количество туристов, тыс. чел.'].pct_change() * 100
        
        return df
    except Exception as e:
        print(f"Ошибка загрузки данных туризма: {e}")
        traceback.print_exc()
        return pd.DataFrame()

def load_and_prepare_water_data(filepath='Экология/Уровень воды.xlsx'):
    """
    Load and prepare water level data for visualization.
    
    Returns:
        DataFrame: Prepared water level data
    """
    if not BASIC_DEPENDENCIES_AVAILABLE:
        print("Не установлены необходимые библиотеки для загрузки данных об уровне воды")
        return pd.DataFrame() if 'pd' in globals() else None
        
    try:
        if not os.path.exists(filepath):
            print(f"Файл данных об уровне воды не найден: {filepath}")
            return pd.DataFrame()
            
        df = pd.read_excel(filepath)
        return df
    except Exception as e:
        print(f"Ошибка загрузки данных об уровне воды: {e}")
        traceback.print_exc()
        return pd.DataFrame()

def load_and_prepare_fish_data(filepath='Леса и животные/Вылов рыбы.xlsx'):
    """
    Load and prepare fish catch data for visualization.
    
    Returns:
        DataFrame: Prepared fish catch data
    """
    if not BASIC_DEPENDENCIES_AVAILABLE:
        print("Не установлены необходимые библиотеки для загрузки данных о вылове рыбы")
        return pd.DataFrame() if 'pd' in globals() else None
        
    try:
        if not os.path.exists(filepath):
            print(f"Файл данных о вылове рыбы не найден: {filepath}")
            return pd.DataFrame()
            
        df = pd.read_excel(filepath)
        return df
    except Exception as e:
        print(f"Ошибка загрузки данных о вылове рыбы: {e}")
        traceback.print_exc()
        return pd.DataFrame()

def load_and_prepare_air_quality_data():
    """
    Загружает и подготавливает данные о качестве воздуха с корректной обработкой дат
    """
    filepath = 'Экология/Атмосфера/PM2,5.csv'
    
    if not os.path.exists(filepath):
        print(f"Файл {filepath} не найден")
        return pd.DataFrame()
    
    try:
        # Загружаем данные с указанием разделителя
        df = pd.read_csv(filepath, delimiter=';')
        
        # Пробуем разные форматы дат с обработкой ошибок
        try:
            # Сначала пытаемся с русским форматом DD.MM.YYYY
            df['date'] = pd.to_datetime(df['Дата/время'], format="%d.%m.%Y %H:%M:%S", errors='coerce')
        except Exception:
            try:
                # Затем пробуем автоопределение с dayfirst=True
                df['date'] = pd.to_datetime(df['Дата/время'], dayfirst=True, errors='coerce')
            except Exception:
                # В крайнем случае используем mixed формат
                df['date'] = pd.to_datetime(df['Дата/время'], format='mixed', dayfirst=True, errors='coerce')
        
        # Отбрасываем строки с недопустимыми датами
        df = df.dropna(subset=['date'])
        
        if df.empty:
            print("После обработки дат все строки признаны недопустимыми")
            return pd.DataFrame()
        
        # Группируем по месяцам
        df['month'] = df['date'].dt.month
        df['year'] = df['date'].dt.year
        
        # Агрегируем по месяцам и годам
        monthly_data = df.groupby(['year', 'month'])['Значение'].mean().reset_index()
        monthly_data['date'] = pd.to_datetime(monthly_data[['year', 'month']].assign(day=1))
        
        return monthly_data
    
    except Exception as e:
        print(f"Ошибка при загрузке данных качества воздуха: {e}")
        return pd.DataFrame()

def load_and_prepare_earthquake_data(filepath='Землетрясения/earthquakes_BR_1923-2023.geojson'):
    """
    Load and prepare earthquake data for visualization.
    
    Returns:
        GeoDataFrame: Prepared earthquake data
    """
    if not GEODATA_DEPENDENCIES_AVAILABLE:
        print("Не установлены необходимые библиотеки для загрузки данных о землетрясениях")
        return None
        
    try:
        if not os.path.exists(filepath):
            print(f"Файл данных о землетрясениях не найден: {filepath}")
            return None
            
        gdf = gpd.read_file(filepath)
        gdf['year'] = pd.to_datetime(gdf['date']).dt.year
        gdf['decade'] = (gdf['year'] // 10) * 10
        
        return gdf
    except Exception as e:
        print(f"Ошибка загрузки данных о землетрясениях: {e}")
        traceback.print_exc()
        return None

def load_and_prepare_fire_data(filepath='Пожары/fires_BR_2011-2021.geojson', sample_size=1000):
    """
    Load and prepare fire data for visualization.
    
    Args:
        filepath (str): Path to the fire data file
        sample_size (int): Number of rows to sample to avoid memory issues
        
    Returns:
        GeoDataFrame: Prepared fire data
    """
    if not GEODATA_DEPENDENCIES_AVAILABLE:
        print("Не установлены необходимые библиотеки для загрузки данных о пожарах")
        return None
        
    try:
        if not os.path.exists(filepath):
            print(f"Файл данных о пожарах не найден: {filepath}")
            return None
            
        gdf = gpd.read_file(filepath, rows=sample_size)
        gdf['year'] = pd.to_datetime(gdf['date']).dt.year
        
        return gdf
    except Exception as e:
        print(f"Ошибка загрузки данных о пожарах: {e}")
        traceback.print_exc()
        return None

def create_combined_ecological_trends():
    """
    Create a combined visualization of multiple ecological trends.
    
    Returns:
        Figure: Plotly figure with combined ecological trends
    """
    if not BASIC_DEPENDENCIES_AVAILABLE:
        return create_placeholder_figure("Не установлены необходимые библиотеки для создания визуализации")
        
    try:
        # Проверка наличия файлов данных
        if not os.path.exists('Экология/Уровень воды.xlsx') or not os.path.exists('Леса и животные/Вылов рыбы.xlsx'):
            missing_files = []
            if not os.path.exists('Экология/Уровень воды.xlsx'):
                missing_files.append('Экология/Уровень воды.xlsx')
            if not os.path.exists('Леса и животные/Вылов рыбы.xlsx'):
                missing_files.append('Леса и животные/Вылов рыбы.xlsx')
            return create_placeholder_figure(f"Отсутствуют файлы: {', '.join(missing_files)}")
        
        water_data = load_and_prepare_water_data()
        fish_data = load_and_prepare_fish_data()
        
        if water_data.empty or fish_data.empty:
            return create_placeholder_figure("Данные об уровне воды или вылове рыбы недоступны")
        
        # Create figure with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Add water level trace
        fig.add_trace(
            go.Scatter(
                x=water_data['Год'],
                y=water_data['Уровень, см'],
                name="Уровень воды (см)",
                line=dict(color="#1f77b4", width=3)
            ),
            secondary_y=False,
        )
        
        # Add fish catch total by year
        fish_by_year = fish_data.groupby('Год')['Вылов, тонн'].sum().reset_index()
        
        fig.add_trace(
            go.Scatter(
                x=fish_by_year['Год'],
                y=fish_by_year['Вылов, тонн'],
                name="Общий вылов рыбы (тонн)",
                line=dict(color="#d62728", width=3, dash='dot')
            ),
            secondary_y=True,
        )
        
        # Set titles
        fig.update_layout(
            title_text="Сопоставление уровня воды и вылова рыбы",
            height=600,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        # Set y-axes titles
        fig.update_yaxes(title_text="Уровень воды (см)", secondary_y=False)
        fig.update_yaxes(title_text="Вылов рыбы (тонн)", secondary_y=True)
        
        return fig
    except Exception as e:
        print(f"Ошибка создания графика экологических трендов: {e}")
        traceback.print_exc()
        return create_placeholder_figure(f"Ошибка при обработке данных: {str(e)}")

def create_tourism_forecast():
    """
    Create a tourism forecast visualization based on historical data.
    
    Returns:
        Figure: Plotly figure with tourism forecast
    """
    if not BASIC_DEPENDENCIES_AVAILABLE:
        return create_placeholder_figure("Не установлены необходимые библиотеки для создания визуализации")
        
    if not SKLEARN_AVAILABLE:
        return create_placeholder_figure("Для создания прогноза необходимо установить scikit-learn")
        
    try:
        # Проверка наличия файла данных
        if not os.path.exists('Туризм/Турпоток.xlsx'):
            return create_placeholder_figure("Отсутствует файл данных о туризме")
        
        tourism_data = load_and_prepare_tourism_data()
        
        if tourism_data.empty:
            return create_placeholder_figure("Данные о туризме недоступны или пусты")
        
        # Convert year to numeric for regression
        tourism_data['Year_num'] = tourism_data['Год'].astype(int)
        
        # Get the most recent years for forecasting
        if len(tourism_data) < 5:
            recent_years = tourism_data
        else:
            recent_years = tourism_data.sort_values('Year_num').tail(10)
        
        # Simple linear regression for forecasting
        x = recent_years['Year_num'].values.reshape(-1, 1)
        y = recent_years['Количество туристов, тыс. чел.'].values
        
        # Calculate slope and intercept using scikit-learn
        model = LinearRegression()
        model.fit(x, y)
        
        # Create future years for prediction
        future_years = np.array(range(recent_years['Year_num'].max() + 1, 
                                      recent_years['Year_num'].max() + 6)).reshape(-1, 1)
        
        # Predict future values
        future_values = model.predict(future_years)
        
        # Create a DataFrame for the forecast
        forecast_df = pd.DataFrame({
            'Год': [str(year[0]) for year in future_years],
            'Количество туристов, тыс. чел.': future_values,
            'Тип': ['Прогноз'] * len(future_years)
        })
        
        # Add type column to original data
        tourism_data['Тип'] = 'Фактические данные'
        
        # Combine actual and forecast data
        combined_df = pd.concat([
            tourism_data[['Год', 'Количество туристов, тыс. чел.', 'Тип']], 
            forecast_df
        ])
        
        # Create the figure
        fig = px.bar(
            combined_df,
            x='Год',
            y='Количество туристов, тыс. чел.',
            color='Тип',
            title='Динамика и прогноз туристического потока в регионе Байкала',
            labels={'Количество туристов, тыс. чел.': 'Количество туристов (тыс. чел.)', 'Год': 'Год'},
            color_discrete_map={
                'Фактические данные': '#1f77b4',
                'Прогноз': '#ff7f0e'
            },
            barmode='group'
        )
        
        fig.update_layout(height=600, hovermode="x unified")
        
        return fig
    except Exception as e:
        print(f"Ошибка создания прогноза туристического потока: {e}")
        traceback.print_exc()
        return create_placeholder_figure(f"Ошибка при создании прогноза: {str(e)}")

if __name__ == "__main__":
    # Test the functions
    try:
        print("Тестирование функций анализа данных...")
        
        water_data = load_and_prepare_water_data()
        print(f"Данные об уровне воды загружены: {len(water_data)} строк")
        
        tourism_data = load_and_prepare_tourism_data()
        print(f"Данные о туризме загружены: {len(tourism_data)} строк")
        
        print("Тестирование завершено успешно")
    except Exception as e:
        print(f"Ошибка при тестировании модуля: {e}")
        traceback.print_exc() 