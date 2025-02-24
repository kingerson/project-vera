"""
Creado el 24/6/2022 a las 4:52 p. m.

@author: jacevedo
"""
"""
Creado el 24/6/2022 a las 9:42 a. m.

@author: jacevedo
"""

from dash import html
import get_pendings

micro_style = {'width': '50%', 'display': 'inline-block'}
big_style = {'font-weight': 'bold', 'fontSize': 80, 'display': 'inline-block'}
good_style = {'font-weight': 'bold', 'color': 'limegreen', 'fontSize': 80, 'display': 'inline-block'}
bad_style = {'font-weight': 'bold', 'color': 'crimson', 'fontSize': 80, 'display': 'inline-block'}
# micro_style = {'display': 'inline-block'}
# big_style = {'font-weight': 'bold', 'fontSize': 80, 'display': 'inline-block'}
# good_style = {'font-weight': 'bold', 'color': 'limegreen', 'fontSize': 80, 'display': 'inline-block'}
# bad_style = {'font-weight': 'bold', 'color': 'crimson', 'fontSize': 80, 'display': 'inline-block'}

def div_creator(titulo, **kwargs):
    diligence_div = html.Div([
        html.H2(titulo, style={'text-align': 'center'}),
        html.Div([
            html.Div([
                html.H3('Pendientes:', style={'display': 'inline-block'}),
                html.H3(f'{kwargs["pendiente"]}', style=big_style)
            ]),
            html.Div([
                html.H3('A tiempo:', style={'display': 'inline-block'}),
                html.H3(f'{kwargs["a_tiempo"]} - {kwargs["a_tiempo_pct"]:.1%}', style=good_style)
            ]),
            html.Div([
                html.H3('Fuera de SLA:', style={'display': 'inline-block'}),
                html.H3(f'{kwargs["fuera_sla"]} - {kwargs["fuera_sla_pct"]:.1%}', style=bad_style)
            ])
        ]),
    ], style={'display': 'inline-block'})
    return diligence_div


def sla_reclamos():
    reclamos = get_pendings.get_pendientes()
    div = div_creator('RECLAMACIONES', **reclamos)
    return div

def sla_info():
    reclamos = get_pendings.get_pendientes(tipo='info')
    div = div_creator('INFORMACIÓN FINANCIERA', **reclamos)
    return div
