"""
Creado el 2/9/2024 a las 1:20 PM

@author: jacevedo
"""

import dash
from dash import dcc, html
import plotly.graph_objs as go
import pandas as pd
from demograficos.demographics_app import get_cantidad_usuarios, get_dos_semanas, get_ocho_semanas, get_gender_groups
from prousuario_tools import get_sb_colors
from reporte_app_graphers import graph_users_datebars
colores = get_sb_colors()

# Inicializa el app
app = dash.Dash(__name__)

# Example DataFrames
df_semanas = get_dos_semanas()
df_ocho_semanas = get_ocho_semanas()
gender_data = get_gender_groups()

app.layout = html.Div([
    # Header numbers
    html.Div([
        html.Div([
            html.H3(f'{get_cantidad_usuarios():,}'),
            html.P('Total de Usuarios')
        ]),
        html.Div([
            html.H3('94.76 mil'),
            html.P('Usuarios I/A')
        ]),
        html.Div([
            html.H3('100.03 mil.'),
            html.P('Monto I/A')
        ]),
        html.Div([
            html.H3('8'),
            html.P('Posición IOS')
        ]),
        html.Div([
            html.H3('8'),
            html.P('Posición Android')
        ]),
        html.Div([
            html.H3('99%'),
            html.P('% Solicitudes listas')
        ]),
        html.Div([
            html.H3('10,624'),
            html.P('Usuarios L. Exc.')
        ]),
        html.Div([
            html.H3('343,206'),
            html.P('Solicitudes L. Exc.')
        ]),
    ], style={'display': 'flex', 'justify-content': 'space-around'}),

    # Line and Bar Graph for 2 weeks data
    dcc.Graph(
        id='two-weeks-graph',
        figure=graph_users_datebars(get_dos_semanas())
    ),

    # Line and Bar Graph for 8 weeks data
    dcc.Graph(
        id='eight-weeks-graph',
        figure={
            'data': [
                go.Bar(
                    x=df_ocho_semanas['Semana'],
                    y=df_ocho_semanas['Registrados'],
                    name='Registrados',
                    marker_color=colores['sb gray']
                ),
                go.Bar(
                    x=df_ocho_semanas['Semana'],
                    y=df_ocho_semanas['Verificados'],
                    name='Verificados',
                    marker_color=colores['blue sb dark']
                ),
                go.Scatter(
                    x=df_ocho_semanas['Semana'],
                    y=df_ocho_semanas['Conversion'],
                    name='% Conversión',
                    yaxis='y2',
                    line=dict(color=colores['turquesa pro'])
                )
            ],
            'layout': go.Layout(
                title='Comportamiento 8 semanas (semana por semana)',
                yaxis=dict(title='Usuarios'),
                yaxis2=dict(title='% Conversión', overlaying='y', side='right'),
                barmode='group'
            )
        }
    ),

    # Pie charts
    html.Div([
        dcc.Graph(
            id='gender-pie-chart',
            figure=go.Figure(
                data=[go.Pie(labels=gender_data.index, values=gender_data['cantidad'])],
                layout=go.Layout(title='Usuarios por Sexo')
            )
        ),
        dcc.Graph(
            id='age-pie-chart',
            figure=go.Figure(
                # data=[go.Pie(labels=age_data['Age Range'], values=age_data['Count'])],
                layout=go.Layout(title='Edad de Usuarios')
            )
        )
    ], style={'display': 'flex', 'justify-content': 'space-around'}),
])

if __name__ == '__main__':
    app.run_server(debug=True)