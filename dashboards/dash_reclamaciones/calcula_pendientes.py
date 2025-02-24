"""
Creado el 7/12/2023 a las 12:18 p. m.

@author: jacevedo
"""

import reclamos_reading
from datetime import datetime
from sql_tools import query_reader
from prousuario_tools import odata_query_creator, get_odata, get_odata_parameters
from reclamos_reading import clean_data
from general_tools import convert_time
from dash.dash_table import DataTable
from dash import dcc
import pandas as pd
import base64
import io

params = get_odata_parameters()
header = params['headers']
reclamos = params['reclamos']
query_cols = reclamos['query_cols']
tabla = reclamos['tabla']
format_label = params['format_label']
nuevos_nombres = reclamos['nuevos_nombres_columnas']

def create_query():
    filters = (
            "new_codigo ne null"
            " and Microsoft.Dynamics.CRM.OnOrAfter"
            f"(PropertyName='createdon',PropertyValue='2023-01-01')"
        )
    cols = ['new_codigo', 'statuscode', 'new_fechadeverificaciondelcaso', 'new_etapaactiva']
    query = odata_query_creator('new_reclamacins', columns=cols, filters=filters)
    return query

def get_data(header):
    query = create_query()
    df = get_odata(query, header)
    df = df.drop('new_reclamacinid', axis=1)
    claims = clean_data(df, format_label, nuevos_nombres)
    claims.activa = claims.activa.map({'Active': True, "Inactive": False})
    claims['fecha_verificacion'] = convert_time(claims['fecha_verificacion'])
    return claims

def get_results():
    query = "select codigo from USRPROUSUARIO.RESULTADOS_RECLAMOS where FECHA_CIERRE > date '2023-01-01'"
    cierres = query_reader(query, mode='all')
    return cierres


def calculo_pendientes():
    claims = get_data(header)
    cierres = get_results()
    filtro_etapa_postfirma = claims.new_etapaactiva.isin(['Notificación y Entrega', 'EIF Notificada', 'Cumplimiento', 'Entregado al Usuario'])
    filtro_firma = ~claims.codigo.isin(cierres.codigo)
    abiertas = claims[filtro_firma & claims.activa & ~filtro_etapa_postfirma].copy()
    abiertas['dias'] = (datetime.today() - abiertas.fecha_verificacion).dt.days
    filtro_60 = abiertas.dias >= 60
    en_riesgo = abiertas.dias.between(50,60)
    abiertas['status'] = 'Pendientes'
    abiertas.loc[~filtro_60, 'status'] = 'A tiempo'
    abiertas.loc[en_riesgo, 'status'] = 'En riesgo'
    abiertas.loc[filtro_60, 'status'] = 'Fuera de SLA'
    pendientes = {
        'Pendientes': len(abiertas),
        'A tiempo': len(abiertas[~filtro_60]),
        'En riesgo': len(abiertas[en_riesgo]),
        'Fuera de SLA': len(abiertas[filtro_60])
    }
    return pendientes, abiertas

from dash import html

micro_style = {'width': '50%', 'display': 'inline-block'}
big_style = {'font-weight': 'bold', 'fontSize': 80, 'display': 'inline-block'}
good_style = {'font-weight': 'bold', 'color': 'limegreen', 'fontSize': 80, 'display': 'inline-block'}
medium_style = {'font-weight': 'bold', 'color': 'orange', 'fontSize': 80, 'display': 'inline-block'}
bad_style = {'font-weight': 'bold', 'color': 'crimson', 'fontSize': 80, 'display': 'inline-block'}

def div_creator():
    pendientes, abiertas = calculo_pendientes()
    abiertas = abiertas.drop('activa', axis=1)
    abiertas['fecha_verificacion'] = abiertas['fecha_verificacion'].dt.strftime('%Y-%m-%d')
    abiertas.sort_values('dias', ascending=False, inplace=True)

    # Provide a downloadable link to the data
    csv_string = abiertas.to_csv(index=False, encoding='utf-8', sep='\t')
    csv_b64 = base64.b64encode(csv_string.encode()).decode()
    data_url = f"data:text/csv;base64,{csv_b64}"

    download_data = dict(
        content=abiertas.to_csv(index=False),
        filename="late_cases_data.csv",
        mime_type="text/csv"
    )

    titles = list(pendientes.keys())
    values = list(pendientes.values())
    diligence_div = html.Div([
        html.H2('Reclamaciones Pendientes', style={'text-align': 'center'}),
        html.Div([
                html.Div([
                        html.H3(f'{title}:', style={'display': 'inline-block'}),
                        html.H3(f'  {value}' if i == 0 else f'  {value} - {value / values[0]:.1%}', style=style)
                    ]) for i, (title, value, style) in enumerate(zip(titles, values, [big_style, good_style, medium_style, bad_style]))
                ], style={'width':'45%', 'display':'inline-block','vertical-align': 'top', 'margin':0, 'padding':0}),
            # html.Div([], style=dict(width='5%', display='inline-block', margin=0, padding=0)),
            html.Div([
                DataTable(id='table',
                          columns=[{'name': col, 'id': col} for col in abiertas.columns],
                          data=abiertas.to_dict('records'),
                          sort_action='native',
                          style_table={'color': 'darkblue'},
                          page_size=20)
            ], style={'width':'45%', 'display':'inline-block','vertical-align': 'top', 'margin':0, 'padding':0})

                # ]),
            # ], style=dict(width='50%', display='inline-block', margin=0, padding=0)),
    ])
    # ], style=dict(display='inline-block', border = '2px solid black'))


    #     html.Div([
    #     html.H2('Reclamaciones Pendientes', style={'text-align': 'center'}),
    #     html.Div([
    #         # Left div
    #         html.Div([
    #             html.Div([
    #                 html.Div([
    #                     html.H3(f'{title}:', style={'display': 'inline-block'}),
    #                     html.H3(f'  {value}' if i == 0 else f'  {value} - {value / values[0]:.1%}', style=style)
    #                 ])
    #                 for i, (title, value, style) in enumerate(zip(titles, values, [big_style, good_style, medium_style, bad_style]))
    #             ])
    #         ], style=dict(width='50%', display='inline-block')),
    #         # Right div
    #         html.Div([
    #             DataTable(id='table',
    #                       columns=[{'name': col, 'id': col} for col in abiertas.columns],
    #                       data=abiertas.iloc[:20].to_dict('records'),
    #                       sort_action='native',
    #                       style_table={'color': 'darkblue'},
    #                       page_size=20)
    #         ], style=dict(width='50%', display='inline-block'))
    #     ])
    # ])


    return diligence_div