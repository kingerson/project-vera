"""
Creado el 19/7/2022 a las 4:25 p. m.

@author: jacevedo
"""

import socket
from datetime import date, timedelta

import dash
import pandas as pd
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
from flask import Flask

import plotly.express as px
from flask import Flask
import infofinanciera_reading
from kpi_module import get_kpi_graphs

from prousuario_tools import get_sb_colors

from waitress import serve
import plotly.express as px

from general_tools import get_ip_address
from kpi_module import get_kpi_data
from prousuario_tools import get_dash_port, get_sb_colors

# Get colors
colors = get_sb_colors()

# Crea el app principal
EXTERNAL_STYLESHEETS = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
server = Flask(__name__)
app = dash.Dash(__name__,
                external_stylesheets=EXTERNAL_STYLESHEETS,
                include_assets_files=True,
                meta_tags=[{'name': 'viewport', 'content': 'width=device-width'}],
                server=server,
                url_base_pathname='/infofinanciera/'
                )
app.title = 'Información Financiera'
server = app.server


TABS_STYLES = {
    'height': '44px',
}

TAB_STYLE = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'backgroundColor': '#5C7F91',
    'color': '#F0F3F5',
    'borderColor': '#0D3048',
    'font-size': '20px'
}

TAB_SELECTED_STYLE = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#0CCCC6',
    'color': '#0D3048',
    'padding': '6px',
    'font-size': '20px'
}

micro_style = {'width': '50%', 'display': 'inline-block'}

# %%
df = infofinanciera_reading.main('2022-06-01')
data = df.groupby('etapa_actual').count()['codigo']

fig = px.bar(data)

def layout_maker():
    app = html.Div(className='row', children=[
        html.Meta(httpEquiv="refresh", content="3600"),
        dcc.Interval(
            id='interval-component',
            interval=3600 * 1000,  # in milliseconds
            n_intervals=0
        ),
        dcc.Store(id='reclamos-data'),
        dcc.Store(id='info-data'),
        dcc.Store(id='sla-data'),
        html.Div([
            html.Div([
                html.Div([
                    html.Img(
                        src='assets/logo_sb.png',
                        height=110, width=140
                        ),
                    ],  style=dict(display='inline-block', height='80px', float="left")),
                html.Div([
                    html.H1(
                        'VERA',
                        id='titulo-cabecera',
                        style={'display': 'inline-block', 'font-weight': 'bold', 'height': '80px', 'text-align': 'top'}
                    ),
                    html.H2(
                        'Métricas Información Financiera',
                        id='sub-titulo',
                        style={'padding-left': '10px', 'display': 'inline-block', 'height': '80px', 'text-align': 'top'}
                    )
                    ], style={'display': 'inline-block', 'height': '60px', 'padding': "20px", "float": "left"})
            ], style=dict(width='45%', display='inline-block')),
            # html.Div([
            #     html.Div([
            #         html.H6(
            #             'Periodo a visualizar   ',
            #             id='date-picker-label'
            #         )
            #     ]),
            #     html.Div([
            #         dcc.DatePickerRange(
            #             id='date-picker-range',
            #             is_RTL=False,
            #             end_date=date.today().isoformat(),
            #             start_date=(date.today() - timedelta(weeks=2)).isoformat(),
            #         )
            #     ]),
            # ],  style={'display': 'inline-block', 'padding-bottom': '20px', 'padding-top': '0px'}),
            # html.Div([
            #     html.Div([
            #         dcc.RadioItems(
            #             id='freq-picker',
            #             options=[
            #                 {'label': 'En días', 'value': 'D'},
            #                 {'label': 'En semanas', 'value': 'W-MON'},
            #                 {'label': 'En meses', 'value': 'M'},
            #                # {'label': 'En años', 'value': 'Y'},
            #             ], value='D'),
            #     ])
            # ], style={
            #     'display': 'inline-block', 'padding-top': '0px',
            #     'padding-bottom': '20px', 'padding-left': '30px'}),
            html.Div([
                dcc.Tabs(id="tabs", value='tab-general', children=[
                    dcc.Tab(
                        label='Generales',
                        value='tab-general',
                        style=TAB_STYLE,
                        selected_style=TAB_SELECTED_STYLE
                    ),
                    dcc.Tab(
                        label='Por Etapas',
                        value='tab-etapas',
                        style=TAB_STYLE,
                        selected_style=TAB_SELECTED_STYLE
                    ),
                    dcc.Tab(
                        label='Por Analistas',
                        value='tab-analistas',
                        style=TAB_STYLE,
                        selected_style=TAB_SELECTED_STYLE
                    )
                ], style=TABS_STYLES),
            ]),
        ]),
        html.Div(id='tabs-content', style={"margin": 20})
    ], style={
        'color': '#F0F3F5',
        "margin": 0,
        'font-family': 'Calibri'
        # 'display': 'flex'
        }
    )
    return app

app.layout = layout_maker()

# @app.callback(
#     [Output('date-picker-range', 'start_date'),
#      Output('date-picker-range', 'end_date')],
#     Input('interval-component', 'n_intervals')
# )
# def update_date():
#     end_date = date.today().isoformat()
#     start_date = (date.today() - timedelta(weeks=2)).isoformat()
#     return start_date, end_date

# @app.callback(
#     Output('reclamos-data', 'data'),
#     [Input('date-picker-range', 'start_date'),
#      Input('date-picker-range', 'end_date')]
# )
# def read(start_date, end_date):
#     result = data_readers.main('reclamos', start_date, end_date)
#     return result

@app.callback(
    Output('tabs-content', 'children'),
    [Input('tabs', 'value')
     # Input('reclamos-data', 'data'),
     # Input('info-data', 'data'),
     # Input('freq-picker', 'value')
     ]
    )
def render_content(tab):
    if tab == 'tab-general':
        fig_promedio, fig_casos = get_kpi_graphs(type='info')
        div = html.Div([
            html.Div([
                dcc.Graph(
                    id='kpi_promedios',
                    figure=fig_promedio
                ),
            ], style=dict(width='50%', display='inline-block')),
            html.Div([
                dcc.Graph(
                    id='kpi_casos',
                    figure=fig_casos
                ),
            ], style=dict(width='50%', display='inline-block'))
        ])
        return div



# if __name__ == '__main__':
#     app.run_server(debug=True, port=8383)

# host = socket.gethostbyname(socket.gethostname())
# if __name__ == '__main__':
#     app.run_server(debug=False, host=host, port=8787)
host = get_ip_address()
port = 8787
# /infofinanciera/
if __name__ == '__main__':
    print('Corriendo Dash Info Financiera')
    print(f'http://{host}:{port}/infofinanciera/')
    # app.run_server(debug=True, host=host, port=port)
    # app.run_server(debug=True)
    serve(app.server, host=host, port=port)