"""
Creado el 31/5/2022 a las 12:01 p. m.

@author: jacevedo
"""
import sql_tools
import pandas as pd
import reclamos_reading
from datetime import timedelta
import locale
locale.setlocale(locale.LC_ALL, 'es_DO.UTF-8')

#%%
end_date = pd.Timestamp('today').to_period('M').start_time
start_date = end_date - pd.offsets.MonthBegin(18)
start_date

#%%
claims = reclamos_reading.main('2020-01-01')

#%%
query = "select * from RESULTADOS_RECLAMOS"
firmas = sql_tools.query_reader(query, mode='all')
firmas



#%%



#%%


a = claims[['codigo', 'fecha_inicio']]

['codigo', 'fecha_inicio', 'fecha_cierre', 'tipo_respuesta',
       'favorabilidad', 'monto_instruido_dop', 'monto_instruido_usd', 'activa',
       'status_cierre']

b = firmas[['codigo', 'fecha_cierre', 'tipo_respuesta',
       'favorabilidad', 'monto_instruido_dop', 'monto_instruido_usd', 'activa',
       'status_cierre']]

firmas = pd.merge(a, b, on='codigo', how='right')

#%%

import plotly.express as px
from plotly.offline import plot
#%%
inicio = firmas.fecha_cierre >= start_date
final = firmas.fecha_cierre < end_date
cierres = firmas[inicio & final]
# cierres = cierres[cierres.fecha_cierre.dt.month.apply(lambda x: x in [1,2,3,4,5])]

inicio = claims.fecha_creacion >= start_date
final = claims.fecha_creacion < end_date
aperturas = claims[inicio & final]
# aperturas = aperturas[aperturas.fecha_creacion.dt.month.apply(lambda x: x in [1,2,3,4,5])]

#%%

def add_year_month_cols(df, date_col):
    # df['year'] = df[date_col].dt.year
    # df['month_name'] = df[date_col].dt.strftime('%b')
    df['yearmonth'] = df[date_col].dt.strftime('%Y-%m')
    # df['month'] = df[date_col].dt.month
    return df

aperturas = add_year_month_cols(aperturas, 'fecha_creacion')
cierres = add_year_month_cols(cierres, 'fecha_cierre')
# df['semana_entrada'] = df['fecha_creacion'].dt.to_period('M').apply(lambda r: r.start_time)
# entradas = df.groupby('semana_entrada').count().codigo


data = pd.DataFrame([
aperturas.groupby('yearmonth').size(),
aperturas[~aperturas.activa].groupby('yearmonth').size(),
cierres.groupby('yearmonth').size()
], index=['entradas', 'descartadas', 'salidas']).fillna(0).astype(int).T
# data = data.reindex([1,2,3,4,5], level=0).reset_index()
# data.iloc[:, :3] = data.iloc[:, :3].astype(str)
data
#%%
data = pd.DataFrame([
aperturas.groupby(['month', 'month_name', 'year']).size(),
aperturas[~aperturas.activa].groupby('yearmonth').size(),
cierres.groupby(['month', 'month_name', 'year']).size()
], index=['Entradas', 'Salidas']).fillna(0).astype(int).T
# data = data.reindex([1,2,3,4,5], level=0).reset_index()
# data.iloc[:, :3] = data.iloc[:, :3].astype(str)
data
#%%
data = pd.DataFrame([
aperturas['fecha_creacion'].dt.to_period('M').apply(lambda r: r.start_time).value_counts(),
aperturas.loc[~aperturas.activa, 'fecha_creacion'].dt.to_period('M').apply(lambda r: r.start_time).value_counts(),
cierres['fecha_cierre'].dt.to_period('M').apply(lambda r: r.start_time).value_counts()
    ], index=['Entradas', 'descartadas', 'Salidas']).fillna(0).astype(int).T
data


#%%
fig = px.bar(data, x='month_name', y='Salidas', color='year'
             , template='presentation', text_auto=True
             # , color_discrete_map={'2022': 'blue', '2021': 'orange', '2020': 'orange'}
             , color_discrete_sequence=px.colors.sequential.Oranges[3::3]
             , barmode='group'
             , width=700, height=600, opacity=0.8)
fig.update_layout(
    yaxis_showgrid=False,
    showlegend=True
    , legend_title='Año'
    ,bargap=0.35
    # xaxis_tickformat = '%_d %b'
    # xaxis_tickvals=list(data.index),
    # xaxis_ticktext=[f.strftime('%b') for f in data.index]
    ,uniformtext_minsize=20, uniformtext_mode='show',
)

# fig.add_hline(
#     matriz['fecha_creacion'].dt.to_period('M').apply(lambda r: r.start_time).value_counts().sort_index()[-52:-1].mean(),
#     line_dash='dash',
#     line_color=px.colors.qualitative.T10[1],
#     line_width=3
# )
# fig.add_hline(
#     matriz['fecha_cierre'].dt.to_period('M').apply(lambda r: r.start_time).value_counts().sort_index()[-52:-1].mean(),
#     line_dash='dash',
#     line_color=px.colors.qualitative.T10[0],
#     line_width=3
# )

fig.update_traces(
    textposition='outside',
    textfont_family='Calibri',
    # textfont_size = 20

)
plot(fig)


#%%
matriz = pd.merge(claims, firmas, on='codigo', how='outer')
matriz = matriz[matriz.fecha_creacion > matriz.fecha_cierre.min()]

sin_verificacion = matriz.fecha_verificacion.isna()

matriz.loc[sin_verificacion, 'fecha_inicio'] = matriz.loc[sin_verificacion, 'fecha_creacion']
matriz.loc[~sin_verificacion, 'fecha_inicio'] = matriz.loc[~sin_verificacion, 'fecha_verificacion']

#%%
entradas = list(set(matriz['fecha_creacion'].dt.to_period('M').apply(lambda r: r.start_time)))
entradas.sort()
pendientes = {}
retrasadas = {}
for n in entradas:
    filtro_descartada = matriz.status_cierre != 'D'
    filtro_desestimada = matriz.tipo_respuesta != 'Desestimada'
    sin_descartes = matriz[filtro_descartada & filtro_desestimada]
    # print(len(sin_descartes))
    filtro_na = sin_descartes.fecha_cierre.isna()
    filtro_month = sin_descartes.fecha_cierre >= n
    sin_cierre = sin_descartes[filtro_na | filtro_month]
    # sin_cierre
    # print(len(sin_cierre))
    filtro_entrada = sin_cierre.fecha_creacion < n
    entro_antes = sin_cierre[filtro_entrada]
    # entro_antes
    # print(len(entro_antes))
    pending = entro_antes.shape[0]
    mas60 = (n - entro_antes.fecha_inicio).dt.days > 60
    late = entro_antes[mas60].shape[0]
    retrasadas[n.date()] = late
    pendientes[n.date()] = pending
    # print()
sla = pd.DataFrame([pendientes, retrasadas], index=['pendientes', 'retrasadas']).sort_index().T
sla['a_tiempo'] = sla.pendientes - sla.retrasadas
sla['a_tiempo%'] = sla.a_tiempo/sla.pendientes
sla['retrasadas%'] = sla.retrasadas/sla.pendientes
sla



#%%
fig = px.bar(sla, y=['retrasadas', 'a_tiempo'], text_auto=True, color_discrete_sequence=['#E45756',
 '#54A24B'], opacity=0.8, template='presentation', width=1000, height=600,
             custom_data=['pendientes', 'a_tiempo%', 'retrasadas%'], range_y=[0,sla.pendientes.max()*1.3])
fig.update_layout(
    yaxis_showgrid=False,
    xaxis_tickvals=list(sla.index),
    xaxis_ticktext=[f.strftime('%d %b') for f in sla.index],
    showlegend=False,
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.99,
        title="Leyenda",
        )
    ,uniformtext_minsize=12, uniformtext_mode='show',
    bargap=0.5
    # ,textfont_align='left'

)
fig.update_traces(
    texttemplate =(
        'P: <b>%{customdata[0]:.}</b>'
        '<br>✅: %{customdata[1]:.0%}'
        '<br>❌: %{customdata[2]:.0%}'
        '<br> '

    ),
    # text ='left',
    textposition='outside',
# textposition="bottom center",
    # width=np.array([10,20,20,50])
    # text_min_size=10
    textfont_size = 13
)
fig.for_each_trace(
    # lambda trace: trace.update(texttemplate=(
    #                             '❌: %{customdata[2]:.0%}'
    #                             '<br> '
    #                             '<br> '
    #
    #
    #                             )
    #                         ) if trace.name == "retrasadas" else trace.update(texttemplate=(
    #                             'P: <b>%{customdata[0]:.}</b>'
    #                             '<br>✅: %{customdata[1]:.0%}'
    #                             '<br> '
    #                             )
    #
    # )
    lambda trace: trace.update(texttemplate=None) if trace.name == "retrasadas" else ()

)
fig.add_hline(
    sla.pendientes.mean(),
    line_dash='dash',
    line_color="#3366cc",
    line_width=3,
    # annotation_text=f'Promedio pendientes<br>Ult. 12 Meses: <b>{pendings.pendientes.mean():.0f}</b>',
    # annotation_font_size=13,
    # annotation_position="bottom left",
    # annotation_align='left',
    # annotation_bgcolor='white',
    # annotation_opacity=0.8
)
plot(fig)

#%%
cierres['yearmonth'] = cierres.fecha_cierre.dt.to_period('M').apply(lambda r: r.start_time)
cierres.groupby(['yearmonth', 'favorabilidad']).size()
#%%
grupero = pd.Grouper(key='fecha_cierre', freq='M')
favorabilidad = cierres.groupby([grupero, 'favorabilidad']).size()

favorabilidad = (
    cierres
    .groupby([grupero, 'favorabilidad'])
    .size()
    .rename('cantidad')
    .sort_index()
    .reset_index()
    .pivot(index='fecha_cierre', columns='favorabilidad', values='cantidad')
    .fillna(0)
    .astype(int)
)
favorabilidad
# favorabilidad.index = favorabilidad.index - pd.tseries.offsets.Week()

#%%
favorabilidad['con_decision'] = favorabilidad['D'] + favorabilidad['F']
favorabilidad['con_decision']
favorabilidad['%_desfavorable'] = favorabilidad['D']  / favorabilidad['con_decision']
favorabilidad['%_favorable'] = favorabilidad['F']/ favorabilidad['con_decision']
# favorabilidad.index = favorabilidad.index - timedelta(6)

# favorabilidad = favorabilidad.reset_index()
# favorabilidad[['month', 'month_name', 'year']] = favorabilidad[['month', 'month_name', 'year']].astype(str)
favorabilidad

#%%

max_y = favorabilidad.con_decision.max()
fig = px.bar(favorabilidad, y='%_favorable', x='month_name',
            color='year', barmode='group',
            text_auto=True, color_discrete_sequence=px.colors.sequential.Greens[4::3],
            opacity=0.8, template='presentation', width=1100, height=600,
            custom_data=['%_favorable', '%_desfavorable', 'con_decision']
)

fig.update_layout(
    yaxis_showgrid=False,
    yaxis_tickformat='.0%',
    # xaxis_tickvals=list(favorabilidad.index),
    # xaxis_ticktext=[f.strftime('%d %b') for f in favorabilidad.index],
    showlegend=True,
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.99,
        title="Leyenda",
        )
    ,uniformtext_minsize=20, uniformtext_mode='show',
    bargap=0.5
    # ,textfont_align='left'

)

fig.update_traces(
    # texttemplate =(
    #     'P: <b>%{customdata[0]:.}</b>'
    #     '<br>✅: %{customdata[1]:.0%}'
    #     '<br>❌: %{customdata[2]:.0%}'
    #     '<br> '
    #     '<br> '
    # ),
    # text ='left',
    textposition='outside',
    # width=np.array([10,20,20,50])
    # text_min_size=10
    textfont_size = 16
)

fig.for_each_trace(
    lambda trace:
    trace.update(texttemplate=(
        '<b>%{customdata[2]}</b>'
        '<br> '
        '%{customdata[1]:.0%}'
        )
    )
    if trace.name == "Desfavorable"
    else trace.update(texttemplate='%{customdata[0]:.0%}')
)

plot(fig)

#%%

no_acreditacion = (cierres.monto_total == 0) ^ (cierres.monto_total.isna())
# grouper = pd.Grouper(key='fecha_cierre', freq='W')
favorable = cierres.favorabilidad == "Favorable"
no_reconsideracion = cierres.reconsideracion == False
grupo = cierres[favorable & no_reconsideracion & ~no_acreditacion].groupby('yearmonth')

montos = pd.DataFrame([
    grupo.sum()['monto_total'],
    grupo.mean()['monto_total'].rename('monto_promedio'),
    grupo.size().rename('condevolucion')]).T


    # .reset_index()
    # .pivot(index='fecha_salida_informe_final', columns='favorabilidad', values='cr')
# montos.index = montos.index - timedelta(6)
# montos = montos.reset_index()
# montos.iloc[:, :3] = montos.iloc[:, :3].astype(str)
montos

#%%

max_y = montos.max()
fig = px.bar(montos, y='monto_total', x='month_name', color='year'
            ,text_auto=True, color_discrete_sequence=['#5C7F91', "#0D3048"],
            opacity=0.8, template='presentation', width=1100, height=600,
             barmode='group'
            # custom_data=['%_favorable', '%_desfavorable', 'con_decision'],
            #  range_y=[0,max_y*1.2]
)

fig.update_layout(
    yaxis_showgrid=False,
    # xaxis_tickvals=list(favorabilidad.index),
    # xaxis_ticktext=[f.strftime('%d %b') for f in favorabilidad.index],
    showlegend=True,
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.99,
        title="Leyenda",
        )
    ,uniformtext_minsize=20, uniformtext_mode='show',
    bargap=0.5
    # ,textfont_align='left'

)

fig.update_traces(
    texttemplate =(
         '$%{y:,.2s}'
    ),
    # text ='left',
    textposition='outside',
    # width=np.array([10,20,20,50])
    # text_min_size=10
    textfont_size = 16
)

# fig.add_hline(
#     # montos.mean(),
#     line_dash='dash',
#     line_color='#f77245',
#     line_width=3,
#     # annotation_text=f'Promedio pendientes<br>Ult. 12 Meses: <b>{pendings.pendientes.mean():.0f}</b>',
#     # annotation_font_size=13,
#     # annotation_position="bottom left",
#     # annotation_align='left',
#     # annotation_bgcolor='white',
#     # annotation_opacity=0.8
# )

plot(fig)

#%%
aperturas
from importlib import reload
reload(dashboards.banks_rank_grapher)

from dashboards.principal.banks_rank_grapher import creates_banks_ranks

grupero_semanal = pd.Grouper(key='fecha_creacion', freq='W')
eif_per_week = aperturas.groupby([grupero_semanal, 'eif']).size()
entries_per_bank = creates_banks_ranks(eif_per_week)
cat_per_week = aperturas.groupby([grupero_semanal, 'categoria']).size()
entries_per_cat = creates_banks_ranks(cat_per_week, color_col='categoria')


#%%
# entries_per_bank['layout']
entries_per_bank.update_layout(
    xaxis_tickmode='array',
xaxis_tickvals = list(set(eif_per_week.index.get_level_values(0))),
xaxis_ticktext = [(f-timedelta(days=6)).strftime('%d %b') for f in set(eif_per_week.index.get_level_values(0))]
)
plot(entries_per_bank)

#%%
entries_per_cat.update_layout(
    xaxis_tickmode='array',
xaxis_tickvals = list(set(eif_per_week.index.get_level_values(0))),
xaxis_ticktext = [(f-timedelta(days=6)).strftime('%d %b') for f in set(eif_per_week.index.get_level_values(0))]
)
plot(entries_per_cat)


#%%

metricas = pd.concat([data, sla, favorabilidad, montos], axis=1)
metricas = pd.concat([data, sla, favorabilidad], axis=1)
metricas.to_excel('metricas_transparencia_julio2022.xlsx')


#%%

megamatriz = pd.merge(claims, matriz, on='codigo', how='left')

descartadas = ~megamatriz['activa_x'] ^ (megamatriz.status_cierre == 'Descartada')
descartes = megamatriz[descartadas]
#%%
descartes['fecha_creacion_x'].dt.strftime('%Y-%m').value_counts().sort_index()