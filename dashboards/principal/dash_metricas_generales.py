"""
Creado el 24/5/2022 a las 6:47 p. m.

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
import locale

from dashboards.principal import data_readers, model_implementation
from dashboards.principal import etapas_reader
from dashboards.principal import sla_stats
from dashboards.principal.banks_rank_grapher import creates_banks_ranks
from dashboards.principal.entradas_salidas_lineas import creates_dcc
from dashboards.principal.etapas_grapher import plot_distribucion_etapas
from dashboards.principal.freq_adjuster import adjust_freq
from dashboards.principal.general_stats import stats_reclamos, stats_info
from dashboards.principal.snapshot_indicators import snapshot_maker
from prousuario_tools import get_sb_colors

locale.setlocale(locale.LC_ALL, 'es_DO.UTF-8')

# Crea el app principal
server = Flask(__name__)
colors = get_sb_colors()

# Crea el app principal
EXTERNAL_STYLESHEETS = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
APP = dash.Dash(__name__,
                external_stylesheets=EXTERNAL_STYLESHEETS,
                include_assets_files=True,
                meta_tags=[{'name': 'viewport', 'content': 'width=device-width'}],
                server=server
                )

APP.title = 'Metricas ProUsuario'
server = APP.server

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


def date_picker(start_date, end_date):
    dcc.DatePickerRange(
        id='date-picker-range',
        is_RTL=False,
        end_date=end_date,
        start_date=start_date,
        style=dict(display='inline-block')
    )


def convert_data(df):
    df = pd.DataFrame().from_dict(df)
    for c in df.columns[df.columns.str.contains('fecha')]:
        df[c] = pd.to_datetime(df[c])
    return df

#%%


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
                        'Métricas ProUsuario',
                        id='sub-titulo',
                        style={'padding-left': '10px', 'display': 'inline-block', 'height': '80px', 'text-align': 'top'}
                    )
                    ], style={'display': 'inline-block', 'height': '60px', 'padding': "20px", "float": "left"})
            ], style=dict(width='45%', display='inline-block')),
            html.Div([
                html.Div([
                    html.H6(
                        'Periodo a visualizar   ',
                        id='date-picker-label'
                    )
                ]),
                html.Div([
                    dcc.DatePickerRange(
                        id='date-picker-range',
                        is_RTL=False,
                        end_date=date.today().isoformat(),
                        start_date=(date.today() - timedelta(weeks=2)).isoformat(),

                    )
                ]),
            ],  style={'display': 'inline-block', 'padding-bottom': '20px', 'padding-top': '0px'}),
            html.Div([
                html.Div([
                    dcc.RadioItems(
                        id='freq-picker',
                        options=[
                            {'label': 'En días', 'value': 'D'},
                            {'label': 'En semanas', 'value': 'W-MON'},
                            {'label': 'En meses', 'value': 'M'},
                           # {'label': 'En años', 'value': 'Y'},
                        ], value='D'),
                    # dcc.RadioItems(
                    #     id='period-picker',
                    #     options=[
                    #         {'title': 'Período específico:' },
                    #         {'label': 'Ultimos 7 días', 'value': 'D'},
                    #         {'label': 'Esta semana', 'value': 'D'},
                    #         {'label': 'Semana pasada', 'value': 'D'},
                    #         {'label': 'Ultimos 30 días', 'value': 'D'},
                    #         {'label': 'Este mes', 'value': 'W-MON'},
                    #         {'label': 'Mes pasado', 'value': 'M'},
                    #         {'label': 'Trimestre', 'value': 'M'},
                    #         {'label': 'Semestre', 'value': 'M'},
                    #
                    #
                    #
                    #
                    #         # {'label': 'En años', 'value': 'Y'},
                    #     ], value='W-MON', style=dict(display='inline-block'))
                ])
            ], style={
                'display': 'inline-block', 'padding-top': '0px',
                'padding-bottom': '20px', 'padding-left': '30px'}),
            html.Div([
                dcc.Tabs(id="tabs", value='tab-general', children=[
                    dcc.Tab(
                        label='Generales',
                        value='tab-general',
                        style=TAB_STYLE,
                        selected_style=TAB_SELECTED_STYLE
                    ),
                    dcc.Tab(
                        label='Flujo Procesos',
                        value='tab-flujo',
                        style=TAB_STYLE,
                        selected_style=TAB_SELECTED_STYLE
                    ),
                    # dcc.Tab(
                    #     label='Reclamaciones',
                    #     value='tab-reclamos',
                    #     style=TAB_STYLE,
                    #     selected_style=TAB_SELECTED_STYLE
                    # ),
                    dcc.Tab(
                        label='Rankings Reclamaciones',
                        value='tab-rankings',
                        style=TAB_STYLE,
                        selected_style=TAB_SELECTED_STYLE
                    ),
                    dcc.Tab(
                        label='Status SLA',
                        value='tab-sla',
                        style=TAB_STYLE,
                        selected_style=TAB_SELECTED_STYLE
                    ),
                    dcc.Tab(
                        label='Status Etapas',
                        value='tab-etapas',
                        style=TAB_STYLE,
                        selected_style=TAB_SELECTED_STYLE
                    ),
                    dcc.Tab(
                        label='COPERNICO',
                        value='tab-copernico',
                        style=TAB_STYLE,
                        selected_style=TAB_SELECTED_STYLE
                    ),
                    # dcc.Tab(
                    #     label='Información Financiera',
                    #     value='tab-info',
                    #     style=TAB_STYLE,
                    #     selected_style=TAB_SELECTED_STYLE
                    # ),
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


APP.layout = layout_maker()


@APP.callback(
    [Output('date-picker-range', 'start_date'),
     Output('date-picker-range', 'end_date')],
    Input('interval-component', 'n_intervals')
)
def update_date(n):
    end_date = date.today().isoformat()
    start_date = (date.today() - pd.offsets.MonthBegin()).date().isoformat()
    return start_date, end_date


@APP.callback(
    Output('reclamos-data', 'data'),
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def read(start_date, end_date):
    result = data_readers.main('reclamos', start_date, end_date)
    return result


@APP.callback(
    Output('info-data', 'data'),
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def read(start_date, end_date):
    result = data_readers.main('info', start_date, end_date)
    return result


@APP.callback(
    Output('freq-picker', 'value'),
    [Input('reclamos-data', 'data'),
     Input('freq-picker', 'value'),
     Input('tabs', 'value')]
)
def adjust(data, freq, tab):
    return adjust_freq(data, freq, tab)


@APP.callback(
    Output('tabs-content', 'children'),
    [Input('tabs', 'value'),
     Input('reclamos-data', 'data'),
     Input('info-data', 'data'),
     Input('freq-picker', 'value')]
    )
def render_content(tab, claims, info, freq):
    claims = convert_data(claims)
    info = convert_data(info)
    if tab == 'tab-general':
        stats = html.Div([
            html.H2((date.today() - pd.offsets.MonthBegin()).strftime('%B %Y').upper(), style={'text-align':'center', 'display':'inline-block'}),
            html.Div([
            stats_reclamos('RECLAMACIONES', claims),
            stats_info('INFORMACIÓN FINANCIERA', info)
            ])
        ])
        return stats

    if tab == 'tab-flujo':
        snapshot = html.Div([
            html.Div([
                snapshot_maker('RECLAMACIONES', claims[['fecha_creacion']], claims[['fecha_cierre']]),
                snapshot_maker('INFORMACIÓN FINANCIERA', info[['fecha_creacion']], info[['fecha_cierre']])
            ]),
            html.Div([
                creates_dcc(claims[['fecha_creacion']], claims[['fecha_cierre']], freq=freq),
                creates_dcc(info[['fecha_creacion']], info[['fecha_cierre']], freq=freq)
            ])
        ])
        return snapshot

    elif tab == 'tab-rankings':
        grupero_semanal = pd.Grouper(key='fecha_creacion', freq=freq)
        eif_per_freq = claims.groupby([grupero_semanal, 'eif']).size()
        entries_per_bank = creates_banks_ranks(eif_per_freq, freq=freq)
        cat_per_freq = claims.groupby([grupero_semanal, 'categoria']).size()
        entries_per_cat = creates_banks_ranks(cat_per_freq, color_col='categoria', freq=freq)
        div = html.Div([
            html.Div([
                dcc.Graph(
                    id='bank-entries',
                    figure=entries_per_bank
                ),
            ], style=dict(width='50%', display='inline-block')),
            html.Div([
                dcc.Graph(
                    id='category-entries',
                    figure=entries_per_cat
                ),
            ], style=dict(width='50%', display='inline-block'))
            ])
        return div

    elif tab == 'tab-sla':
        info_div = sla_stats.sla_info()
        reclamos_div = sla_stats.sla_reclamos()
        div = html.Div([
            html.H1(f'Status SLA al {date.today().strftime("%d de %B de %Y")}'),
            html.Div([
                reclamos_div,
                info_div
            ])
        ])
        return div
    elif tab == 'tab-etapas':
        cantidad_dias = 365
        titulo = 'por etapas pendientes'
        etapas_info_pendientes = etapas_reader.get_etapas(dias=cantidad_dias)
        fig_pendientes = plot_distribucion_etapas(etapas_info_pendientes, titulo=titulo, color='#0cccc6')
        cantidad_dias = 14
        titulo = 'por etapas cerradas en ultimos 14 días'
        etapas_info_cerradas = etapas_reader.get_etapas(tipo='cierres', dias=cantidad_dias)
        fig_cerradas = plot_distribucion_etapas(etapas_info_cerradas, titulo=titulo, color='#f77245')
        div = html.Div([
            html.Div([
                dcc.Graph(
                    id='info-pendientes',
                    figure=fig_pendientes
                ),
            ], style=dict(width='50%', display='inline-block')),
            html.Div([
                dcc.Graph(
                    id='info-cerradas',
                    figure=fig_cerradas
                ),
            ], style=dict(width='50%', display='inline-block'))
        ])
        return div
    elif tab == 'tab-copernico':
        yesterday = date.today() - timedelta(1)
        result = model_implementation.main()
        print(result)
        df = result[['codigo', 'eif', 'duracion_estimada']]
        df.columns = df.columns.str.replace('_', ' ').str.title()
        # tabla = dash_table.DataTable(
        #     df.to_dict('records'),
        #     [{"name": i.replace('_', ' ').title(), "id": i} for i in df.columns]
        # )

        div = html.Div([
            html.H1(f'Tiempo de duración estimado'),
            html.H3(f'Reclamaciones de {yesterday.strftime("%d de %B de %Y")}'),
            generate_table(df)
            # html.Div([
            #     dcc.Graph(
            #         id='predictions',
            #         # figure=fig
            #     ), generate_table(df)
            # ], style=dict(width='50%', display='inline-block')),
        ])
        return div


def generate_table(dataframe, max_rows=10):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ])
#%%
#
#
# if __name__ == "__main__":
#     APP.run_server(debug=False)


host = socket.gethostbyname(socket.gethostname())
port = 9393
if __name__ == '__main__':
    APP.run_server(debug=False, host=host)
