"""
Creado el 11/12/2023 a las 12:27 p. m.

@author: jacevedo
"""

from datetime import date
import numpy as np
import dash
import dash
import plotly.graph_objs as go
from babel.dates import format_date
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
from pandas.tseries.offsets import MonthBegin
from sql_tools import query_reader
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
    # 'height': '10px',
}

TAB_STYLE = {
    # 'borderBottom': '1px solid #d6d6d6',
    'padding': '0px 0px 0px 0px',
    # 'backgroundColor': '#5C7F91',
    # 'color': '#F0F3F5',
    # 'borderColor': '#0D3048',
    'font-size': '32px',
    'font-family': 'SairaLight'
}


TAB_SELECTED_STYLE = {
    # 'borderTop': '1px solid #d6d6d6',
    # 'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': get_sb_colors()['turquesa pro'],
    # 'color': '#0D3048',
    # 'padding': '6px',
    'padding': '0px 0px 0px 0px',
    'font-size': '32px',
    'font-family': 'SairaBold'
}


#%%

cards = lectura_tarifarios.new()

lista_eif_a = [{'label':a, 'value':a} for a in cards.eif.sort_values().unique()]
lista_marca_a = [{'label':a[1], 'value':a[0]} for a in cards[['marca', 'marca_fixed']].value_counts().sort_index().index]
lista_producto_a = [{'label':a[1], 'value':a[0]} for a in cards[['producto', 'producto_fixed']].value_counts().sort_index().index]
lista_nombre_a = [{'label':a[1], 'value':a[0]} for a in cards[['nombre', 'nombre_fixed']].value_counts().sort_index().index]
lista_moneda_a = ['DOP', 'USD']

lista_eif_b = lista_eif_a
lista_marca_b = lista_marca_a
lista_producto_b =lista_producto_a
lista_nombre_b = lista_nombre_a
lista_moneda_b = lista_moneda_a

# Define dropdown configurations
dropdowns_a = [
    {'label': 'Entidad', 'options': lista_eif_a, 'id': 'lista-eif-a', 'width': '13%'},
    {'label': 'Marca', 'options': lista_marca_a, 'id': 'lista-marca-a', 'width': '15%'},
    {'label': 'Tipo de Tarjeta', 'options': lista_producto_a, 'id': 'lista-producto-a', 'width': '15%'},
    {'label': 'Nombre Tarjeta', 'options': lista_nombre_a, 'id': 'lista-nombre-a', 'width': '23%'},
    {'label': 'Moneda', 'options': lista_moneda_a, 'id': 'lista-moneda-a', 'width': '12%'}
]

dropdowns_b = [
    {'label': 'Entidad', 'options': lista_eif_b, 'id': 'lista-eif-b', 'width': '13%'},
    {'label': 'Marca', 'options': lista_marca_b, 'id': 'lista-marca-b', 'width': '15%'},
    {'label': 'Tipo de Tarjeta', 'options': lista_producto_b, 'id': 'lista-producto-b', 'width': '15%'},
    {'label': 'Nombre Tarjeta', 'options': lista_nombre_b, 'id': 'lista-nombre-b', 'width': '23%'},
    {'label': 'Moneda', 'options': lista_moneda_b, 'id': 'lista-moneda-b', 'width': '12%'}
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

cell_style = [
    {'if': {'column_id': 'eif'}, 'width': '5%'},
    {'if': {'column_id': 'marca'}, 'width': '5%'},
    {'if': {'column_id': 'nombre'}, 'width': '35%'},
    {'if': {'column_id': 'cliente'}, 'width': '5%'},
    {'if': {'column_id': 'cargo'}, 'width': '55%'},
    {'if': {'column_id': 'moneda'}, 'width': '5%'},
    {'if': {'column_id': 'frecuencia'}, 'width': '5%'},
    {'if': {'column_id': 'monto'}, 'width': '5%'},
    {'if': {'column_id': 'porcentaje'}, 'width': '5%'},
]

tab_comparativo = (
html.Div([
    html.Div([

        html.Div([        html.H2('Tarjeta A', style={'textAlign': 'left',
                                    'padding': '0px 0px 0px 0px',
                                    'margin-bottom': '0px',
                                    'margin-top': '0px'}),]+
            [

            html.Div([
                html.H3(dropdown['label'], style={'margin': '0px'}),
                dcc.Dropdown(
                    options=dropdown['options'],
                    value=None,
                    id=dropdown['id'],
                    style={'margin': '0px'}
                    )
                ], style={
                'display': 'inline-block',
                'width': dropdown['width'],
                'align-items': 'flex-start',
                'margin-bottom': '0px',
                'margin-top': '0px'
                }
            ) for dropdown in dropdowns_a]
            , id='menu-tarjeta-a', style={'padding': '20px 20px', 'margin': '0px', 'margin-bottom': '0px',
                'margin-top': '0px'}),
        ]),
    html.Div([

        html.Div([html.H2('Tarjeta B', style={'textAlign': 'left',
                                    'padding': '0px 0px 0px 0px',
                                    'margin-bottom': '0px',
                                    'margin-top': '0px'}),]+[
            html.Div([
                html.H3(dropdown['label'], style={'margin': '0px'}),
                dcc.Dropdown(
                    options=dropdown['options'],
                    value=None,
                    id=dropdown['id'],
                    style={'margin': '0px'}
                )
            ], style={
                'display': 'inline-block',
                'width': dropdown['width'],
                'align-items': 'flex-start',
                'margin-bottom': '0px',
                'margin-top': '0px'
            }
            ) for dropdown in dropdowns_b]
            , id='menu-tarjeta-b', style={'padding': '20px 20px', 'margin': '0px', 'margin-bottom': '0px',
                                     'margin-top': '0px'}),
        ]),
    html.Div([
    ],id='texto-tarjeta-a')
    ],
    )
)

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
    dcc.Tabs(id="tabs", value='tab-2', children=[
        dcc.Tab(label='Tabla de Tarifarios', className='metric-title', value='tab-1', style=TAB_STYLE,
                selected_style=TAB_SELECTED_STYLE),
        dcc.Tab(label='Comparativo Tarjetas', className='metric-title', value='tab-2', style=TAB_STYLE,
                selected_style=TAB_SELECTED_STYLE),
    ]),
    html.Div(tab_comparativo, id='tabs-content'

             ),

        # ])

    # Hidden div to store the data
    dcc.Store(id='data-ranking_tc'),
    # dcc.Store(id='lista-eif-store', data=lista_eif),
    # dcc.Store(id='lista-marca-store', data=lista_marca),
    # dcc.Store(id='lista-eif-store', data=lista_nombre)
])


#Callback for tab content
@app.callback(Output('tabs-content', 'children'),
              Input('tabs', 'value')
              )
def render_content(tab):
    if tab == 'tab-2':
        return tab_comparativo
    #     return tab_tarifario
    # elif tab == 'tab-1':
    #     return tab_comparativo
    # elif tab == 'tab-1':
    #     return tab_evolucion


# Gets selected card data
@app.callback(
     Output('texto-tarjeta-a', 'children')
    ,
    [Input('lista-eif-a', 'value'),
     Input('lista-marca-a', 'value'),
     Input('lista-producto-a', 'value'),
     Input('lista-nombre-a', 'value'),
     Input('lista-moneda-a', 'value'),
     ]
)
def filter_options(eif, marca, producto, nombre, moneda):
    if all([eif, marca, producto, nombre, moneda]):
        # marca = [a['value'] for a in lista_marca_a if a['label'] == marca][0]
        # producto = [a['value'] for a in lista_producto_a if a['label'] == producto][0]
        # nombre = [a['value'] for a in lista_nombre_a if a['label'] == nombre][0]
        query = f"""
        select 
        distinct lpad(a.entidad, 4, '0')
        -- a.marca||
        ||lpad(a.codigo, 6, '0')
        --||lpad(a.CLIENTEOBJ, 3, '0')||
                  ||CASE 
                  WHEN moneda = 'DOP' THEN '01'
                  WHEN moneda = 'USD' THEN '02'
                  end
                  unique_id
        , fecha
        , c.NOMBRE_CORTO eif
        , trim(b.DESCRIPCIO) marca
        , trim(e.DESCRIPCIO) producto
        , a.nombre nombre
        , d.DESCRIPCIO cliente
        , g.moneda moneda
        , g.cargo cargo
        , g.frecuencia frecuencia
        , g.formato_cargo formato_cargo
        , g.montofijo monto_fijo
        , g.minimo minimo
        , g.maximo maximo
        , g.porcentaje porcentaje
        from fincomunes.tc1b a
        left join fincomunes.marcatarje b on a.marca = b.codigo
        left join fincomunes.REGISTRO_ENTIDADES c on c.CODIGOI = a.entidad
        left join fincomunes.CATEGORIAS_CLIENTES d on d.CODIGO = a.CLIENTEOBJ
        left join fincomunes.PRODUSERVI E on E.CODIGO = a.TIPOPROD
        LEFT JOIN (
            SELECT
            ano||lpad(mes, 2, '0') fecha
            , e.CODIGO
            , i.conceptos cargo
            , e.monedaoper moneda
            , F.DESCRIPCION frecuencia
            , e.ENTIDAD entidad
            , h.DESCRIPCIO formato_cargo
            , e.montofijo montofijo
            , e.LIMESCMIN minimo
            , e.LIMESCMAX maximo
            , e.porcentaje porcentaje
            FROM TC02 e
            left join t010 f on e.PERIODICID = f.codigo
            left join fincomunes.FORMATOS_COBRO h on e.formato = h.codigo
            left join MONITOREO.t_tabla_89 i on e.codigoconc = i.código
            where ano||lpad(mes, 2, '0') = '202407'
        ) g ON g.codigo||g.entidad = a.codigo||a.entidad
        where a.TIPOPAGO = 'TC' and CLIENTEOBJ in(101, 102)
        and a.ano||lpad(a.mes, 2, '0') = '202407' and NOMBRE_CORTO != 'ATLANTICO'
        and c.NOMBRE_CORTO = '{eif}' and trim(b.DESCRIPCIO) = '{marca}' and trim(e.DESCRIPCIO) = '{producto}'
        and a.nombre = '{nombre}' and g.moneda = '{moneda}'
        """
        card = query_reader(query)
        print(card)
        cargos = dict()
        for c in card.cargo:
            filtro = card.cargo == c
            formato = card.loc[filtro, 'formato_cargo'].values[0]
            if formato == 'Monto Fijo':
                monto = f'{moneda} {card.loc[filtro, 'monto_fijo'].values[0]:,.2f}'
            elif formato == 'Porcentaje':
                monto = f'{card.loc[filtro, 'porcentaje'].values[0]}%'
            elif formato == 'Escala de valores fijos':
                monto = f"{moneda} {card.loc[filtro, 'minimo'].values[0]}-{card.loc[filtro, 'maximo'].values[0]}"
            elif formato == 'Escala de valores porcentuales':
                monto = f"{card.loc[filtro, 'minimo'].values[0]}-{card.loc[filtro, 'maximo'].values[0]}%"
            elif formato == 'Porcentaje Limitado por escala de valores fijos':
                monto = f"{moneda} {card.loc[filtro, 'minimo'].values[0]}-{card.loc[filtro, 'maximo'].values[0]} / {card.loc[filtro, 'porcentaje'].values[0]}%"
            elif formato == 'Porcentaje Limitado por monto fijo mínimo':
                monto = f"{moneda} {card.loc[filtro, 'monto_fijo'].values[0]} / {card.loc[filtro, 'porcentaje'].values[0]}%"
            elif formato == 'Monto fijo más porcentaje':
                monto = f"{moneda} {card.loc[filtro, 'monto_fijo'].values[0]} + {card.loc[filtro, 'porcentaje'].values[0]}%"
            cargos[c] = monto
        cargos_string = ""
        for x, y in cargos.items():
            cargos_string += f'| {x}| {y}|'

        card = dcc.Markdown(f"""
        ### {eif}
        ## {marca} {nombre}
        _{producto}_
        ---
        | Cargos | Costo |
        |----------|----------|
        """+cargos_string

                            )

    else:
        card = 'No se ha escogido'
    return card

# Options delimiter
@app.callback([
     Output('lista-eif-a', 'options'),
     Output('lista-marca-a', 'options'),
     Output('lista-producto-a', 'options'),
     Output('lista-nombre-a', 'options'),
     Output('lista-moneda-a', 'options'),
    ],
    [Input('lista-eif-a', 'value'),
     Input('lista-marca-a', 'value'),
     Input('lista-producto-a', 'value'),
     Input('lista-nombre-a', 'value'),
     Input('lista-moneda-a', 'value'),
     ]
)
def filter_options(eif, marca, producto, nombre, moneda):
    dff = cards.copy()
    print(eif, marca, producto, nombre, moneda)
    # Dictionary for filter conditions
    filters = {
        'eif': eif,
        'marca': marca,
        'producto': producto,
        'nombre': nombre,
        'moneda': moneda
    }

    for col, value in filters.items():
        if value:
            dff = dff[dff[col] == value]

    def generate_options(column):
        if column in ('marca', 'producto', 'nombre'):
            lista = [{'label': a[1], 'value': a[0]} for a in
                             dff[[column, f'{column}_fixed']].value_counts().sort_index().index]
        else:
            lista = [{'label': item, 'value': item} for item in dff[column].dropna().sort_values().unique()]
        return lista


    # Generate updated options for dropdowns
    lista_eif = generate_options('eif')
    lista_marca = generate_options('marca')
    lista_producto = generate_options('producto')
    lista_nombre = generate_options('nombre')
    lista_moneda = generate_options('moneda')
    # print(lista_eif)
    return [lista_eif, lista_marca, lista_producto, lista_nombre, lista_moneda]

# @app.callback(
#     [
#         # Output('data-table', 'data'),
#      Output('lista-eif-a', 'value'),
#      Output('lista-marca-a', 'value'),
#      Output('lista-producto-a', 'value'),
#      Output('lista-nombre-a', 'value'),
#      Output('lista-moneda-a', 'value'),
#      # Output('lista-eif-b', 'value'),
#      # Output('lista-marca-b', 'value'),
#      # Output('lista-producto-b', 'value'),
#      # Output('lista-nombre-b', 'value'),
#      # Output('lista-moneda-b', 'value')
# ],
#     [Input('lista-eif-a', 'value'),
#      Input('lista-marca-a', 'value'),
#      Input('lista-producto-a', 'value'),
#      Input('lista-nombre-a', 'value'),
#      Input('lista-moneda-a', 'value'),
#      # Input('lista-eif-b', 'value'),
#      # Input('lista-marca-b', 'value'),
#      # Input('lista-producto-b', 'value'),
#      # Input('lista-nombre-b', 'value'),
#      # Input('lista-moneda-b', 'value')
#      ]
# )
# def filter_eif(
#         eif_a, marca_a, producto_a, nombre_a, moneda_a,
#         # eif_b, marca_b, producto_b, nombre_b, moneda_b
# ):
#     dff = cards.copy()
#     # Dictionary for filter conditions
#     filters = {
#         'eif': eif_a,
#         'marca': marca_a,
#         'producto': producto_a,
#         'nombre': nombre_a,
#         'moneda': moneda_a
#     }
#
#     query = f"""
#         select
#         , c.NOMBRE_CORTO eif
#         , trim(b.DESCRIPCIO) marca
#         , trim(e.DESCRIPCIO) producto
#         , a.nombre nombre
#         , moneda
#         from fincomunes.tc1b a
#         left join fincomunes.marcatarje b on a.marca = b.codigo
#         left join fincomunes.REGISTRO_ENTIDADES c on c.CODIGOI = a.entidad
#         left join fincomunes.PRODUSERVI E on E.CODIGO = a.TIPOPROD
#         LEFT JOIN (
#             SELECT
#             distinct monedaoper moneda
#             , entidad
#             , codigo
#             FROM fincomunes.TC02
#             where ano||lpad(mes, 2, '0') = '202407'
#         ) g ON g.codigo||g.entidad = a.codigo||a.entidad
#         where a.TIPOPAGO = 'TC' and CLIENTEOBJ = 101
#         and a.ano||lpad(a.mes, 2, '0') = '202407' and NOMBRE_CORTO != 'ATLANTICO'
#         and c.nombre_corto = {eif_a} and trim(b.DESCRIPCIO) = {marca_a}
#         and c.nombre = {nombre_a} and trim(e.DESCRIPCIO) = {producto_a}
#         and moneda = {moneda_a}
#     """
#     lel = query_reader(query)
#     print(lel)
#
#     # Apply filters dynamically
#     for col, value in filters.items():
#         if value:
#             dff = dff[dff[col] == value]
#
#     # Helper function to generate dropdown options
#     def generate_options(column):
#         return [{'label': item, 'value': item} for item in dff[column].dropna().sort_values().unique()]
#
#     # Generate updated options for dropdowns
#     lista_eif = generate_options('eif')
#     lista_marca = generate_options('marca')
#     lista_producto = generate_options('producto')
#     lista_nombre = generate_options('nombre')
#     lista_moneda = generate_options('moneda')
#
#     return [dff.to_dict('records'), lista_eif, lista_marca, lista_producto, lista_nombre, lista_moneda]



# %%
# Run the app
host = get_ip_address()
port = get_dash_port('tarifario_tc')
port = 4444
if __name__ == '__main__':
    print('Corriendo Dash Tarifarios')
    print(f'http://{host}:{port}')
    app.run_server(debug=True, host=host, port=port)
    # app.run_server(debug=True)
    # serve(app.server, host=host, port=port)
