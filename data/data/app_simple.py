import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import warnings
import os
from dash_bootstrap_templates import load_figure_template

# Подавление предупреждений
warnings.filterwarnings('ignore')

# Проверка наличия данных
required_files = [
    'Туризм/Турпоток.xlsx',
    'Экология/Уровень воды.xlsx',
    'Леса и животные/Вылов рыбы.xlsx'
]

# Проверка наличия тестовых данных и их генерация при необходимости
missing_files = [f for f in required_files if not os.path.exists(f)]
if missing_files:
    print(f"Отсутствуют следующие файлы: {', '.join(missing_files)}")
    print("Запуск генерации тестовых данных...")
    
    try:
        import generate_test_data
        generate_test_data.generate_tourism_data()
        generate_test_data.generate_water_level_data()
        generate_test_data.generate_fish_catch_data()
        generate_test_data.generate_air_quality_data()
        print("Тестовые данные успешно сгенерированы.")
    except Exception as e:
        print(f"Ошибка при генерации тестовых данных: {e}")

# Инициализация данных
tourism_data = pd.DataFrame()
water_level_data = pd.DataFrame()
fish_catch_data = pd.DataFrame()
air_quality_data = pd.DataFrame()

# Статус загрузки данных
data_files_status = {
    "Туризм": False,
    "Уровень воды": False,
    "Вылов рыбы": False,
    "Качество воздуха": False
}

# Загрузка данных
try:
    if os.path.exists('Туризм/Турпоток.xlsx'):
        tourism_data = pd.read_excel('Туризм/Турпоток.xlsx')
        tourism_data['Год'] = tourism_data['Год'].astype(str)
        tourism_data['growth_rate'] = tourism_data['Количество туристов, тыс. чел.'].pct_change() * 100
        data_files_status["Туризм"] = True
        print("Данные о туризме успешно загружены.")
    
    if os.path.exists('Экология/Уровень воды.xlsx'):
        water_level_data = pd.read_excel('Экология/Уровень воды.xlsx')
        data_files_status["Уровень воды"] = True
        print("Данные об уровне воды успешно загружены.")
    
    if os.path.exists('Леса и животные/Вылов рыбы.xlsx'):
        fish_catch_data = pd.read_excel('Леса и животные/Вылов рыбы.xlsx')
        data_files_status["Вылов рыбы"] = True
        print("Данные о вылове рыбы успешно загружены.")
    
    if os.path.exists('Экология/Атмосфера') and os.path.exists('Экология/Атмосфера/PM2,5.csv'):
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
            
            if not air_pm25.empty:
                air_pm25['month'] = air_pm25['date'].dt.month
                air_pm25['year'] = air_pm25['date'].dt.year
                air_quality_data = air_pm25.groupby(['year', 'month'])['Значение'].mean().reset_index()
                air_quality_data['date'] = pd.to_datetime(air_quality_data[['year', 'month']].assign(day=1))
                data_files_status["Качество воздуха"] = True
                print("Данные о качестве воздуха успешно загружены.")
        except Exception as e:
            print(f"Ошибка при загрузке данных качества воздуха: {e}")
    
    # Данные успешно загружены (хотя бы частично)
    print("Статус загрузки данных:")
    for key, value in data_files_status.items():
        print(f"  {key}: {'Успешно' if value else 'Ошибка'}")
    
except Exception as e:
    print(f"Общая ошибка загрузки данных: {e}")

# Создание приложения
app = dash.Dash(__name__, 
                external_stylesheets=[dbc.themes.JOURNAL],
                meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0'}]
)
server = app.server

# Load figure template for consistent styling
load_figure_template("journal")

# Определение цветовой палитры
colors = {
    'primary': '#007bff',
    'secondary': '#6c757d',
    'success': '#28a745',
    'danger': '#dc3545',
    'warning': '#ffc107',
    'info': '#17a2b8',
    'light': '#f8f9fa',
    'dark': '#343a40',
    'background': '#f8f9fa',
    'text': '#343a40',
    'water': '#0db7ed',
    'tourism': '#8884d8',
    'chart1': '#5D69B1',
    'chart2': '#52BCA3',
    'chart3': '#E58606',
    'chart4': '#99C945'
}

# Функция для создания заглушки графика при отсутствии данных
def create_placeholder_figure(message="Данные недоступны"):
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        showarrow=False,
        font=dict(size=20, color=colors['secondary'])
    )
    fig.update_layout(
        height=400,
        paper_bgcolor=colors['light'],
        plot_bgcolor=colors['light'],
        font=dict(color=colors['text'])
    )
    return fig

# Функция для создания простой карты Байкальского региона
def create_simple_map():
    # Координаты основных городов
    cities = {
        'Иркутск': {'lat': 52.3, 'lon': 104.3},
        'Улан-Удэ': {'lat': 51.8, 'lon': 107.6},
        'Северобайкальск': {'lat': 55.6, 'lon': 109.3},
        'Листвянка': {'lat': 51.9, 'lon': 104.8}
    }
    
    # Создаем карту
    fig = go.Figure()
    
    # Добавляем города как маркеры
    fig.add_trace(go.Scattermapbox(
        lat=[city['lat'] for city in cities.values()],
        lon=[city['lon'] for city in cities.values()],
        mode='markers+text',
        marker=dict(size=12, color=colors['danger'], symbol='circle'),
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
        line=dict(width=3, color=colors['primary']),
        fill='toself',
        fillcolor='rgba(0, 123, 255, 0.3)',
        name='Озеро Байкал'
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
        paper_bgcolor=colors['light'],
        font=dict(color=colors['dark']),
        legend=dict(
            bgcolor=colors['light'],
            bordercolor=colors['primary'],
            borderwidth=2,
            font=dict(size=12, color=colors['dark'])
        )
    )
    
    return fig

# Определение макета приложения
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H1("Байкальская природная территория", 
                        className="text-center my-4", 
                        style={'color': colors['primary'], 'font-weight': 'bold'}),
                html.H5("Мониторинг экологических и социально-экономических показателей", 
                        className="text-center mb-4", 
                        style={'color': colors['secondary']})
            ], style={
                'background-color': colors['light'],
                'padding': '20px',
                'border-radius': '10px',
                'box-shadow': '0 4px 8px rgba(0, 0, 0, 0.1)',
                'margin-bottom': '20px'
            })
        ], width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H4("Навигация", className="m-0", style={'font-weight': 'bold'}),
                ], style={'background-color': colors['primary'], 'color': 'white'}),
                dbc.CardBody([
                    dcc.Tabs(id='tabs', value='tab-map', children=[
                        dcc.Tab(
                            label='Карта региона', 
                            value='tab-map',
                            style={'padding': '12px', 'font-weight': 'bold'},
                            selected_style={'padding': '12px', 'font-weight': 'bold', 'background-color': colors['primary'], 'color': 'white'}
                        ),
                        dcc.Tab(
                            label='Экология водных ресурсов', 
                            value='tab-ecology',
                            style={'padding': '12px', 'font-weight': 'bold'},
                            selected_style={'padding': '12px', 'font-weight': 'bold', 'background-color': colors['primary'], 'color': 'white'}
                        ),
                        dcc.Tab(
                            label='Туризм', 
                            value='tab-tourism',
                            style={'padding': '12px', 'font-weight': 'bold'},
                            selected_style={'padding': '12px', 'font-weight': 'bold', 'background-color': colors['primary'], 'color': 'white'}
                        )
                    ], colors={
                        "border": colors['light'],
                        "primary": colors['primary'],
                        "background": colors['background']
                    })
                ], style={'padding': '0'})
            ], className="mb-4", style={'box-shadow': '0 4px 8px rgba(0, 0, 0, 0.1)'})
        ], width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            html.Div(id='tab-content', style={'min-height': '600px'})
        ], width=12)
    ]),
    
    html.Footer([
        html.Hr(style={'margin-top': '30px', 'margin-bottom': '20px'}),
        html.Div([
            html.P("© 2023 Дашборд Байкальской природной территории", 
                  className="text-center mb-0", 
                  style={'color': colors['secondary'], 'font-weight': 'bold'}),
            html.P("Данные о регионе, экологии и туризме", 
                  className="text-center", 
                  style={'color': colors['secondary'], 'font-size': '0.9rem'})
        ], style={'padding': '10px'})
    ], className="mt-4")
    
], fluid=True, style={'background-color': colors['background'], 'min-height': '100vh', 'padding': '20px'})

# Callback для обновления содержимого вкладки
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

# Отображение вкладки с картой
def render_map_tab():
    return dbc.Card([
        dbc.CardHeader([
            html.H3("Байкальская природная территория", className="card-title m-0"),
        ], style={'background-color': colors['primary'], 'color': 'white'}),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.P("Интерактивная карта региона с основными географическими объектами", 
                          className="lead text-muted mb-4"),
                    dcc.Graph(figure=create_simple_map(), 
                             style={'height': '800px', 'box-shadow': '0 4px 8px rgba(0, 0, 0, 0.1)', 'border-radius': '8px'})
                ], width=12)
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Информация о регионе", className="card-title"),
                            html.P([
                                """Байкальская природная территория включает озеро Байкал, водоохранную зону, особо охраняемые природные территории, 
                                прилегающие к озеру Байкал, а также прилегающую к озеру Байкал территорию шириной до 200 километров на запад и северо-запад от него.
                                """
                            ], className="card-text"),
                            html.P([
                                """Озеро Байкал — крупнейший природный резервуар пресной воды (23 тыс. куб. км), что составляет около 19% мировых запасов.
                                Глубина озера достигает 1642 м. Возраст озера составляет около 25-30 млн лет.
                                """
                            ], className="card-text mt-2"),
                            dbc.Row([
                                dbc.Col([
                                    dbc.ListGroup([
                                        dbc.ListGroupItem("Площадь: 31 722 км²", color="light"),
                                        dbc.ListGroupItem("Длина: 636 км", color="light"),
                                        dbc.ListGroupItem("Ширина: до 79 км", color="light"),
                                    ], className="mt-3 mb-2")
                                ], md=6),
                                dbc.Col([
                                    dbc.ListGroup([
                                        dbc.ListGroupItem("Глубина: до 1642 м", color="light"),
                                        dbc.ListGroupItem("Объем: 23 615 км³", color="light"),
                                        dbc.ListGroupItem("Водосборная площадь: 557 тыс. км²", color="light"),
                                    ], className="mt-3 mb-2")
                                ], md=6),
                            ])
                        ])
                    ], className="mt-4", style={'box-shadow': '0 4px 8px rgba(0, 0, 0, 0.1)'})
                ], width=12)
            ])
        ])
    ], style={'box-shadow': '0 4px 8px rgba(0, 0, 0, 0.1)'})

# Отображение вкладки с экологической информацией
def render_ecology_tab():
    panels = []
    
    panels.append(
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("Экологические показатели", className="card-title m-0"), 
                                  style={'background-color': colors['primary'], 'color': 'white'}),
                    dbc.CardBody([
                        html.P("Ключевые индикаторы состояния водных ресурсов Байкальской природной территории", 
                              className="lead text-muted mb-4"),
                    ])
                ], style={'box-shadow': '0 4px 8px rgba(0, 0, 0, 0.1)'})
            ], width=12)
        ])
    )
    
    # График уровня воды
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
            water_fig.update_layout(
                height=500, 
                hovermode="x unified",
                title_font=dict(size=18, color=colors['dark']),
                font=dict(color=colors['dark']),
                plot_bgcolor=colors['light'],
                paper_bgcolor=colors['light'],
                xaxis=dict(
                    title_font=dict(size=14),
                    tickfont=dict(size=12),
                    gridcolor='rgba(0,0,0,0.05)'
                ),
                yaxis=dict(
                    title_font=dict(size=14),
                    tickfont=dict(size=12),
                    gridcolor='rgba(0,0,0,0.05)'
                ),
                margin=dict(l=40, r=40, t=50, b=40)
            )
        except Exception as e:
            print(f"Ошибка при создании графика уровня воды: {e}")
            water_fig = create_placeholder_figure("Ошибка при отображении данных об уровне воды")
    else:
        water_fig = create_placeholder_figure("Данные об уровне воды недоступны")
    
    # График вылова рыбы
    if data_files_status["Вылов рыбы"]:
        try:
            fish_fig = px.bar(
                fish_catch_data,
                x='Год',
                y='Вылов, тонн',
                color='Вид',
                title='Вылов рыбы по видам в Байкальском бассейне',
                labels={'Вылов, тонн': 'Вылов (тонн)', 'Год': 'Год', 'Вид': 'Вид рыбы'},
                color_discrete_map={
                    'Омуль': colors['chart1'],
                    'Сиг': colors['chart2'],
                    'Хариус': colors['chart3'],
                    'Осетр': colors['chart4'],
                    'Другие': colors['secondary']
                }
            )
            fish_fig.update_layout(
                height=500, 
                hovermode="x unified",
                title_font=dict(size=18, color=colors['dark']),
                font=dict(color=colors['dark']),
                plot_bgcolor=colors['light'],
                paper_bgcolor=colors['light'],
                xaxis=dict(
                    title_font=dict(size=14),
                    tickfont=dict(size=12),
                    gridcolor='rgba(0,0,0,0.05)'
                ),
                yaxis=dict(
                    title_font=dict(size=14),
                    tickfont=dict(size=12),
                    gridcolor='rgba(0,0,0,0.05)'
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                    font=dict(size=12)
                ),
                margin=dict(l=40, r=40, t=80, b=40)
            )
        except Exception as e:
            print(f"Ошибка при создании графика вылова рыбы: {e}")
            fish_fig = create_placeholder_figure("Ошибка при отображении данных о вылове рыбы")
    else:
        fish_fig = create_placeholder_figure("Данные о вылове рыбы недоступны")
    
    panels.append(
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(figure=water_fig)
                    ])
                ], style={'box-shadow': '0 4px 8px rgba(0, 0, 0, 0.1)'})
            ], width=12, lg=6, className="mb-4"),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(figure=fish_fig)
                    ])
                ], style={'box-shadow': '0 4px 8px rgba(0, 0, 0, 0.1)'})
            ], width=12, lg=6, className="mb-4")
        ])
    )
    
    # График качества воздуха
    if data_files_status["Качество воздуха"]:
        try:
            air_fig = px.line(
                air_quality_data,
                x='date',
                y='Значение',
                title='Среднемесячная концентрация PM2.5 в атмосфере',
                labels={'Значение': 'Концентрация PM2.5 (мкг/м³)', 'date': 'Дата'},
                color_discrete_sequence=[colors['danger']]
            )
            air_fig.update_layout(
                height=400, 
                hovermode="x unified",
                title_font=dict(size=18, color=colors['dark']),
                font=dict(color=colors['dark']),
                plot_bgcolor=colors['light'],
                paper_bgcolor=colors['light'],
                xaxis=dict(
                    title_font=dict(size=14),
                    tickfont=dict(size=12),
                    gridcolor='rgba(0,0,0,0.05)'
                ),
                yaxis=dict(
                    title_font=dict(size=14),
                    tickfont=dict(size=12),
                    gridcolor='rgba(0,0,0,0.05)'
                ),
                margin=dict(l=40, r=40, t=50, b=40)
            )
            
            panels.append(
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                dcc.Graph(figure=air_fig)
                            ])
                        ], style={'box-shadow': '0 4px 8px rgba(0, 0, 0, 0.1)'})
                    ], width=12)
                ])
            )
        except Exception as e:
            print(f"Ошибка при создании графика качества воздуха: {e}")
    
    # Добавляем информацию о важности мониторинга экологии
    panels.append(
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Экологический мониторинг Байкала", className="m-0"), 
                                  style={'background-color': colors['primary'], 'color': 'white'}),
                    dbc.CardBody([
                        html.P([
                            """Экологический мониторинг озера Байкал и прилегающих территорий имеет важное значение для сохранения 
                            его уникальной экосистемы. Регулярный контроль уровня воды, состояния воздуха и биоресурсов позволяет 
                            своевременно выявлять негативные изменения и принимать меры по их устранению.
                            """
                        ], className="card-text"),
                        html.P([
                            """Основные экологические показатели включают уровень воды в озере, динамику вылова рыбы, 
                            концентрацию загрязняющих веществ в воздухе и воде. Данные показатели служат индикаторами 
                            состояния экосистемы и отражают эффективность природоохранных мероприятий.
                            """
                        ], className="card-text mt-3")
                    ])
                ], className="mt-4 mb-2", style={'box-shadow': '0 4px 8px rgba(0, 0, 0, 0.1)'})
            ], width=12)
        ])
    )
    
    return dbc.Card([
        dbc.CardBody(panels)
    ], style={'box-shadow': '0 4px 8px rgba(0, 0, 0, 0.1)'})

# Отображение вкладки с информацией о туризме
def render_tourism_tab():
    panels = []
    
    panels.append(
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("Туристическая активность", className="card-title m-0"), 
                                  style={'background-color': colors['primary'], 'color': 'white'}),
                    dbc.CardBody([
                        html.P("Анализ туристического потока в Байкальском регионе и его динамика", 
                              className="lead text-muted mb-4"),
                    ])
                ], style={'box-shadow': '0 4px 8px rgba(0, 0, 0, 0.1)'})
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
            # График туристического потока
            tourism_fig = px.bar(
                tourism_data,
                x='Год',
                y='Количество туристов, тыс. чел.',
                title='Динамика туристического потока в регионе Байкала',
                labels={'Количество туристов, тыс. чел.': 'Количество туристов (тыс. чел.)', 'Год': 'Год'},
                color_discrete_sequence=[colors['tourism']]
            )
            tourism_fig.update_layout(
                height=500, 
                hovermode="x unified",
                title_font=dict(size=18, color=colors['dark']),
                font=dict(color=colors['dark']),
                plot_bgcolor=colors['light'],
                paper_bgcolor=colors['light'],
                xaxis=dict(
                    title_font=dict(size=14),
                    tickfont=dict(size=12),
                    gridcolor='rgba(0,0,0,0.05)'
                ),
                yaxis=dict(
                    title_font=dict(size=14),
                    tickfont=dict(size=12),
                    gridcolor='rgba(0,0,0,0.05)'
                ),
                margin=dict(l=40, r=40, t=50, b=40)
            )
            
            # График темпов роста
            growth_fig = px.line(
                tourism_data.dropna(),
                x='Год',
                y='growth_rate',
                title='Темпы роста туристического потока (%)',
                labels={'growth_rate': 'Рост (% к предыдущему году)', 'Год': 'Год'},
                markers=True,
                color_discrete_sequence=[colors['chart3']]
            )
            growth_fig.update_layout(
                height=500, 
                hovermode="x unified",
                title_font=dict(size=18, color=colors['dark']),
                font=dict(color=colors['dark']),
                plot_bgcolor=colors['light'],
                paper_bgcolor=colors['light'],
                xaxis=dict(
                    title_font=dict(size=14),
                    tickfont=dict(size=12),
                    gridcolor='rgba(0,0,0,0.05)'
                ),
                yaxis=dict(
                    title_font=dict(size=14),
                    tickfont=dict(size=12),
                    gridcolor='rgba(0,0,0,0.05)'
                ),
                margin=dict(l=40, r=40, t=50, b=40)
            )
            
            panels.append(
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                dcc.Graph(figure=tourism_fig)
                            ])
                        ], style={'box-shadow': '0 4px 8px rgba(0, 0, 0, 0.1)'})
                    ], width=12, lg=6, className="mb-4"),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                dcc.Graph(figure=growth_fig)
                            ])
                        ], style={'box-shadow': '0 4px 8px rgba(0, 0, 0, 0.1)'})
                    ], width=12, lg=6, className="mb-4")
                ])
            )
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
        
        # Добавляем информацию о туризме
        panels.append(
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Развитие туризма в регионе", className="m-0"), 
                                      style={'background-color': colors['primary'], 'color': 'white'}),
                        dbc.CardBody([
                            html.P([
                                """Байкал является одним из наиболее популярных туристических направлений в России.
                                Регион предлагает различные виды туризма: экологический, спортивный, культурно-познавательный, 
                                лечебно-оздоровительный и другие. Основные туристические центры сосредоточены в Иркутской области и Республике Бурятия."""
                            ], className="card-text"),
                            
                            dbc.Row([
                                dbc.Col([
                                    dbc.Card([
                                        dbc.CardHeader(html.H6("Виды туризма", className="m-0"), 
                                                     style={'background-color': colors['secondary'], 'color': 'white'}),
                                        dbc.ListGroup([
                                            dbc.ListGroupItem("Экологический туризм", color="light"),
                                            dbc.ListGroupItem("Культурно-познавательный туризм", color="light"),
                                            dbc.ListGroupItem("Активный отдых и спортивный туризм", color="light"),
                                            dbc.ListGroupItem("Лечебно-оздоровительный туризм", color="light"),
                                        ], flush=True)
                                    ], className="mt-3")
                                ], md=6),
                                dbc.Col([
                                    dbc.Card([
                                        dbc.CardHeader(html.H6("Основные туристические центры", className="m-0"), 
                                                     style={'background-color': colors['secondary'], 'color': 'white'}),
                                        dbc.ListGroup([
                                            dbc.ListGroupItem("Иркутск и окрестности", color="light"),
                                            dbc.ListGroupItem("Листвянка", color="light"),
                                            dbc.ListGroupItem("Остров Ольхон", color="light"),
                                            dbc.ListGroupItem("Байкальск и Северобайкальск", color="light"),
                                        ], flush=True)
                                    ], className="mt-3")
                                ], md=6),
                            ], className="mt-3")
                        ])
                    ], className="mt-3 mb-3", style={'box-shadow': '0 4px 8px rgba(0, 0, 0, 0.1)'})
                ], width=12)
            ])
        )
    
    return dbc.Card([
        dbc.CardBody(panels)
    ], style={'box-shadow': '0 4px 8px rgba(0, 0, 0, 0.1)'})

if __name__ == '__main__':
    print("Запуск дашборда Байкальской природной территории...")
    app.run_server(debug=True, port=8051) 