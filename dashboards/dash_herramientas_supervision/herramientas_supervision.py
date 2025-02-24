"""
Creado el 19/6/2024 a las 10:17 AM

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
import pandas as pd
from waitress import serve
import plotly.express as px

from general_tools import get_ip_address
from sql_tools import query_reader
from kpi_module import get_kpi_data
from prousuario_tools import get_dash_port, get_sb_colors, get_categoria_producto


lista_bancos = ['ACTIVO', 'ADEMI', 'ADOPEM', 'ALAVER', 'APAP', 'ATLANTICO', 'BAGRICOLA',
 'BANCO BACC', 'BANCOTUI', 'BANDEX', 'BANESCO', 'BANFONDESA', 'BANRESERVAS', 'BDI',
 'BHD', 'BLH', 'BONANZA', 'BONAO', 'CARIBE', 'CIBAO', 'CITIBANK', 'COFACI', 'CONFISA',
 'DUARTE', 'EMPIRE', 'GRUFICORP', 'JMMB', 'LA NACIONAL', 'LAFISE', 'LEASCONFISA',
 'MAGUANA', 'MOCANA', 'MOTOR CREDITO', 'NORPRESA', 'OFICORP', 'PERAVIA', 'POPULAR',
 'PROMERICA', 'QIK BANCO DIGITAL', 'ROMANA', 'SANTA CRUZ', 'SCOTIABANKRD', 'UNION',
 'VIMENCA']

periods = pd.date_range('2023-01-01', date.today(), freq='Q', normalize=True).date

# Initialize the Dash app
app = dash.Dash(__name__)


# Define the layout of the app
app.layout = html.Div([
    html.Header([
        html.Img(src='./assets/prousuario-logo.svg', style={'height': '50px', 'margin-right': '10px'}),
        # Adjust logo size as needed
        html.H1("VERA | Herramientas Supervisión",
                # style={'display': 'inline-block', 'vertical-align': 'middle', 'margin-left': '10px'}
                )
    # ], style={'display': 'flex', 'align-items': 'flex-end', 'margin-bottom': '0px'}),
    ], style={'margin-bottom': '0px'}),
    html.Div([
        html.H2(['Generador listas',html.Br(),'de exclusión']),
        html.Button('Generar listas', id='lista_exclusion', n_clicks=0, style={'padding':10}),
        html.H1(id='numero_veces')
    ], style={
  # 'display': 'flex',
  'justify-content': 'center',
  # 'align-items': 'center',
        'margin-top':20,
  'text-align': 'center',
  'min-height': '100vh'
})
        # html.Div([
        #     # html.P('sidebar'),
        #         html.H3('Entidad'),
        #         dcc.Dropdown(options=[{'label':b, 'value':b} for b in lista_bancos], value='POPULAR', id='lista_bancos'),
        #         html.H3('Por trimestre'),
        #         dcc.Dropdown(options=[{'label':b, 'value':b} for b in periods], value=periods[-1], id='lista_periodos'),
        #         html.H3('Por rango de fecha'),
        #         dcc.DatePickerRange(style={'display': 'flex', 'align-items': 'flex-end', 'margin-bottom': '0px'}, id='rango_fecha'),
        #
        # ], style={'display': 'inline-block', 'vertical-align':'top', 'width': '20%',  'margin':10}),
        # html.Div([
        #     # html.H2('main'),
        #     html.Div(id='graph1'),
        # ], style={'display': 'inline-block', 'width': '75%', 'margin':10}),
])

@app.callback(
    Output('numero_veces', 'children'),
    Input('lista_exclusion', 'n_clicks')
)
def print_nclicks(value):
    if value == 0:
        result = ''
    else:
        result = f'se ha hecho click {value} veces'
    return result
#
# def update_graph1(banco, fecha):
#     query = (f"""select trim(b.descripcio) producto from pu01 a
#                 left join PRODUSERVI B on A.TIPOPRODUCTO = B.CODIGO
#                 left join registro_entidades c on c.codigoi = a.entidad
#                 where to_date(FECHAAPERTURARECLAMACION, 'DD/MM/YYYY') = date '2024-03-01'
#                 and c.nombre_corto = '{banco}'
#                 """)
#
#     df = query_reader(query, mode='all')
#     df.producto = df.producto.map(get_categoria_producto())
#     figure = px.bar(df.producto.value_counts(), template='presentation', text_auto=True,
#                     title='Cantidad por producto', width=500, height=400
#                     )
#     figure.update_layout(font_family='SairaMedium', yaxis_title=None, xaxis_title=None,
#                          showlegend=False, yaxis_visible=False, yaxis_showgrid=False)
#     return dcc.Graph(figure=figure)


# Run the app
host = get_ip_address()
port = get_dash_port('supervision')
if __name__ == '__main__':
    print('Corriendo Dash Herramientas Supervision')
    print(f'http://{host}:{port}')
    app.run_server(debug=True, host=host, port=port)
    # app.run_server(debug=True)
    # serve(app.server, host=host, port=port)