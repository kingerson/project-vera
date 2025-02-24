"""
Creado el 14/7/2022 a las 3:32 p. m.

@author: jacevedo
"""
import sql_tools
import pandas as pd
import plotly.express as px
from plotly.offline import plot
import locale
locale.setlocale(locale.LC_ALL,'es_ES.UTF-8')


#%%

query = "select * from RESULTADOS_RECLAMOS"
df = sql_tools.query_reader(query, mode='all')

#%%

filtro_fecha = df.fecha_cierre > '2020-12-31'
filtro_mes = df.fecha_cierre.dt.month.apply(lambda x: x in list(range(1,7)))
df = df[filtro_fecha & filtro_mes]

#%%

data = df.groupby([df.fecha_cierre.dt.to_period('M').dt.start_time, 'favorabilidad']).size().rename('cantidad').reset_index()

data = data.pivot(index='fecha_cierre', columns='favorabilidad', values='cantidad')
data = data.drop('O', axis=1)
data['total'] = data.sum(axis=1)

data['favorabilidad'] = data['F'] / data['total']
# round(data.favorabilidad * 100, 1)
#%%

data = data.reset_index()
# data.columns = ['fecha', 'cantidad']
data['year'] = data.fecha_cierre.dt.year.astype(str)
data['mes'] = data.fecha_cierre.dt.strftime('%B')
data
#%%

# fig = px.bar(data, x='fecha', y='cantidad', color='year', barmode='group')
fig = px.bar(data,x='mes', y='favorabilidad', color='year', barmode='group',
             template='presentation', color_discrete_sequence=px.colors.sequential.Greens[2::3],text_auto=True)
fig.update_layout(
    yaxis_showgrid=False
)
fig.update_traces(
    texttemplate =('%{y:.0%}'))
plot(fig)

