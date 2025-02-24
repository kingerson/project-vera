"""
Creado el 9/2/2024 a las 1:31 p. m.

@author: jacevedo
"""
import pandas as pd
import plotly.express as px
from plotly.offline import plot
from prousuario_tools import get_sb_colors
#%%
colores = get_sb_colors()


#%% COLORES ORDENADOS POR HEX VALUE
barras = len(colores)*[10]
colormap = colores.keys()
lista_colores = list(colores.values())
lista_colores = list(set(colores.values()))
lista_colores.sort()

ordered_colors = {}
for c in lista_colores:
    for v in colores.items():
        if v[1] == c:
            ordered_colors[v[0]] = v[1]

fig = px.bar(
    barras,
    x=colormap,
    color=ordered_colors.keys(),
    color_discrete_sequence=lista_colores,
    template='presentation',
    orientation='v',
    width=1200,
    height=600
)
fig.update_layout(
    font_family='Calibri'
    , xaxis_visible=True
    , xaxis_tickangle=-30
    , xaxis_title=None
    , yaxis_visible=False
)

plot(fig)

#%% COLORES ORDENADOS POR GRUPO

barras = len(colores)*[10]
colormap = colores.keys()
lista_colores = list(colores.values())


fig = px.bar(
    barras,
    x=colormap,
    color=colormap,
    color_discrete_sequence=lista_colores,
    template='presentation',
    orientation='v',
    width=1200,
    height=600
)
fig.update_layout(
    font_family='Calibri'
    , xaxis_visible=True
    , xaxis_tickangle=-30
    , xaxis_title=None
    , yaxis_visible=False
)

plot(fig)


#%%

import infofinanciera_reading
from sql_tools import query_reader
from general_tools import excel_formatter

query = """select * from USRPROUSUARIO.RESULTADOS_INFO where FECHA_CIERRE between date '2023-06-01' and date '2024-01-31'"""
results = query_reader(query, mode='all')

info = infofinanciera_reading.main('2021-01-01', '2024-01-31')

mezcla = pd.merge(results, info, on='codigo', how='left')

mezcla['dias'] = (mezcla.fecha_cierre - mezcla.fecha_inicio).dt.days
filtro_tarde = mezcla.dias > 60
with pd.ExcelWriter('casos_tarde_IF_2023.xlsx', engine='xlsxwriter') as writer:
    excel_formatter(writer, mezcla[filtro_tarde], 'Casos Tardíos')
