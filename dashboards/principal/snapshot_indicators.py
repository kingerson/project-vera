"""
Creado el 24/6/2022 a las 9:42 a. m.

@author: jacevedo
"""

from dash import html

micro_style = {'width': '50%', 'display': 'inline-block'}
big_style = {'font-weight': 'bold', 'fontSize': 80, 'width': '50%', 'display': 'inline-block'}


def calculate_diligencia(entradas, salidas):
    diligencia = salidas / entradas - 1
    if diligencia > 0.005:
        style = {'font-weight': 'bold', 'color': 'limegreen', 'fontSize': 80}
        diligencia = f'▲ {diligencia:.1%}'
    elif 0.005 > diligencia > -0.005:
        style = {'font-weight': 'bold', 'color': 'slateblue', 'fontSize': 80}
        diligencia = f'= {diligencia:.1%}'
    else:
        style = {'font-weight': 'bold', 'color': 'crimson', 'fontSize': 80}
        diligencia = f'▼ {abs(diligencia):.1%}'
    return diligencia, style


def indicator_calculation(entradas, salidas):
    entradas = len(entradas.fecha_creacion.dropna())
    salidas = len(salidas.fecha_cierre.dropna())
    diligencia, estilo = calculate_diligencia(entradas, salidas)
    return entradas, salidas, diligencia, estilo


def div_creator(titulo, entradas, cierres, diligencia, estilo):
    diligence_div = html.Div([
        html.H2(titulo, style={'text-align': 'center'}),
        html.Div([
            html.H3('Recibidas:', style=micro_style),
            html.H3(f'{entradas}', style=big_style),
            html.H3('Completadas:', style=micro_style),
            html.H3(f'{cierres}', style=big_style),
        ], style=micro_style),
        html.Div([
            html.H3('Indicador de diligencia:'),
            html.H3(diligencia, style=estilo),
        ], style=micro_style),
    ], style=micro_style)
    return diligence_div


def snapshot_maker(titulo, entradas, salidas):
    entradas, salidas, diligencia, estilo = indicator_calculation(entradas, salidas)
    div = div_creator(titulo, entradas, salidas, diligencia, estilo)
    return div
