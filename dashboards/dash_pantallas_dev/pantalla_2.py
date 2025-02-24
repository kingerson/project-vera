"""Creado el 11/12/2023 a las 12:27 p. m.

@author: jacevedo
"""

from datetime import date
import math
import dash
from babel.dates import format_date
from dash import dcc, html
from dash.dependencies import Input, Output, State
from pandas.tseries.offsets import MonthBegin
from waitress import serve
import pandas as pd
from reporte_prousuario_app import reporte_app

import metricas_pantalla2
from general_tools import get_ip_address
from prousuario_tools import get_dash_port, get_sb_colors
import sql_tools

fecha = date.today()
if fecha.day < 3:
    fecha = (fecha - MonthBegin(1)).date()
print(fecha)


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
# Initialize the Dash app
app = dash.Dash(
    __name__,
    title='Metricas Pantalla 2',
    # url_base_pathname='/pantalla2/'
)

tabs = dcc.Tabs(id='tabs', value='tab-metricas', children=[
    dcc.Tab(label='Métricas Flujo', className='metric-title', value='tab-metricas', style=TAB_STYLE,
            selected_style=TAB_SELECTED_STYLE),
    dcc.Tab(label='App ProUsuario', className='metric-title', value='tab-app', style=TAB_STYLE,
            selected_style=TAB_SELECTED_STYLE),
])
# Define the layout of the app
app.layout = html.Div([
    # html.Meta(httpEquiv="refresh", content="3600"),
    # dcc.Store(id='reclamos-data', data=metricas_pantalla2.main()),
    html.Header([
        html.Img(src='./assets/prousuario-logo.svg', style={'height': '50px', 'margin-right': '10px'}),
        # Adjust logo size as needed
        html.H1("VERA | Métricas ProUsuario", style={'display': 'inline-block', 'vertical-align': 'middle', 'margin-left': '10px'})
    ],  style={'display': 'flex', 'align-items': 'flex-end', 'margin-bottom': '0px'}),
    tabs,
    # dcc.Tabs(id='tabs', value='tab-metricas', children=[
    #     dcc.Tab(label='Métricas Flujo', className='metric-title', value='tab-metricas', style=TAB_STYLE,
    #             selected_style=TAB_SELECTED_STYLE),
    #     dcc.Tab(label='App ProUsuario', className='metric-title', value='tab-app', style=TAB_STYLE,
    #             selected_style=TAB_SELECTED_STYLE),
    #     # html.Div([
    #     #     html.Img(src='./assets/process.png', style={'height': '100px', 'margin-right': '10px', 'align':'center'}),
    #     #     html.H1(format_date(fecha, format="MMMM YYYY", locale='es_DO').upper(), style={'textAlign': 'top-center'}, id='titulo-mes'),
    #     #     html.Div(id='contenido', className='content', style={'text-align': 'center'})
    #     #     ], style={'align': 'center'}),
    # ]),
    html.H1(style={'textAlign': 'center'},
            id='titulo-mes'),
    html.Div(id='tabs-content'
             ),

    # Hidden div to store the data
    dcc.Store(id='metric-data-store'),
    dcc.Store(id='app-data-store'),

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

# Callback for data refresh
# @app.callback(Output('metric-data-store', 'data'),
#               [Input('data-refresh-interval', 'n_intervals')])
# def refresh_data(n_intervals):
#     fetch_kpi_data()
#     return

# @app.callback(Output('app-data-store', 'data'),
#               [Input('data-refresh-interval', 'n_intervals')])
# def refresh_data(n_intervals):
#     get_app_data()
#     return

# Callback for automatic tab rotation
@app.callback(Output('tabs', 'value'),
              [Input('interval-component', 'n_intervals')],
              [State('tabs', 'value')])
def rotate_tabs(n_intervals, current_tab):
    tab_sequence = [a.value for a in tabs.children]
    current_index = tab_sequence.index(current_tab)
    next_index = (current_index + 1) % len(tab_sequence)
    return tab_sequence[next_index]

@app.callback(
    Output('metric-data-store', 'data'),
    Input('data-refresh-interval', 'n_intervals')
)
# Input('interval-component', 'n_intervals'))
def refresh_data(n):
    return metricas_pantalla2.main()

@app.callback(
    Output('app-data-store', 'data'),
    Input('data-refresh-interval', 'n_intervals')
)
# Input('interval-component', 'n_intervals'))
def refresh_data(n):
    filepath = r"C:\Users\jacevedo\OneDrive - Superintendencia de Bancos de la Republica Dominicana\Documents\ProUsuario Project\reporte_prousuario_app\data_prousuario_app.csv"
    df = pd.read_csv(filepath)
    query = """
    select count(UserId) from UserInfo
    where EmailVerified = 1 and UserIdentityVerificationStatus = 2
    """
    df = sql_tools.query_reader(query, creds='azure_db_user_report')
    df
    df.accepted_terms_and_conditions = df.accepted_terms_and_conditions.fillna(False)
    df.columns = df.columns.str.lower().str.replace(' ', '_')
    filtro_email = df.email_verified
    filtro_status = df.user_identity_verification_status == 2
    verif = df[filtro_status & filtro_email].copy()
    return metricas_pantalla2.main()

# Callback for data refresh
@app.callback([Output('tabs-content', 'children'),
               Output('titulo-mes', 'children')],
              [Input('tabs', 'value'),
               Input('metric-data-store', 'data')]
              )
def render_content(tab, data):
    if tab == 'tab-metricas':
        fecha = date.today()
        if fecha.day < 3:
            fecha = (fecha - MonthBegin(1)).date()
        # print(fecha)
        titulo_mes = format_date(fecha, format="MMMM YYYY", locale='es_DO').upper()
        # print(data['monto'])
        if math.isnan(data['monto']):
            data['monto'] = 0
        monto = f"DOP {data['monto'] / 1000:,.1f} K"
        if data['monto'] > 1000000:
            monto = f"DOP {data['monto']/1000000:,.2f} M"
        metrics_div = [html.Div([
            html.H2("RECLAMACIONES", style={'text-align': 'center', 'font-size': '30px'}),
            html.Div([html.H3("Recibidas:", className='metric-title'),
                      html.H3(data['recibidas_claims'], className='big-metric')], className='metric-grid'),
            html.Div([html.H3("Completadas:", className='metric-title'),
                      html.H3(data['salidas_claims'], className='big-metric')], className='metric-grid'),
            # html.Div([html.H3("Tiempo de respuesta:", className='metric-title'),
            #           html.H3(f"{math.floor(data['promedio_claims']):.0f} días", className='big-metric')], className='metric-grid'),
            # html.Div([html.H3("Casos a tiempo:", className='metric-title'),
            #           html.H3(f"{data['casos_claims']:.0%}", className='big-metric')], className='metric-grid'),
            html.Div([html.H3("Favorabilidad:", className='metric-title'),
                      html.H3(f"{data['favorabilidad']:.0%}", className='big-metric')], className='metric-grid'),
            html.Div([html.H3("Monto dispuesto a acreditar:", className='metric-title'),
                      html.H3(monto, className='big-metric')], className='metric-grid'),
        ], className='metric-box',
            style={'width': '50%', 'display': 'inline-block', 'box-shadow': '0 4px 8px 0 rgba(0,0,0,0.2)',
                   'border-radius': '10px', 'padding': '20px'}),
        html.Div([
            html.H2("Información Financiera".upper(), style={'text-align': 'center', 'font-size': '30px'}),
            html.Div([html.H3("Recibidas:", className='metric-title'),
                      html.H3(data['recibidas_info'], className='big-metric')]),
            html.Div([html.H3("Completadas:", className='metric-title'),
                      html.H3(data['salidas_info'], className='big-metric')]),
            html.Div([html.H3("Central de Riesgo Procesadas:", className='metric-title'),
                      html.H3(data['cantidad_central'], className='big-metric')]),
            # html.Div([html.H3("Tiempo de respuesta:", className='metric-title'),
            #           html.H3(f"{math.floor(data['promedio_info']):.0f} días", className='big-metric')]),
            # html.Div([html.H3("Casos a tiempo:", className='metric-title'),
            #           html.H3(f"{data['casos_info']:.0%}", className='big-metric')])
        ], className='metric-box',
            style={'width': '50%', 'display': 'inline-block', 'box-shadow': '0 4px 8px 0 rgba(0,0,0,0.2)',
                   'border-radius': '10px', 'padding': '20px'})
        ]
        return metrics_div, titulo_mes
    elif tab == 'tab-app':
        print('hola')
        return 1, 2


# Callback for tab content
# @app.callback(Output('tabs-content', 'children'),
#               [Input('tabs', 'value'),
#                Input('metric-data-store', 'data')])
# def render_content(tab, kpi_data):
#     if tab == 'tab-metricas':
#         return refresh_data

# Run the app
host = get_ip_address()
port = get_dash_port('pantalla_2')
if __name__ == '__main__':
    print('Corriendo Dash Pantalla 2')
    print(f'http://{host}:{port}')
    # app.run_server(debug=True, host=host, port=port)
    app.run_server(debug=True)
    # serve(app.server, host=host, port=port)
