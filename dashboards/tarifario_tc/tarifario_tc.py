"""
Creado el 11/12/2023 a las 12:27 p. m.

@author: jacevedo
"""

from datetime import date
import numpy as np
import dash
import plotly.graph_objs as go
from babel.dates import format_date
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
from pandas.tseries.offsets import MonthBegin
import pandas as pd
from waitress import serve
import plotly.express as px
# import lectura_tarifarios
import dashboards.tarifario_tc.lectura_tarifarios as lectura_tarifarios
from general_tools import get_ip_address
from prousuario_tools import get_dash_port, get_sb_colors


#%%
# Initialize the Dash app
app = dash.Dash(__name__)

colores = get_sb_colors()

escala_len = len(px.colors.diverging.RdYlGn_r[1:])
escala_colores_dias = []
for idx, color in zip(np.arange(30,71,40/escala_len), px.colors.diverging.RdYlGn_r[1:]):
    escala_colores_dias.append({'range': [np.ceil(idx), np.ceil(idx + 40 / escala_len)], 'color': color})
    if idx == 30.0:
        escala_colores_dias.append({'range': [np.ceil(0), np.ceil(idx + 40 / escala_len)], 'color': color})

escala_colores_porciento = [{'range':[idx,idx+.5/escala_len], 'color':color} for idx, color in zip(np.arange(0.5,1.01,0.5/escala_len), px.colors.diverging.RdYlGn[:-1])]

gauge_color = colores['blue sb darker']


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

df = lectura_tarifarios.old()
cols = ['eif', 'marca', 'producto', 'nombre', 'cliente',
        'cargo', 'moneda', 'frecuencia', 'monto', 'porcentaje']
df = df[cols]
lista_eif = [{'label':eif, 'value':eif} for eif in df.eif.sort_values().unique()]
lista_marca = [{'label':eif, 'value':eif} for eif in df.marca.sort_values().unique()]
lista_producto = [{'label':eif, 'value':eif} for eif in df.producto.sort_values().unique()]
lista_nombre = [{'label':eif, 'value':eif} for eif in df.nombre.sort_values().unique() if eif is not None]
lista_cliente = [{'label':eif, 'value':eif} for eif in df.cliente.sort_values().unique() if eif is not None]
lista_cargo = [{'label': eif, 'value': eif} for eif in df.cargo.sort_values().unique() if eif is not None]
lista_moneda = ['DOP', 'USD']

# Define dropdown configurations
dropdowns = [
    {'label': 'Entidad', 'options': lista_eif, 'id': 'lista-eif', 'width': '13%'},
    {'label': 'Marca', 'options': lista_marca, 'id': 'lista-marca', 'width': '15%'},
    {'label': 'Tipo de Tarjeta', 'options': lista_producto, 'id': 'lista-producto', 'width': '15%'},
    {'label': 'Nombre Tarjeta', 'options': lista_nombre, 'id': 'lista-nombre', 'width': '23%'},
    {'label': 'Tipo de Cliente', 'options': lista_cliente, 'id': 'lista-cliente', 'width': '23%'},
    {'label': 'Tipo de Cargo', 'options': lista_cargo, 'id': 'lista-cargo', 'width': '37%'},
    {'label': 'Moneda', 'options': lista_moneda, 'id': 'lista-moneda', 'width': '12%'}
]

# Define custom HTML template with a custom title
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        {%favicon%}
        {%css%}
        <title>VERA | Tarifarios TC</title>  <!-- Custom browser tab title -->
    </head>
    <body>
        {%app_entry%}
        {%config%}
        {%scripts%}
        {%renderer%}
    </body>
</html>
'''

# Define the layout of the app
app.layout = html.Div([
        # html.Title(),  # Set the custom title for the browser tab
    html.Header([
        html.Img(src='./assets/prousuario-logo.svg', style={'height': '40px', 'margin-right': '10px', 'margin-bottom': '0px'}),
        html.H2("VERA | Tarifarios TC", style={'margin':'0px'}
                )
    ], style={'display': 'flex', 'height':'70px', 'align-items': 'center', 'margin': '0px', 'padding':'0 0px'}),
    html.H1(style={'textAlign': 'center'},
            id='titulo-mes'),
    html.Div([
        # html.H1(f'{df.shape}'),
        html.Div([
html.Div(
            [
                html.H3(dropdown['label'], style={'margin':'0px'}),
                dcc.Dropdown(
                    options=dropdown['options'],
                    value=None,
                    id=dropdown['id'],
                    style={'margin':'0px'}
                )
            ],
            style={
                'display': 'inline-block',
                'width': dropdown['width'],
                'align-items': 'flex-start',
                'margin-bottom': '0px',
                'margin-top': '0px'
            }
        ) for dropdown in dropdowns
        ],id='side-menu', style={'padding':'20px 20px', 'margin':'0px'}),
        # html.Div([
            html.Div([
                dash_table.DataTable(id='data-table',
                          columns=[{'name': col.title(), 'id': col} for col in df.columns],
                          data=df.to_dict('records'),
                          sort_action='native',
                                     style_header={
                                         'fontWeight': 'bold',  # Make column headers bold
                                         'fontSize': '18px',
                                         'fontFamily': 'Calibri',
                                         'textAlign': 'left',  # Align header text to the left (optional)
                                          'backgroundColor': '#0d3048',
                                          'color': 'white'
                                     },
                          style_data={
                                         'whiteSpace': 'normal',
                                         'height': 'auto',
                                    'fontFamily': 'Calibri',
                                     },
                                     style_table={'width':'100%'},
                                     # style_cell={'width':'1366px'},
                           style_cell_conditional=[
                                         {'if': {'column_id': 'eif'},
                                          'width': '5%'},
                                         {'if': {'column_id': 'marca'},
                                          'width': '5%'},
                               {'if': {'column_id': 'nombre'},
                                'width': '35%'},
                               {'if': {'column_id': 'cliente'},
                                'width': '5%'},
                               {'if': {'column_id': 'cargo'},
                                'width': '55%'},
                               {'if': {'column_id': 'moneda'},
                                'width': '5%'},
                               {'if': {'column_id': 'frecuencia'},
                                'width': '5%'},
                               {'if': {'column_id': 'monto'},
                                'width': '5%'},
                               {'if': {'column_id': 'porcentaje'},
                                'width': '5%'},
                                     ],
                          # filter_action='native',
                          page_size=50)
                ],
                id='content', style={'display': 'inline-block', 'width':'100%', 'align-items': 'center','padding':'20px 20px', 'margin-bottom': '20px'}
                )
        # ])
    ]),
    # Hidden div to store the data
    dcc.Store(id='data-ranking_tc'),
    # dcc.Store(id='lista-eif-store', data=lista_eif),
    # dcc.Store(id='lista-marca-store', data=lista_marca),
    # dcc.Store(id='lista-eif-store', data=lista_nombre)
])


# Callback for tab content
# @app.callback(Output('tabs-content', 'children'),
#               [Input('tabs', 'value'),
#                Input('kpi-data-store', 'data')])
# def render_content(tab, kpi_data):
@app.callback(
    [Output('data-table', 'data'),
     Output('lista-eif', 'options'),
     Output('lista-marca', 'options'),
     Output('lista-producto', 'options'),
     Output('lista-nombre', 'options'),
     Output('lista-cliente', 'options'),
     Output('lista-cargo', 'options'),
     Output('lista-moneda', 'options'),
],
    [Input('lista-eif', 'value'),
     Input('lista-marca', 'value'),
     Input('lista-producto', 'value'),
     Input('lista-nombre', 'value'),
     Input('lista-cliente', 'value'),
     Input('lista-cargo', 'value'),
     Input('lista-moneda', 'value')]
)
def filter_eif(eif, marca, producto, nombre, cliente, cargo, moneda):
    dff = df.copy()
    print(eif, marca, producto, nombre, moneda)
    # Dictionary for filter conditions
    filters = {
        'eif': eif,
        'marca': marca,
        'producto': producto,
        'nombre': nombre,
        'cliente': cliente,
        'cargo': cargo,
        'moneda': moneda
    }

    # Apply filters dynamically
    for col, value in filters.items():
        if value:
            dff = dff[dff[col] == value]

    # Helper function to generate dropdown options
    def generate_options(column):
        return [{'label': item, 'value': item} for item in dff[column].dropna().sort_values().unique()]

    # Generate updated options for dropdowns
    lista_eif = generate_options('eif')
    lista_marca = generate_options('marca')
    lista_producto = generate_options('producto')
    lista_nombre = generate_options('nombre')
    lista_cliente = generate_options('cliente')
    lista_cargo = generate_options('cargo')
    lista_moneda = generate_options('moneda')

    return [dff.to_dict('records'), lista_eif, lista_marca, lista_producto, lista_nombre, lista_cliente, lista_cargo, lista_moneda]

# %%
# Run the app
host = get_ip_address()
port = get_dash_port('tarifario_tc')
if __name__ == '__main__':
    print('Corriendo Dash Tarifarios')
    print(f'http://{host}:{port}')
    # app.run_server(debug=True, host=host, port=port)
    # app.run_server(debug=True)
    serve(app.server, host=host, port=port)
