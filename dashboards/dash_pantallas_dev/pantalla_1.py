"""
Creado el 11/12/2023 a las 12:27 p. m.

@author: jacevedo
"""

from datetime import date
import numpy as np
import dash
import plotly.graph_objs as go
from babel.dates import format_date
from dash import dcc, html
from dash.dependencies import Input, Output, State
from pandas.tseries.offsets import MonthBegin
from waitress import serve
import plotly.express as px

from general_tools import get_ip_address
from kpi_module import get_kpi_data
from prousuario_tools import get_dash_port, get_sb_colors

# Initialize the Dash app
app = dash.Dash(__name__)

# start_date = (date.today()-MonthBegin(1)).date()
start_date = (date.today() - MonthBegin(2)).date()
colores = get_sb_colors()

escala_len = len(px.colors.diverging.RdYlGn_r[1:])
escala_colores_dias = []
for idx, color in zip(np.arange(30,71,40/escala_len), px.colors.diverging.RdYlGn_r[1:]):
    escala_colores_dias.append({'range': [np.ceil(idx), np.ceil(idx + 40 / escala_len)], 'color': color})
    if idx == 30.0:
        escala_colores_dias.append({'range': [np.ceil(0), np.ceil(idx + 40 / escala_len)], 'color': color})

escala_colores_porciento = [{'range':[idx,idx+.5/escala_len], 'color':color} for idx, color in zip(np.arange(0.5,1.01,0.5/escala_len), px.colors.diverging.RdYlGn[:-1])]

gauge_color = colores['blue sb darker']

# Dummy function to fetch or update data
def fetch_kpi_data():
    reclamos = get_kpi_data(type='reclamos', start_date=start_date)
    info = get_kpi_data(type='info', start_date=start_date)
    contratos = get_kpi_data(type='contratos', start_date=start_date)
    kpi_reclamos_pre = reclamos.iloc[0].to_dict()
    kpi_reclamos = reclamos.iloc[1].to_dict()
    kpi_info_pre = info.iloc[0].to_dict()
    kpi_info = info.iloc[1].to_dict()
    kpi_contratos_pre = contratos.iloc[0].to_dict()
    kpi_contratos = contratos.iloc[1].to_dict()
    # kpi_contratos_pre = contratos.iloc[0].to_dict()
    # kpi_contratos = contratos.iloc[1].to_dict()
    # return {"reclamos": kpi_reclamos, "info": kpi_info, "reclamos_pre": kpi_reclamos_pre, "info_pre": kpi_info_pre, "contratos": kpi_contratos, "contratos_pre": kpi_contratos_pre}
    return {"reclamos": kpi_reclamos, "reclamos_pre": kpi_reclamos_pre,
            "info": kpi_info, "info_pre": kpi_info_pre,
            'contratos': kpi_contratos, "contratos_pre": kpi_contratos_pre
            }


# Function to create a gauge chart
def create_gauge_chart(kpi_name, value, prev, tipo_grafico='days', width=900, height=500):
    fig = go.Figure()
    if tipo_grafico == 'days':
        trace = go.Indicator(
            mode="gauge+number+delta",
            value=value,
            title={'text': kpi_name, 'font': {'family': 'SairaMedium', 'size': 30}},
            number={"valueformat": ".0f", 'font_family': 'SairaBold', 'suffix': ' días'},
            gauge={
                'axis': {'range': [None, 70], 'tickformat': '.0f'},
                'bar': {'color': gauge_color, 'thickness':0.4},
                # 'bar': {'color': 'white', 'thickness':0.3
                    # , 'line_color': 'white', 'line_width':3
                    #     },
                # 'steps': [
                #     {'range': [0, 50], 'color': "#c2f0c2"},
                #     {'range': [50, 60], 'color': "#ffe0b3"},
                #     {'range': [60, 70], 'color': "#ffb3b3"}
                # ],
                'steps':escala_colores_dias
                # 'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 60}
            },
            delta={'reference': prev, 'relative': True, 'valueformat': '.1%', 'increasing.color': 'red',
                   'decreasing.color': 'green'},
        )

    elif tipo_grafico == 'cases':
        trace = go.Indicator(
            mode="gauge+number+delta",
            value=round(value, 3),
            title={'text': kpi_name, 'font': {'family': 'SairaMedium', 'size': 30}},
            number={"valueformat": ".0%", 'font_family': 'SairaBold'},
            gauge={
                'axis': {'range': [0.5, 1], 'tickformat': '.0%'},
                'bar': {'color': gauge_color, 'thickness':0.4},
                # 'shape':'bullet',
                # 'steps': [
                #     {'range': [0, 0.7], 'color': "#ffb3b3"},
                #     {'range': [0.7, 0.9], 'color': "#ffe0b3"},
                #     {'range': [0.9, 1], 'color': "#c2f0c2"}
                # ],
                'steps':escala_colores_porciento
                # 'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 0.8}
            },
            delta={'reference': round(prev, 3), 'relative': False, 'valueformat': '.1%', 'increasing.color': 'green',
                   'decreasing.color': 'red', 'suffix': 'pp'},
        )
    else:
        trace = go.Indicator(title='Error en tipo de indicador')
    fig.add_trace(trace)

    fig.update_layout(width=width, height=height, font_size=30)
    fig.add_annotation(
        text='Diferencia frente<br>al mes anterior', x=0.5, align='center', y=-0.1, showarrow=False,
        font_family='SairaMedium', font_size=20
    )
    return fig


TABS_STYLES = {
    'height': '44px',
}

TAB_STYLE = {
    # 'borderBottom': '1px solid #d6d6d6',
    # 'padding': '6px',
    # 'backgroundColor': '#5C7F91',
    # 'color': '#F0F3F5',
    # 'borderColor': '#0D3048',
    'font-size': '40px',
    'font-family': 'SairaLight'
}


TAB_SELECTED_STYLE = {
    # 'borderTop': '1px solid #d6d6d6',
    # 'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': get_sb_colors()['turquesa pro'],
    # 'color': '#0D3048',
    # 'padding': '6px',
    'font-size': '45px',
    'font-family': 'SairaBold'
}

# Define the layout of the app
app.layout = html.Div([
    html.Header([
        html.Img(src='./assets/prousuario-logo.svg', style={'height': '50px', 'margin-right': '10px'}),
        # Adjust logo size as needed
        html.H1("VERA | Métricas ProUsuario",
                # style={'display': 'inline-block', 'vertical-align': 'middle', 'margin-left': '10px'}
                )
    ], style={'display': 'flex', 'align-items': 'flex-end', 'margin-bottom': '0px'}),
    dcc.Tabs(id="tabs", value='tab-1', children=[
        # dcc.Tab(label='Indicadores de Gestión', className='metric-title', value='tab-1'),
        # dcc.Tab(label='Cases and Projections', className='metric-title', value='tab-2'),
        # dcc.Tab(label='Future Development', className='metric-title', value='tab-3'),
        dcc.Tab(label='Reclamaciones', className='metric-title', value='tab-1', style=TAB_STYLE,
                selected_style=TAB_SELECTED_STYLE),
        dcc.Tab(label='Información Financiera', className='metric-title', value='tab-2', style=TAB_STYLE,
                selected_style=TAB_SELECTED_STYLE),
        dcc.Tab(label='Contratos', className='metric-title', value='tab-3', style=TAB_STYLE,
                selected_style=TAB_SELECTED_STYLE),
        # dcc.Tab(label='Future Development', className='metric-title', value='tab-3'),
    ]),
    html.H1(style={'textAlign': 'center'},
            id='titulo-mes'),
    html.Div(id='tabs-content'

             ),
    html.Div(id='casos-mes'

             ),

    # Hidden div to store the data
    dcc.Store(id='kpi-data-store'),

    # Interval component for data refresh
    dcc.Interval(
        id='data-refresh-interval',
        interval=60 * 60 * 1000,  # in milliseconds (1 hour)
        n_intervals=0
    ),

    # Interval component for tab rotation
    dcc.Interval(
        id='interval-component',
        interval=60 * 1000,  # in milliseconds (5 minutes)
        n_intervals=0
    )
])


@app.callback(
    Output('casos-mes', 'children'),
[Input('tabs', 'value'),
 Input('kpi-data-store', 'data')])
def show_casos_mes(tab, kpi_data):
    if tab == 'tab-1':
        total_casos = kpi_data['reclamos']['total_casos']
        texto = f'{total_casos} casos cerrados en el mes'
    elif tab == 'tab-2':
        total_casos = kpi_data['info']['total_casos']
        texto = f'{total_casos} casos cerrados en el mes'
    elif tab == 'tab-3':
        total_ra = kpi_data['contratos']['total_ra']
        total_sib = kpi_data['contratos']['total_sib']
        texto = f'{total_ra} casos RA y {total_sib} SIB cerrados en el mes'
    return html.Div([
        html.H1(texto, style={'font-size': 60})
    ], style={'display': 'flex', 'width': '100%', 'justify-content': 'center'})


# Callback for tab content
@app.callback(Output('tabs-content', 'children'),
              [Input('tabs', 'value'),
               Input('kpi-data-store', 'data')])
def render_content(tab, kpi_data):
    if tab == 'tab-1':
        # Content for first tab
        title_dias = "Tiempo promedio de respuesta"
        title_casos = "Casos a tiempo"
        kpi_dias = kpi_data['reclamos']['kpi_dias']
        kpi_dias_prev = kpi_data['reclamos_pre']['kpi_dias']
        kpi_casos = kpi_data['reclamos']['kpi_casos']
        kpi_casos_prev = kpi_data['reclamos_pre']['kpi_casos']
        return html.Div([
            # html.H2('Indicadores de Gestión', style={'text-align':'center'}),
            # html.Div([
            #     html.Div([
            #         html.H2('Reclamaciones', style={'text-align':'center', 'font-size':40}),

            dcc.Graph(figure=create_gauge_chart(title_dias, kpi_dias, kpi_dias_prev, tipo_grafico='days')),
            dcc.Graph(figure=create_gauge_chart(title_casos, kpi_casos, kpi_casos_prev, tipo_grafico='cases'))
            # ]),
            # ], style={'width': '50%', 'display': 'flex', 'flex-direction': 'column'}),

            # dcc.Graph(figure=create_gauge_chart("Tiempo promedio de respuesta - Contratos")),
            # dcc.Graph(figure=create_gauge_chart("Casos a tiempo - Contratos")),
            # ], style={'display': 'flex', 'flex-wrap': 'wrap', 'justify-content': 'center', 'align-items': 'center'})
        ], style={'display': 'flex', 'width': '100%', 'justify-content': 'center'})
        # ])
        # ])
    elif tab == 'tab-2':
        # Content for second tab
        title_dias = "Tiempo promedio de respuesta"
        title_casos = "Casos a tiempo"
        kpi_dias = kpi_data['info']['kpi_dias']
        kpi_dias_prev = kpi_data['info_pre']['kpi_dias']
        kpi_casos = kpi_data['info']['kpi_casos']
        kpi_casos_prev = kpi_data['info_pre']['kpi_casos']
        return html.Div([
            # Bar/line charts for cases and projections
            # html.Div([])
            #     html.H2('Información Financiera', style={'text-align': 'center', 'font-size': 40}),
            dcc.Graph(figure=create_gauge_chart(title_dias, kpi_dias, kpi_dias_prev, tipo_grafico='days')),
            dcc.Graph(figure=create_gauge_chart(title_casos, kpi_casos, kpi_casos_prev, tipo_grafico='cases'))
            # ], style={'width': '50%', 'display': 'flex', 'flex-direction': 'column', 'margin': 'auto'}),
        ], style={'display': 'flex', 'width': '100%', 'margin': 'auto', 'justify-content': 'center'})
    elif tab == 'tab-3':
        # Content for third tab
        # Content for second tab
        title_dias_ra = "Tiempo promedio de respuesta RA"
        title_dias_sib = "Tiempo promedio de respuesta SIB"
        title_casos = "Casos a tiempo"
        kpi_dias_ra = kpi_data['contratos']['RA']
        kpi_dias_sib = kpi_data['contratos']['SIB']
        kpi_dias_prev_ra = kpi_data['contratos_pre']['RA']
        kpi_dias_prev_sib = kpi_data['contratos_pre']['SIB']
        kpi_casos = kpi_data['contratos']['A tiempo']
        kpi_casos_prev = kpi_data['contratos_pre']['A tiempo']
        return html.Div([
            # Bar/line charts for cases and projections
            # html.Div([])
            #     html.H2('Información Financiera', style={'text-align': 'center', 'font-size': 40}),
            # html.Div([
            # dcc.Graph(figure=create_gauge_chart(title_dias_ra, kpi_dias_ra, kpi_dias_prev_ra, tipo_grafico='days', height=400)),
            # dcc.Graph(figure=create_gauge_chart(title_dias_sib, kpi_dias_sib, kpi_dias_prev_sib, tipo_grafico='days', height=400)),
            # ]),
            # dcc.Graph(figure=create_gauge_chart(title_casos, kpi_casos, kpi_casos_prev, tipo_grafico='cases'))
            dcc.Graph(figure=create_gauge_chart(title_dias_ra, kpi_dias_ra, kpi_dias_prev_ra, tipo_grafico='days', width=650)),
            dcc.Graph(figure=create_gauge_chart(title_dias_sib, kpi_dias_sib, kpi_dias_prev_sib, tipo_grafico='days', width=650)),
            dcc.Graph(figure=create_gauge_chart(title_casos, kpi_casos, kpi_casos_prev, tipo_grafico='cases', width=650))
            # ], style={'width': '50%', 'display': 'flex', 'flex-direction': 'column', 'margin': 'auto'}),
        ], style={'display': 'flex', 'width': '100%', 'margin': '0', 'justify-content': 'center'})


# Callback for automatic tab rotation
@app.callback(Output('tabs', 'value'),
              [Input('interval-component', 'n_intervals')],
              [State('tabs', 'value')])
def rotate_tabs(n_intervals, current_tab):
    tab_sequence = ['tab-1', 'tab-2', 'tab-3']
    current_index = tab_sequence.index(current_tab)
    next_index = (current_index + 1) % len(tab_sequence)
    return tab_sequence[next_index]


# Callback for data refresh
@app.callback(Output('kpi-data-store', 'data'),
              [Input('data-refresh-interval', 'n_intervals')])
def refresh_data(n_intervals):
    return fetch_kpi_data()


@app.callback(Output('titulo-mes', 'children'),
              [Input('data-refresh-interval', 'n_intervals')])
def update_title_mes(n_intervals):
    fecha = date.today()
    if fecha.day < 3:
        fecha = (fecha - MonthBegin(1)).date()
    return format_date(fecha, format="MMMM YYYY", locale='es_DO').upper()


# %%
# Run the app
host = get_ip_address()
port = get_dash_port('pantalla_1')
if __name__ == '__main__':
    print('Corriendo Dash Pantalla 1')
    print(f'http://{host}:{port}')
    # app.run_server(debug=True, host=host, port=port)
    serve(app.server, host=host, port=port)
