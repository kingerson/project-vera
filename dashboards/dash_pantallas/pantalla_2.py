"""Creado el 11/12/2023 a las 12:27 p. m.

@author: jacevedo
"""

from datetime import date
import math
import dash
from babel.dates import format_date
from dash import dcc, html
from dash.dependencies import Input, Output
from pandas.tseries.offsets import MonthBegin
from waitress import serve

import metricas_pantalla2
from general_tools import get_ip_address
from prousuario_tools import get_dash_port

fecha = date.today()
if fecha.day < 3:
    fecha = (fecha - MonthBegin(1)).date()
print(fecha)

# Initialize the Dash app
app = dash.Dash(
    __name__,
    title='Metricas Pantalla 2',
    # url_base_pathname='/pantalla2/'
)

# Define the layout of the app
app.layout = html.Div([
    # html.Meta(httpEquiv="refresh", content="3600"),
    dcc.Interval(
        id='interval-component',
        interval=3600 * 1000,  # in milliseconds
        n_intervals=0
    ),
    # dcc.Store(id='reclamos-data', data=metricas_pantalla2.main()),
    html.Header([
        html.Img(src='./assets/prousuario-logo.svg', style={'height': '50px', 'margin-right': '10px'}),
        # Adjust logo size as needed
        html.H1("VERA | Métricas ProUsuario", style={'display': 'inline-block', 'vertical-align': 'middle', 'margin-left': '10px'})
    ],  style={'display': 'flex', 'align-items': 'flex-end', 'margin-bottom': '20px'}),
    html.Div([
        html.Img(src='./assets/process.png', style={'height': '100px', 'margin-right': '10px', 'align':'center'}),
        html.H1(format_date(fecha, format="MMMM YYYY", locale='es_DO').upper(), style={'textAlign': 'top-center'}, id='titulo-mes'),
        html.Div(id='contenido', className='content', style={'text-align': 'center'})
        ], style={'align': 'center'}),

])

@app.callback(
    [Output('contenido', 'children'),
    Output('titulo-mes', 'children')],
    Input('interval-component', 'n_intervals')
)
def update_date(n):
    print(f'{n} ciclos han ocurrido')
    fecha = date.today()
    if fecha.day < 3:
        fecha = (fecha - MonthBegin(1)).date()
    print(fecha)
    titulo_mes = format_date(fecha, format="MMMM YYYY", locale='es_DO').upper()
    metricas = metricas_pantalla2.main()
    print(metricas['monto'])
    if math.isnan(metricas['monto']):
        metricas['monto'] = 0
    monto = f"DOP {metricas['monto'] / 1000:,.1f} K"
    if metricas['monto'] > 1000000:
        monto = f"DOP {metricas['monto']/1000000:,.2f} M"
    metrics_div = [html.Div([
        html.H2("RECLAMACIONES", style={'text-align': 'center', 'font-size': '30px'}),
        html.Div([html.H3("Recibidas:", className='metric-title'),
                  html.H3(metricas['recibidas_claims'], className='big-metric')], className='metric-grid'),
        html.Div([html.H3("Completadas:", className='metric-title'),
                  html.H3(metricas['salidas_claims'], className='big-metric')], className='metric-grid'),
        # html.Div([html.H3("Tiempo de respuesta:", className='metric-title'),
        #           html.H3(f"{math.floor(metricas['promedio_claims']):.0f} días", className='big-metric')], className='metric-grid'),
        # html.Div([html.H3("Casos a tiempo:", className='metric-title'),
        #           html.H3(f"{metricas['casos_claims']:.0%}", className='big-metric')], className='metric-grid'),
        html.Div([html.H3("Favorabilidad:", className='metric-title'),
                  html.H3(f"{metricas['favorabilidad']:.0%}", className='big-metric')], className='metric-grid'),
        html.Div([html.H3("Monto dispuesto a acreditar:", className='metric-title'),
                  html.H3(monto, className='big-metric')], className='metric-grid'),
    ], className='metric-box',
        style={'width': '50%', 'display': 'inline-block', 'box-shadow': '0 4px 8px 0 rgba(0,0,0,0.2)',
               'border-radius': '10px', 'padding': '20px'}),
    html.Div([
        html.H2("Información Financiera".upper(), style={'text-align': 'center', 'font-size': '30px'}),
        html.Div([html.H3("Recibidas:", className='metric-title'),
                  html.H3(metricas['recibidas_info'], className='big-metric')]),
        html.Div([html.H3("Completadas:", className='metric-title'),
                  html.H3(metricas['salidas_info'], className='big-metric')]),
        html.Div([html.H3("Central de Riesgo Procesadas:", className='metric-title'),
                  html.H3(metricas['cantidad_central'], className='big-metric')]),
        # html.Div([html.H3("Tiempo de respuesta:", className='metric-title'),
        #           html.H3(f"{math.floor(metricas['promedio_info']):.0f} días", className='big-metric')]),
        # html.Div([html.H3("Casos a tiempo:", className='metric-title'),
        #           html.H3(f"{metricas['casos_info']:.0%}", className='big-metric')])
    ], className='metric-box',
        style={'width': '50%', 'display': 'inline-block', 'box-shadow': '0 4px 8px 0 rgba(0,0,0,0.2)',
               'border-radius': '10px', 'padding': '20px'})
    ]
    return metrics_div, titulo_mes


# Run the app
host = get_ip_address()
port = get_dash_port('pantalla_2')
if __name__ == '__main__':
    print('Corriendo Dash Pantalla 2')
    print(f'http://{host}:{port}')
    # app.run_server(debug=True, host=host, port=port)
    serve(app.server, host=host, port=port)
