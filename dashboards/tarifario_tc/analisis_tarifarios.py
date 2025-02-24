# Created on 18/9/2024 by jacevedo

import pandas as pd
import plotly.express as px
from plotly.offline import plot
import locale
from sql_tools import query_reader

#%%


def create_figure(data, title=None):
    fig = px.line(data)
    fig.update_layout(
        title=title,
        xaxis_title=None
    )
    plot(fig)

#%%

query = """
select
    a.ano||lpad(a.mes, 2, '0') fecha
    , nombre_corto eif
from fincomunes.tc1b a
left join fincomunes.REGISTRO_ENTIDADES c on c.CODIGOI = a.entidad
where a.ano||lpad(a.mes, 2, '0') > '202001'
order by fecha, NOMBRE_CORTO
"""

df = query_reader(query, mode='all')
#%%
por_mes = df.groupby(['fecha', 'eif']).size().rename('cantidad').reset_index()
# por_mes = por_mes.sort_values(['cantidad'], ascending=True)
eif_order = por_mes.groupby('eif')['cantidad'].mean().sort_values(ascending=False).index

#%%

fig = px.line(por_mes, x='fecha', y='cantidad', color='eif'
              , category_orders={'eif': eif_order}
              )
fig.update_layout(
    title=None
    , xaxis_title=None
)
fig
# plot(fig)

#%%

query = """
select
    a.ano||lpad(a.mes, 2, '0') fecha
    , nombre_corto eif
    -- , e.DESCRIPCIO producto
from fincomunes.tc1b a
left join fincomunes.REGISTRO_ENTIDADES c on c.CODIGOI = a.entidad
left join produservi e on e.CODIGO = a.tipoprod
where a.ano||lpad(a.mes, 2, '0') > '202001'
and e.DESCRIPCIO like '%AHORRO%'
order by fecha, NOMBRE_CORTO
"""

df = query_reader(query, mode='all')
#%%
por_mes = df.groupby(['fecha', 'eif']).size().rename('cantidad').reset_index()
# por_mes = por_mes.sort_values(['cantidad'], ascending=True)
eif_order = por_mes.groupby('eif')['cantidad'].mean().sort_values(ascending=False).index

#%%

fig = px.line(por_mes, x='fecha', y='cantidad', color='eif'
              , category_orders={'eif': eif_order}
              )
fig.update_layout(
    title=None
    , xaxis_title=None
)
fig

#%%

# CANTIDAD DE CARGOS DISTINTOS POR MES POR ENTIDAD

query = """
select fecha, NOMBRE_CORTO eif, cantidad from (
select
    a.ano||lpad(a.mes, 2, '0') fecha
    , a.entidad eif
    , COUNT( DISTINCT g.CODIGOCONC) cantidad
    -- , e.DESCRIPCIO producto
from fincomunes.tc1b a
--left join produservi e on e.CODIGO = a.tipoprod
LEFT JOIN fincomunes.TC02 g ON g.codigo||g.entidad = a.codigo||a.entidad
where a.ano||lpad(a.mes, 2, '0') > '202001'
-- and e.DESCRIPCIO like '%AHORRO%'
and TIPOPAGO = 'TC'
group by a.ano||lpad(a.mes, 2, '0'), a.entidad
) a
left join fincomunes.REGISTRO_ENTIDADES c on c.CODIGOI = a.eif
order by fecha, eif
"""

df = query_reader(query, mode='all')
#%%
por_mes = df.groupby(['fecha', 'eif'])['cantidad'].sum().rename('cantidad').reset_index()
# por_mes = por_mes.sort_values(['cantidad'], ascending=True)
eif_order = por_mes.groupby('eif')['cantidad'].mean().sort_values(ascending=False).index

#%%

fig = px.line(por_mes, x='fecha', y='cantidad', color='eif'
              , category_orders={'eif': eif_order}
              , template='plotly_dark'
              )
fig.update_layout(
    title=None
    , xaxis_title=None
    , yaxis_tickvals=list(range(0, 27))
)
fig