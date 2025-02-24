import dash
from dash import dcc, html, Input, Output, State, dash_table
import pandas as pd
import dash_bootstrap_components as dbc

# Sample DataFrame (Replace this with your database connection)
data = {
    'Bank': ['Bank A', 'Bank B', 'Bank C', 'Bank A', 'Bank B'],
    'Brand': ['Visa', 'MasterCard', 'Amex', 'Visa', 'MasterCard'],
    'CardType': ['Credit', 'Debit', 'Credit', 'Debit', 'Credit'],
    'CardName': ['Gold', 'Silver', 'Platinum', 'Classic', 'Gold'],
    'Currency': ['USD', 'EUR', 'USD', 'EUR', 'USD'],
    'ClientType': ['Individual', 'Business', 'Individual', 'Business', 'Individual'],
    'FeeType': ['Annual', 'Transaction', 'Withdrawal', 'Annual', 'Transaction'],
    'FeeAmount': [100, 200, 150, 120, 180],
    'Month': ['2021-01', '2021-02', '2021-01', '2021-02', '2021-01']
}

df = pd.DataFrame(data)

# Initialize the app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Layout for Tab 1: Compare 2 Cards
tab1_layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H4('Card 1'),
            dcc.Dropdown(id='bank1-dropdown', options=[{'label': i, 'value': i} for i in df['Bank'].unique()], placeholder='Select Bank'),
            dcc.Dropdown(id='brand1-dropdown', placeholder='Select Brand'),
            dcc.Dropdown(id='type1-dropdown', placeholder='Select Card Type'),
            dcc.Dropdown(id='name1-dropdown', placeholder='Select Card Name'),
            dcc.Dropdown(id='currency1-dropdown', placeholder='Select Currency'),
        ], width=6),
        dbc.Col([
            html.H4('Card 2'),
            dcc.Dropdown(id='bank2-dropdown', options=[{'label': i, 'value': i} for i in df['Bank'].unique()], placeholder='Select Bank'),
            dcc.Dropdown(id='brand2-dropdown', placeholder='Select Brand'),
            dcc.Dropdown(id='type2-dropdown', placeholder='Select Card Type'),
            dcc.Dropdown(id='name2-dropdown', placeholder='Select Card Name'),
            dcc.Dropdown(id='currency2-dropdown', placeholder='Select Currency'),
        ], width=6),
    ], style={'margin-top': '20px'}),
    html.Br(),
    dbc.Button('Compare', id='compare-button', color='primary', n_clicks=0),
    html.Br(),
    html.Div(id='comparison-table')
])

# Layout for Tab 2: Top 10 Fees
tab2_layout = dbc.Container([
    html.H4('Select Fee Type'),
    dcc.Dropdown(
        id='fee-type-dropdown-tab2',
        options=[{'label': i, 'value': i} for i in df['FeeType'].unique()],
        placeholder='Select Fee Type'
    ),
    html.Br(),
    html.Div(id='top10-table')
])

# Layout for Tab 3: Filter Cards
tab3_layout = dbc.Container([
    dcc.Store(id='data-store'),
    html.H4('Filter Cards'),
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(id='bank-dropdown', options=[{'label': i, 'value': i} for i in df['Bank'].unique()], placeholder='Select Bank')
        ], width=4),
        dbc.Col([
            dcc.Dropdown(id='brand-dropdown', placeholder='Select Brand')
        ], width=4),
        dbc.Col([
            dcc.Dropdown(id='type-dropdown', placeholder='Select Card Type')
        ], width=4),
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(id='name-dropdown', placeholder='Select Card Name')
        ], width=4),
        dbc.Col([
            dcc.Dropdown(id='client-dropdown', placeholder='Select Client Type')
        ], width=4),
        dbc.Col([
            dcc.Dropdown(id='fee-type-dropdown-tab3', placeholder='Select Fee Type')
        ], width=4),
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(id='currency-dropdown', placeholder='Select Currency')
        ], width=4),
    ]),
    html.Br(),
    html.Div(id='filtered-data-table')
])

# Main app layout with Tabs
app.layout = dbc.Container([
    dcc.Tabs(id='tabs', value='tab-1', children=[
        dcc.Tab(label='Compare Cards', value='tab-1'),
        dcc.Tab(label='Top 10 Fees', value='tab-2'),
        dcc.Tab(label='Filter Cards', value='tab-3'),
    ]),
    html.Div(id='tabs-content')
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
    elif tab == 'tab-3':
        return tab3_layout

# Callbacks for Tab 1: Update dropdowns for Card 1
@app.callback(
    Output('brand1-dropdown', 'options'),
    Input('bank1-dropdown', 'value')
)
def update_brand1_options(selected_bank):
    if selected_bank is None:
        return []
    else:
        filtered_df = df[df['Bank'] == selected_bank]
        return [{'label': i, 'value': i} for i in filtered_df['Brand'].unique()]

@app.callback(
    Output('type1-dropdown', 'options'),
    Input('bank1-dropdown', 'value'),
    Input('brand1-dropdown', 'value')
)
def update_type1_options(selected_bank, selected_brand):
    if None in (selected_bank, selected_brand):
        return []
    filtered_df = df[(df['Bank'] == selected_bank) & (df['Brand'] == selected_brand)]
    return [{'label': i, 'value': i} for i in filtered_df['CardType'].unique()]

@app.callback(
    Output('name1-dropdown', 'options'),
    Input('bank1-dropdown', 'value'),
    Input('brand1-dropdown', 'value'),
    Input('type1-dropdown', 'value')
)
def update_name1_options(selected_bank, selected_brand, selected_type):
    if None in (selected_bank, selected_brand, selected_type):
        return []
    filtered_df = df[(df['Bank'] == selected_bank) & (df['Brand'] == selected_brand) & (df['CardType'] == selected_type)]
    return [{'label': i, 'value': i} for i in filtered_df['CardName'].unique()]

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
    filtered_df = df[(df['Bank'] == selected_bank) & (df['Brand'] == selected_brand) & (df['CardType'] == selected_type) & (df['CardName'] == selected_name)]
    return [{'label': i, 'value': i} for i in filtered_df['Currency'].unique()]

# Callbacks for Tab 1: Update dropdowns for Card 2
@app.callback(
    Output('brand2-dropdown', 'options'),
    Input('bank2-dropdown', 'value')
)
def update_brand2_options(selected_bank):
    if selected_bank is None:
        return []
    else:
        filtered_df = df[df['Bank'] == selected_bank]
        return [{'label': i, 'value': i} for i in filtered_df['Brand'].unique()]

@app.callback(
    Output('type2-dropdown', 'options'),
    Input('bank2-dropdown', 'value'),
    Input('brand2-dropdown', 'value')
)
def update_type2_options(selected_bank, selected_brand):
    if None in (selected_bank, selected_brand):
        return []
    filtered_df = df[(df['Bank'] == selected_bank) & (df['Brand'] == selected_brand)]
    return [{'label': i, 'value': i} for i in filtered_df['CardType'].unique()]

@app.callback(
    Output('name2-dropdown', 'options'),
    Input('bank2-dropdown', 'value'),
    Input('brand2-dropdown', 'value'),
    Input('type2-dropdown', 'value')
)
def update_name2_options(selected_bank, selected_brand, selected_type):
    if None in (selected_bank, selected_brand, selected_type):
        return []
    filtered_df = df[(df['Bank'] == selected_bank) & (df['Brand'] == selected_brand) & (df['CardType'] == selected_type)]
    return [{'label': i, 'value': i} for i in filtered_df['CardName'].unique()]

@app.callback(
    Output('currency2-dropdown', 'options'),
    Input('bank2-dropdown', 'value'),
    Input('brand2-dropdown', 'value'),
    Input('type2-dropdown', 'value'),
    Input('name2-dropdown', 'value')
)
def update_currency2_options(selected_bank, selected_brand, selected_type, selected_name):
    if None in (selected_bank, selected_brand, selected_type, selected_name):
        return []
    filtered_df = df[(df['Bank'] == selected_bank) & (df['Brand'] == selected_brand) & (df['CardType'] == selected_type) & (df['CardName'] == selected_name)]
    return [{'label': i, 'value': i} for i in filtered_df['Currency'].unique()]

# Callback for Tab 1: Generate comparison table
@app.callback(
    Output('comparison-table', 'children'),
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
        return ''
    if None in (bank1, brand1, type1, name1, currency1, bank2, brand2, type2, name2, currency2):
        return 'Please select all fields for both cards.'
    # Fetch data for both cards
    card1_df = df[(df['Bank'] == bank1) & (df['Brand'] == brand1) & (df['CardType'] == type1) & (df['CardName'] == name1) & (df['Currency'] == currency1)]
    card2_df = df[(df['Bank'] == bank2) & (df['Brand'] == brand2) & (df['CardType'] == type2) & (df['CardName'] == name2) & (df['Currency'] == currency2)]
    if card1_df.empty or card2_df.empty:
        return 'Card data not found.'
    # Prepare data for comparison
    card1_fees = card1_df[['FeeType', 'FeeAmount']].rename(columns={'FeeAmount': 'Card1 Fee'})
    card2_fees = card2_df[['FeeType', 'FeeAmount']].rename(columns={'FeeAmount': 'Card2 Fee'})
    comparison_df = pd.merge(card1_fees, card2_fees, on='FeeType', how='outer')
    comparison_df.fillna(0, inplace=True)
    # Apply conditional formatting
    def highlight_row(row):
        style = {}
        if row['Card1 Fee'] < row['Card2 Fee']:
            style['Card1 Fee'] = 'background-color: green; color: white;'
            style['Card2 Fee'] = 'background-color: red; color: white;'
        elif row['Card1 Fee'] > row['Card2 Fee']:
            style['Card1 Fee'] = 'background-color: red; color: white;'
            style['Card2 Fee'] = 'background-color: green; color: white;'
        return style

    # Generate data styles
    data_style = []
    for i in range(len(comparison_df)):
        row_id = f'row-{i}'
        styles = highlight_row(comparison_df.iloc[i])
        for column, style in styles.items():
            data_style.append({
                'if': {'row_index': i, 'column_id': column},
                'backgroundColor': style.split(';')[0].split(': ')[1],
                'color': style.split(';')[1].split(': ')[1]
            })

    # Create DataTable
    table = dash_table.DataTable(
        data=comparison_df.to_dict('records'),
        columns=[
            {'name': 'Fee Type', 'id': 'FeeType'},
            {'name': f'{bank1} Fee', 'id': 'Card1 Fee'},
            {'name': f'{bank2} Fee', 'id': 'Card2 Fee'}
        ],
        style_data_conditional=data_style,
        style_cell={'textAlign': 'center'},
        style_header={'fontWeight': 'bold'}
    )
    return table

# Callback for Tab 2: Update top 10 tables
@app.callback(
    Output('top10-table', 'children'),
    Input('fee-type-dropdown-tab2', 'value')
)
def update_top10_table(selected_fee_type):
    if selected_fee_type is None:
        return ''
    # Filter the DataFrame for the selected fee type
    filtered_df = df[df['FeeType'] == selected_fee_type]
    # Get top 10 highest fees
    highest_fees = filtered_df.nlargest(10, 'FeeAmount')
    # Get top 10 lowest fees
    lowest_fees = filtered_df.nsmallest(10, 'FeeAmount')
    # Create tables
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
    return dbc.Row([
        dbc.Col([
            html.H5('Top 10 Highest Fees'),
            highest_table
        ], width=6),
        dbc.Col([
            html.H5('Top 10 Lowest Fees'),
            lowest_table
        ], width=6),
    ])

# Callback for Tab 3: Update options and filtered data
@app.callback(
    Output('brand-dropdown', 'options'),
    Input('bank-dropdown', 'value')
)
def update_brand_options(selected_bank):
    dff = df.copy()
    if selected_bank:
        dff = dff[dff['Bank'] == selected_bank]
    return [{'label': i, 'value': i} for i in dff['Brand'].unique()]

@app.callback(
    Output('type-dropdown', 'options'),
    Input('bank-dropdown', 'value'),
    Input('brand-dropdown', 'value')
)
def update_type_options(selected_bank, selected_brand):
    dff = df.copy()
    if selected_bank:
        dff = dff[dff['Bank'] == selected_bank]
    if selected_brand:
        dff = dff[dff['Brand'] == selected_brand]
    return [{'label': i, 'value': i} for i in dff['CardType'].unique()]

@app.callback(
    Output('name-dropdown', 'options'),
    Input('bank-dropdown', 'value'),
    Input('brand-dropdown', 'value'),
    Input('type-dropdown', 'value')
)
def update_name_options(selected_bank, selected_brand, selected_type):
    dff = df.copy()
    if selected_bank:
        dff = dff[dff['Bank'] == selected_bank]
    if selected_brand:
        dff = dff[dff['Brand'] == selected_brand]
    if selected_type:
        dff = dff[dff['CardType'] == selected_type]
    return [{'label': i, 'value': i} for i in dff['CardName'].unique()]

@app.callback(
    Output('client-dropdown', 'options'),
    Input('bank-dropdown', 'value'),
    Input('brand-dropdown', 'value'),
    Input('type-dropdown', 'value'),
    Input('name-dropdown', 'value')
)
def update_client_options(selected_bank, selected_brand, selected_type, selected_name):
    dff = df.copy()
    if selected_bank:
        dff = dff[dff['Bank'] == selected_bank]
    if selected_brand:
        dff = dff[dff['Brand'] == selected_brand]
    if selected_type:
        dff = dff[dff['CardType'] == selected_type]
    if selected_name:
        dff = dff[dff['CardName'] == selected_name]
    return [{'label': i, 'value': i} for i in dff['ClientType'].unique()]

@app.callback(
    Output('fee-type-dropdown-tab3', 'options'),
    Input('bank-dropdown', 'value'),
    Input('brand-dropdown', 'value'),
    Input('type-dropdown', 'value'),
    Input('name-dropdown', 'value'),
    Input('client-dropdown', 'value')
)
def update_fee_type_options(selected_bank, selected_brand, selected_type, selected_name, selected_client):
    dff = df.copy()
    if selected_bank:
        dff = dff[dff['Bank'] == selected_bank]
    if selected_brand:
        dff = dff[dff['Brand'] == selected_brand]
    if selected_type:
        dff = dff[dff['CardType'] == selected_type]
    if selected_name:
        dff = dff[dff['CardName'] == selected_name]
    if selected_client:
        dff = dff[dff['ClientType'] == selected_client]
    return [{'label': i, 'value': i} for i in dff['FeeType'].unique()]

@app.callback(
    Output('currency-dropdown', 'options'),
    Input('bank-dropdown', 'value'),
    Input('brand-dropdown', 'value'),
    Input('type-dropdown', 'value'),
    Input('name-dropdown', 'value'),
    Input('client-dropdown', 'value'),
    Input('fee-type-dropdown-tab3', 'value')
)
def update_currency_options(selected_bank, selected_brand, selected_type, selected_name, selected_client, selected_fee_type):
    dff = df.copy()
    if selected_bank:
        dff = dff[dff['Bank'] == selected_bank]
    if selected_brand:
        dff = dff[dff['Brand'] == selected_brand]
    if selected_type:
        dff = dff[dff['CardType'] == selected_type]
    if selected_name:
        dff = dff[dff['CardName'] == selected_name]
    if selected_client:
        dff = dff[dff['ClientType'] == selected_client]
    if selected_fee_type:
        dff = dff[dff['FeeType'] == selected_fee_type]
    return [{'label': i, 'value': i} for i in dff['Currency'].unique()]

@app.callback(
    Output('filtered-data-table', 'children'),
    Input('bank-dropdown', 'value'),
    Input('brand-dropdown', 'value'),
    Input('type-dropdown', 'value'),
    Input('name-dropdown', 'value'),
    Input('client-dropdown', 'value'),
    Input('fee-type-dropdown-tab3', 'value'),
    Input('currency-dropdown', 'value')
)
def update_filtered_table(selected_bank, selected_brand, selected_type, selected_name, selected_client, selected_fee_type, selected_currency):
    dff = df.copy()
    if selected_bank:
        dff = dff[dff['Bank'] == selected_bank]
    if selected_brand:
        dff = dff[dff['Brand'] == selected_brand]
    if selected_type:
        dff = dff[dff['CardType'] == selected_type]
    if selected_name:
        dff = dff[dff['CardName'] == selected_name]
    if selected_client:
        dff = dff[dff['ClientType'] == selected_client]
    if selected_fee_type:
        dff = dff[dff['FeeType'] == selected_fee_type]
    if selected_currency:
        dff = dff[dff['Currency'] == selected_currency]
    # Display the filtered data
    if dff.empty:
        return 'No data found for the selected criteria.'
    table = dash_table.DataTable(
        data=dff.to_dict('records'),
        columns=[{'name': i, 'id': i} for i in dff.columns],
        page_size=10,
        style_cell={'textAlign': 'center'},
        style_header={'fontWeight': 'bold'}
    )
    return table

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=7777)
