"""
Creado el 19/7/2022 a las 4:25 p. m.

@author: jacevedo
"""

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from flask import Flask
from waitress import serve

import calcula_pendientes
import reclamos_reading
from general_tools import get_ip_address
from kpi_module import get_kpi_graphs
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
                url_base_pathname='/reclamaciones/'
                )
app.title = 'Reclamaciones'
# server = app.server


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
df = reclamos_reading.main('2022-06-01')
# data = df.groupby('etapa_actual').count()['codigo']
#
# fig = px.bar(data)

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
                    html.Img(src='assets/logo_sb.png', height=110, width=140),
                ], style={'display': 'inline-block', 'height': '80px', 'float': 'left'}),
                html.Div([
                    html.H1('VERA', id='titulo-cabecera', style={'display': 'inline-block', 'font-weight': 'bold', 'height': '80px', 'text-align': 'top'}),
                    html.H2('Dash Reclamaciones', id='sub-titulo', style={'padding-left': '10px', 'display': 'inline-block', 'height': '80px', 'text-align': 'top'})
                ], style={'display': 'inline-block', 'height': '60px', 'padding': "20px", "float": "left"})
            ], style={'width': '45%', 'display': 'inline-block'}),
            html.Div([
                dcc.Tabs(id="tabs", value='tab-general', children=[
                    dcc.Tab(label='KPIs', value='tab-general', style=TAB_STYLE, selected_style=TAB_SELECTED_STYLE),
                    dcc.Tab(label='SLA', value='tab-sla', style=TAB_STYLE, selected_style=TAB_SELECTED_STYLE),
                    dcc.Tab(label='Por Analistas [En proceso]', value='tab-analistas', style=TAB_STYLE, selected_style=TAB_SELECTED_STYLE)
                ], style=TABS_STYLES),
            ]),
        ]),
        html.Div(id='tabs-content', style={"margin": 5, "align":"center"})
    ], style={'color': '#F0F3F5', "margin": 0, 'font-family': 'Calibri'})
    return app

app.layout = layout_maker()

@app.callback(
    Output('tabs-content', 'children'),
    [Input('tabs', 'value')]
    )
def render_content(tab):
    if tab == 'tab-general':
        fig_promedio, fig_casos = get_kpi_graphs(type='reclamos')
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
    elif tab == 'tab-sla':
        div = calcula_pendientes.div_creator()
        return div



# if __name__ == '__main__':
#     app.run_server(debug=True, port=8383)

host = get_ip_address()
port = get_dash_port('reclamaciones')
if __name__ == '__main__':
    print('Corriendo Dash Reclamaciones')
    print(f'http://{host}:{port}')
    # app.run_server(debug=False, host=host, port=port)
    serve(app.server, host=host, port=port)
    # serve(app.server, host=host, port=8484)