# Created on 17/9/2024 by jacevedo

import dash
from waitress import serve
from general_tools import get_ip_address
from prousuario_tools import get_dash_port, get_sb_colors
import dash
from dash import dcc, html, Input, Output, State, dash_table
import pandas as pd
import dash_bootstrap_components as dbc
import dashboards.tarifario_tc.lectura_tarifarios as lectura_tarifarios
# import lectura_tarifarios

colores = get_sb_colors()

app = dash.Dash(__name__, assets_folder='assets', external_stylesheets=[dbc.themes.BOOTSTRAP])
# app = dash.Dash(__name__)
titulo = "Prueba"
puerto = None

TABS_STYLES = {
    'height': '44px',
}

TAB_STYLE = {
    # 'borderBottom': '1px solid #d6d6d6',
    # 'padding': '6px',
    # 'backgroundColor': '#5C7F91',
    # 'color': '#F0F3F5',
    # 'borderColor': '#0D3048',
    'padding': '0px 0px 0px 0px',
    'fontSize': '30px',
    'fontFamily': 'SairaLight'
}


TAB_SELECTED_STYLE = {
    # 'borderTop': '1px solid #d6d6d6',
    # 'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': get_sb_colors()['turquesa pro'],
    # 'color': '#0D3048',
    # 'padding': '6px',
    'padding': '0px 0px 0px 0px',
    'fontSize': '30px',
    'fontFamily': 'SairaBold'
}


app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        {%favicon%}
        {%css%}'''+f"<title>{titulo}</title>  <!-- Custom browser tab title -->"+'''</head>
    <body>
        {%app_entry%}
        {%config%}
        {%scripts%}
        {%renderer%}
    </body>
</html>
'''

def consolidate_fees(card_df):
    filtro_formato = card_df.formato_cargo == 'Monto Fijo'
    card_df.loc[filtro_formato, 'valor'] = card_df.loc[filtro_formato, 'monto_fijo']
    filtro_formato = card_df.formato_cargo == 'Porcentaje'
    card_df.loc[filtro_formato, 'valor'] = card_df.loc[filtro_formato, 'porcentaje']
    return card_df

df = lectura_tarifarios.new()
print(df.head())

# Layout for Tab 1: Compare 2 Cards
tab1_layout = html.Div([
    dbc.Row([
        dbc.Col([
            html.H4('Tarjeta A'),
            dcc.Dropdown(id='bank1-dropdown', options=[{'label':a, 'value':a} for a in df.eif.sort_values().unique()], placeholder='Escoge la entidad'),
            dcc.Dropdown(id='brand1-dropdown', placeholder='Escoge la marca'),
            dcc.Dropdown(id='type1-dropdown', placeholder='Escoge tipo de tarjeta'),
            dcc.Dropdown(id='name1-dropdown', placeholder='Escoge nombre de la tarjeta'),
            dcc.Dropdown(id='currency1-dropdown', placeholder='Escoge la moneda'),
        ], width=6),
        dbc.Col([
            html.H4('Tarjeta B'),
            dcc.Dropdown(id='bank2-dropdown', options=[{'label': i, 'value': i} for i in df['eif'].unique()], placeholder='Escoge la entidad'),
            dcc.Dropdown(id='brand2-dropdown', placeholder='Escoge la marca'),
            dcc.Dropdown(id='type2-dropdown', placeholder='Escoge tipo de tarjeta'),
            dcc.Dropdown(id='name2-dropdown', placeholder='Escoge nombre de la tarjeta'),
            dcc.Dropdown(id='currency2-dropdown', placeholder='Escoge la moneda'),
        ], width=6),
    ], style={'margin-top': '20px'}),
    html.Br(),
    dbc.Button('Comparar', id='compare-button', color='primary', n_clicks=0),
    html.Br(),
    html.H1('Favor seleccionar las características de las tarjetas', id='resultado', style={'textAlign':'center'}),
    html.Div(id='comparison-table', style={'padding': '0px 100px 0px 100px'}),
])



# Layout for Tab 2: Top 10 Fees
tab2_layout = html.Div([
    html.H4('Seleccione el cargo a comparar'),
    dcc.Dropdown(
        id='fee-type-dropdown-tab2',
        options=[{'label': i, 'value': i} for i in df['cargo'].unique()],
        placeholder='Escoga el cargo deseado.'
    ),
    html.Br(),
    html.Div(id='top10-table')
])

app.layout = html.Div([
    html.Header([
        html.Img(src='./assets/prousuario-logo.svg',
                 style={'height': '40px', 'margin-right': '10px', 'margin-bottom': '0px'}),
        html.H2("VERA | Tarifarios TC", style={'margin': '0px'}
                )
    ], style={'display': 'flex', 'height': '70px', 'align-items': 'center', 'margin': '0px', 'padding': '0 0px'}),
    html.H1(style={'textAlign': 'center'},
            id='titulo-mes'),
    # html.Div([
        dcc.Tabs(id='tabs', value='tab-1', children=[
            dcc.Tab(label='Comparador Tarjetas', value='tab-1', style=TAB_STYLE,
                selected_style=TAB_SELECTED_STYLE),
            dcc.Tab(label='Comparador Cargos', value='tab-2', style=TAB_STYLE,
                selected_style=TAB_SELECTED_STYLE),
            dcc.Tab(label='Tarifario General', value='tab-3', style=TAB_STYLE,
                selected_style=TAB_SELECTED_STYLE),
        ]),
        html.Div(id='tabs-content'
                 , style={'padding': '0px 30px 0px 30px'})
    # ])
])

# Callback to render tab content
@app.callback(
    Output('tabs-content', 'children'),
    Input('tabs', 'value')
)
def render_content(tab):
    if tab == 'tab-1':
        return tab1_layout
    elif tab == 'tab-2':
        return tab2_layout
    # elif tab == 'tab-3':
        # return tab3_layout


# Callbacks for Tab 1: Update dropdowns for Card 1
@app.callback(
    Output('brand1-dropdown', 'options'),
    Input('bank1-dropdown', 'value')
)
def update_brand1_options(selected_bank):
    if selected_bank is None:
        return []
    else:
        filtered_df = df[df['eif'] == selected_bank]
        return [{'label':a[1], 'value':a[0]} for a in filtered_df[['marca', 'marca_fixed']].value_counts().sort_index().index]

@app.callback(
    Output('type1-dropdown', 'options'),
    Input('bank1-dropdown', 'value'),
    Input('brand1-dropdown', 'value')
)
def update_type1_options(selected_bank, selected_brand):
    if None in (selected_bank, selected_brand):
        return []
    filtered_df = df[(df['eif'] == selected_bank) & (df['marca'] == selected_brand)]
    return [{'label':a[1], 'value':a[0]} for a in filtered_df[['producto', 'producto_fixed']].value_counts().sort_index().index]

@app.callback(
    Output('name1-dropdown', 'options'),
    Input('bank1-dropdown', 'value'),
    Input('brand1-dropdown', 'value'),
    Input('type1-dropdown', 'value')
)
def update_name1_options(selected_bank, selected_brand, selected_type):
    if None in (selected_bank, selected_brand, selected_type):
        return []
    filtered_df = df[(df['eif'] == selected_bank) & (df['marca'] == selected_brand) & (df['producto'] == selected_type)]
    return [{'label':a[1], 'value':a[0]} for a in filtered_df[['nombre', 'nombre_fixed']].value_counts().sort_index().index]

@app.callback(
    Output('currency1-dropdown', 'options'),
    Input('bank1-dropdown', 'value'),
    Input('brand1-dropdown', 'value'),
    Input('type1-dropdown', 'value'),
    Input('name1-dropdown', 'value')
)
def update_currency1_options(selected_bank, selected_brand, selected_type, selected_name):
    if None in (selected_bank, selected_brand, selected_type, selected_name):
        return []
    filtered_df = df[(df['eif'] == selected_bank) & (df['marca'] == selected_brand) & (df['producto'] == selected_type) & (df['nombre'] == selected_name)]
    return [{'label':a, 'value':a} for a in filtered_df['moneda'].unique()]


# Callbacks for Tab 1: Update dropdowns for Card 2
@app.callback(
    Output('brand2-dropdown', 'options'),
    Input('bank2-dropdown', 'value')
)
def update_brand1_options(selected_bank):
    if selected_bank is None:
        return []
    else:
        filtered_df = df[df['eif'] == selected_bank]
        return [{'label':a[1], 'value':a[0]} for a in filtered_df[['marca', 'marca_fixed']].value_counts().sort_index().index]

@app.callback(
    Output('type2-dropdown', 'options'),
    Input('bank2-dropdown', 'value'),
    Input('brand2-dropdown', 'value')
)
def update_type1_options(selected_bank, selected_brand):
    if None in (selected_bank, selected_brand):
        return []
    filtered_df = df[(df['eif'] == selected_bank) & (df['marca'] == selected_brand)]
    return [{'label':a[1], 'value':a[0]} for a in filtered_df[['producto', 'producto_fixed']].value_counts().sort_index().index]

@app.callback(
    Output('name2-dropdown', 'options'),
    Input('bank2-dropdown', 'value'),
    Input('brand2-dropdown', 'value'),
    Input('type2-dropdown', 'value')
)
def update_name1_options(selected_bank, selected_brand, selected_type):
    if None in (selected_bank, selected_brand, selected_type):
        return []
    filtered_df = df[(df['eif'] == selected_bank) & (df['marca'] == selected_brand) & (df['producto'] == selected_type)]
    return [{'label':a[1], 'value':a[0]} for a in filtered_df[['nombre', 'nombre_fixed']].value_counts().sort_index().index]

@app.callback(
    Output('currency2-dropdown', 'options'),
    Input('bank2-dropdown', 'value'),
    Input('brand2-dropdown', 'value'),
    Input('type2-dropdown', 'value'),
    Input('name2-dropdown', 'value')
)
def update_currency1_options(selected_bank, selected_brand, selected_type, selected_name):
    if None in (selected_bank, selected_brand, selected_type, selected_name):
        return []
    filtered_df = df[(df['eif'] == selected_bank) & (df['marca'] == selected_brand) & (df['producto'] == selected_type) & (df['nombre'] == selected_name)]
    return [{'label':a, 'value':a} for a in filtered_df['moneda'].unique()]


# Callback for Tab 1: Generate comparison table
@app.callback(
    Output('comparison-table', 'children'),
    Output('resultado', 'children'),
    Input('compare-button', 'n_clicks'),
    State('bank1-dropdown', 'value'),
    State('brand1-dropdown', 'value'),
    State('type1-dropdown', 'value'),
    State('name1-dropdown', 'value'),
    State('currency1-dropdown', 'value'),
    State('bank2-dropdown', 'value'),
    State('brand2-dropdown', 'value'),
    State('type2-dropdown', 'value'),
    State('name2-dropdown', 'value'),
    State('currency2-dropdown', 'value')
)
def update_comparison_table(n_clicks, bank1, brand1, type1, name1, currency1, bank2, brand2, type2, name2, currency2):
    if n_clicks == 0:
        return '', 'Seleccione las características de las tarjetas.'
    if None in (bank1, brand1, type1, name1, currency1, bank2, brand2, type2, name2, currency2):
        return '', 'Favor seleccionar todas las opciones para ambas tarjetas.'
    # Fetch data for both cards
    card1_df = df[(df['eif'] == bank1) & (df['marca'] == brand1) & (df['producto'] == type1) & (df['nombre'] == name1) & (df['moneda'] == currency1)]
    card2_df = df[(df['eif'] == bank2) & (df['marca'] == brand2) & (df['producto'] == type2) & (df['nombre'] == name2) & (df['moneda'] == currency2)]
    if card1_df.empty or card2_df.empty:
        return 'Tarjeta no encontrada.'
    # Prepare data for comparison
    card1_df = consolidate_fees(card1_df.copy())
    card2_df = consolidate_fees(card2_df.copy())
    key_cols = ['cargo', 'formato_cargo', 'frecuencia', 'valor']
    key_cols = ['cargo', 'valor']
    card1_fees = card1_df[key_cols].rename(columns={'valor': 'Monto Tarjeta A'})
    card2_fees = card2_df[key_cols].rename(columns={'valor': 'Monto Tarjeta B'})
    comparison_df = pd.merge(card1_fees, card2_fees, on=key_cols[:-1], how='outer')
    comparison_df.fillna(0, inplace=True)
    # Apply conditional formatting
    def highlight_row(row, count_a, count_b):
        style = {}
        if row['Monto Tarjeta A'] < row['Monto Tarjeta B']:
            style['Monto Tarjeta A'] = 'background-color: green; color: white;'
            style['Monto Tarjeta B'] = 'background-color: red; color: white;'
            count_a += 1
        elif row['Monto Tarjeta A'] > row['Monto Tarjeta B']:
            style['Monto Tarjeta A'] = 'background-color: red; color: white;'
            style['Monto Tarjeta B'] = 'background-color: green; color: white;'
            count_b += 1
        return style, count_a, count_b

    # Generate data styles
    data_style = []
    count_a = 0
    count_b = 0
    # comparison_df.loc[len(comparison_df)] = ['Categorias a favor', None, None, count_a, count_b]
    for i in range(len(comparison_df)):
        row_id = f'row-{i}'
        styles, count_a, count_b = highlight_row(comparison_df.iloc[i], count_a, count_b)
        for column, style in styles.items():
            data_style.append({
                'if': {'row_index': i, 'column_id': column},
                'backgroundColor': style.split(';')[0].split(': ')[1],
                'color': style.split(';')[1].split(': ')[1]
            })

    # Create DataTable
    # comparison_df.loc[len(comparison_df)-1] = ['Categorias a favor', None, None, count_a, count_b]
    # print(comparison_df.columns)
    # print(comparison_df)
    columns=[
        {'name': 'Concepto Cargo/Comisión', 'id': 'cargo'},
        {'name': f'{bank1}', 'id': 'Monto Tarjeta A'},
        {'name': f'{bank2}', 'id': 'Monto Tarjeta B'}
    ]
    if "formato_cargo" in comparison_df.columns:
        columns = [
            {'name': 'Concepto Cargo/Comisión', 'id': 'cargo'},
            {'name': 'Formato de cobro', 'id': 'formato_cargo'},
            {'name': 'Frecuencia', 'id': 'frecuencia'},
            {'name': f'{bank1}', 'id': 'Monto Tarjeta A'},
            {'name': f'{bank2}', 'id': 'Monto Tarjeta B'}
        ]
    table = dash_table.DataTable(
        data=comparison_df.to_dict('records'),
        columns=columns,
        style_data_conditional=data_style,
        style_cell={'textAlign': 'left', 'fontFamily': 'Calibri'},
        style_header={'fontWeight': 'bold'}
    )
    if count_a > count_b:
        resultado = f"{brand1} {name1} de {bank1} ganó en {count_a} categorias y {brand2} {name2} de {bank2} en {count_b}"
    elif count_a < count_b:
        resultado = f"{brand2} {name2} de {bank2} ganó en {count_a} categorias y {brand1} {name1} de {bank1} en {count_a}"
    else:
        resultado = f"Ambas tarjetas quedaron empate cantidad de categorías"
    return table, resultado


# Callback for Tab 2: Update top 10 tables
@app.callback(
    Output('top10-table', 'children'),
    Input('fee-type-dropdown-tab2', 'value')
)
def update_top10_table(selected_fee_type):
    if selected_fee_type is None:
        return ''
    # Filter the DataFrame for the selected fee type
    filtered_df = df[df['cargo'] == selected_fee_type]
    filtered_df = consolidate_fees(filtered_df.copy())
    # print(filtered_df.valor.apply(lambda x: type(x)).value_counts())
    filtered_df.valor = filtered_df.valor.fillna(0).astype(float)
    # Get top 10 highest fees
    highest_fees = filtered_df.nlargest(10, 'valor')
    # Get top 10 lowest fees
    lowest_fees = filtered_df.nsmallest(10, 'valor')
    # Create tables
    keycols = [
        'eif', 'marca_fixed', 'producto_fixed', 'nombre_fixed',
        'formato_cargo', 'valor'
    ]
    highest_fees = highest_fees[keycols]
    lowest_fees = lowest_fees[keycols]
    lowest_fees.columns = lowest_fees.columns.str.replace('_fixed', '').str.replace('_', ' ').str.title()
    highest_fees.columns = highest_fees.columns.str.replace('_fixed', '').str.replace('_', ' ').str.title()
    highest_table = dash_table.DataTable(
        data=highest_fees.to_dict('records'),
        columns=[{'name': i, 'id': i} for i in highest_fees.columns],
        style_cell={'textAlign': 'center'},
        style_header={'fontWeight': 'bold'}
    )
    lowest_table = dash_table.DataTable(
        data=lowest_fees.to_dict('records'),
        columns=[{'name': i, 'id': i} for i in lowest_fees.columns],
        style_cell={'textAlign': 'center'},
        style_header={'fontWeight': 'bold'}
    )
    # Display the tables side by side
    return [
        dbc.Row([
            html.H5('10 Tarjetas más caras'),
            highest_table
        ]),
        dbc.Row([]),
        dbc.Row([
            html.H5('10 Tarjetas más baratas'),
            lowest_table
        ],),
    ]
# %%
# Run the app
host = get_ip_address()
# port = get_dash_port(puerto)
port = 9999
if __name__ == '__main__':
    print('Corriendo Dash Tarifarios')
    print(f'http://{host}:{port}')
    # app.run_server(debug=True, host=host, port=port)
    # app.run_server(debug=True)
    serve(app.server, host=host, port=port)