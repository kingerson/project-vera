"""
Creado el 24/6/2022 a las 4:52 p. m.

@author: jacevedo
"""
"""
Creado el 24/6/2022 a las 9:42 a. m.

@author: jacevedo
"""

from dash import html

micro_style = {'width': '50%', 'display': 'inline-block'}
big_style = {'font-weight': 'bold', 'fontSize': 80, 'width': '50%', 'display': 'inline-block'}


def calculate_diligencia(entradas, salidas):
    diligencia = salidas / entradas - 1
    if diligencia > 0:
        style = {'font-weight': 'bold', 'color': 'limegreen', 'fontSize': 80}
        diligencia = f'▲ {diligencia:.1%}'
    elif 0.005 > diligencia > 0:
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

def calcula_favorables(data):
    favorables = data.value_counts(normalize=True)['F']

def div_creator(titulo, entradas, cierres, dias_promedio, favs, estilo):
    diligence_div = html.Div([
        html.H2(titulo, style={'text-align': 'center'}),
        html.Div([
            html.H3('Recibidas:', style=micro_style),
            html.H3(f'{entradas:}', style=big_style),
            html.H3('Completadas:', style=micro_style),
            html.H3(f'{cierres:}', style=big_style),
            html.H3('Promedio de días:', style=micro_style),
            html.H3(f'{dias_promedio:.1f}', style=big_style),
            html.H3('Favorabilidad:', style=micro_style),
            html.H3(f'{favs:.1%}', style=big_style),
        ], style=micro_style),
    ], style=micro_style)
    return diligence_div


def div_info(titulo, entradas, cierres, dias_promedio):
    diligence_div = html.Div([
        html.H2(titulo, style={'text-align': 'center'}),
        html.Div([
            html.H3('Recibidas:', style=micro_style),
            html.H3(f'{entradas:}', style=big_style),
            html.H3('Completadas:', style=micro_style),
            html.H3(f'{cierres:}', style=big_style),
            html.H3('Promedio de días:', style=micro_style),
            html.H3(f'{dias_promedio:.1f}', style=big_style),
            html.H3('‎', style=micro_style),
            html.H3('‎', style=big_style)
        ], style=micro_style),
    ], style=micro_style)
    return diligence_div

def stats_reclamos(titulo, data):
    # print(data.head())
    entradas = data[['fecha_creacion']]
    salidas = data[['fecha_cierre']]
    favs = data[data.favorabilidad.fillna('').str.contains('F|D')].favorabilidad
    favs = favs.value_counts(normalize=True)['F']
    cierres = data.dropna(subset='fecha_cierre')
    dias_promedio = (cierres.fecha_cierre - cierres.fecha_inicio).dt.days.mean()
    entradas, salidas, diligencia, estilo = indicator_calculation(entradas, salidas)
    div = div_creator(titulo, entradas, salidas, dias_promedio, favs, estilo)
    return div


def stats_info(titulo, data):
    entradas = len(data.fecha_creacion.dropna())
    salidas = len(data.fecha_cierre.dropna())
    cierres = data.dropna(subset='fecha_cierre')
    dias_promedio = (cierres.fecha_cierre - cierres.fecha_inicio).dt.days.mean()
    div = div_info(titulo, entradas, salidas, dias_promedio)
    return div
