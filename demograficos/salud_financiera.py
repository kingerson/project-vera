#%%
import pandas as pd
import plotly.express as px
from plotly.offline import plot
import locale
from sql_tools import query_reader
from prousuario_tools import get_sb_colors
import numpy as np

#%%

query = """
select 
*
from IDV2 a
left join (
    select cedula, sum(monto_cuota)/count(fecha) cuota_mensual, count(distinct producto) cantidad_productos
    from (
    select IDENTIFICACIONDEUDOR cedula
    ,MONTOCUOTA monto_cuota
    ,d.ano||d.mes fecha
    , d.entidad || d.codigocredito producto
    from IDV2 c
    left join FINCOMUNES.rcc_rc01 d on d.IDENTIFICACIONDEUDOR = c.CEDULA
    where ano = 2024
    )
    group by cedula
) b on a.cedula = b.cedula
left join (
    select cedula, sum(consumos)/count(fecha) consumo_mensual, count(distinct producto) cantidad_productos
    from (
    select IDENTIFICACIONDEUDOR cedula
    ,CONSUMOSMES consumos
    ,b.ano||b.mes fecha
    ,b.entidad || b.codigocredito producto
    from IDV2 a
    left join FINCOMUNES.rcc_rc03 b on b.IDENTIFICACIONDEUDOR = a.CEDULA
    where ano = 2024
    )
    group by cedula
) c on a.cedula = c.cedula

"""
deuda_mensual = query_reader(query, mode='all')
deuda_mensual

#%%

cols = ['fecha_creacion', 'nombre', 'email', 'genero', 'cedula', 'fecha_nac',
       'nacionalidad', 'estado_civil', 'cantidad_logins', 'nivel_educativo',
       'fuente_ingresos', 'ingresos', 'otras_deudas', 
       'cuota_mensual', 'consumo_mensual']

df = df[cols]

#%%

df.cuota_mensual = df.cuota_mensual.astype(float)
df.consumo_mensual = df.consumo_mensual.astype(float)
df.dtypes

#%%

df['deuda_mensual_promedio'] = df.consumo_mensual.fillna(0) + df.cuota_mensual.fillna(0)
df.deuda_mensual_promedio = df.deuda_mensual_promedio.astype(float).round(2)
df.deuda_mensual_promedio.min()
filtro_ingresos = df.ingresos.between(5000,2000000)
con_ingresos = df[filtro_ingresos].copy()
con_ingresos['nivel_deuda'] = con_ingresos.deuda_mensual_promedio / (con_ingresos.ingresos+1)
con_ingresos.nivel_deuda = con_ingresos.nivel_deuda.round(4)
con_ingresos.nivel_deuda.dropna().describe(percentiles=[0.1,0.25,0.5,0.75,0.9,0.95,0.99,0.999]).apply(lambda x: round(x,2))
con_ingresos.nivel_deuda.clip(upper=10).value_counts(bins=range(0,101,10)).sort_index()

con_ingresos[con_ingresos.nivel_deuda > 5].T
con_ingresos[con_ingresos.ingresos > 1000000].T

# financiado y cuanto genero de intereses
# utilizacion de limite de tarjetas

#%%
con_ingresos['ingresos_clipped'] = con_ingresos.ingresos.clip(upper=100000)
con_ingresos['deuda_clipped'] = con_ingresos.deuda_mensual_promedio.clip(upper=100000)
fig = px.scatter(con_ingresos, x='ingresos_clipped', y='deuda_clipped'
                 , color='nivel_deuda', color_continuous_midpoint=0.5,color_continuous_scale='RdYlGn_r'
                 , template='plotly_dark', range_color=[0.25,1]
                 , custom_data=['nivel_deuda', 'ingresos', 'deuda_mensual_promedio']
                 )
fig.update_traces(
       hovertemplate="""<b>Nivel deuda: %{customdata[0]:,.2f}</b><br>Ingresos: $%{customdata[1]:,.2f}<br>Deuda mensual<br>promedio: $%{customdata[2]:,.2f}
       """,
)
ingresos_mean = con_ingresos.ingresos.median()
fig.add_vline(ingresos_mean, annotation_text=f"Media de ingresos: ${ingresos_mean:,.2f}")
deuda_mean = con_ingresos.deuda_mensual_promedio.median()
fig.add_hline(deuda_mean, annotation_text=f"Media de deuda mensual: ${deuda_mean:,.2f}")

plot(fig)
#%%

con_ingresos.nivel_deuda.value_counts()