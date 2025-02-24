"""
Creado el 4/4/2023 a las 4:14 a. m.

@author: jacevedo
"""

import reclamos_reading
import pandas as pd
from general_tools import excel_formatter

from sql_tools import query_reader
from datetime import date
from pandas.tseries.offsets import MonthEnd, MonthBegin

#%%
START_DATE = (date.today() - MonthBegin(2)).date()
END_DATE = (date.today() - MonthEnd()).date()
END_DATE_SQL = (date.today() - MonthBegin()).date()

#%%
claims = reclamos_reading.main(START_DATE, END_DATE)
claims['mes'] = claims.fecha_creacion.dt.to_period('M')
claims = claims[claims.activa].reset_index(drop=True)
claims.reconsideracion = claims.reconsideracion.map({True: 'Reconsideraciones', False:'Reclamaciones'})
total_mes = claims.reconsideracion.value_counts()

#%%
filtro_eif = claims.eif.str.contains('BANRESERVAS|BHD|POPULAR|SCOTIA')
agrupado = claims[filtro_eif].groupby(['eif', 'reconsideracion', 'tipo_reclamo']).size().rename('cantidad')
# feb_group = feb[filtro_eif].groupby(['mes', 'eif', 'reconsideracion']).size().rename('cantidad')
# recon =feb_group.xs('Reconsideraciones', level=1).reset_index().pivot_table(index='mes', columns='eif', values='cantidad').fillna(0).astype(int)
# cantidad = feb_group.groupby(level='eif').reset_index(level=0, drop=True)
# otros = feb_group.groupby(level='eif').sum() - cantidad.groupby(level='eif').sum()
# otros.index = pd.MultiIndex.from_product([otros.index, ['OTROS']], names=['eif', 'tipo_reclamo'])
# cantidad = pd.concat([feb_group, otros]).astype(int)
# cantidad = feb_group.astype(int)
# reclamaciones = cantidad.loc[:, 'Reclamaciones']
reclamaciones = agrupado.xs('Reclamaciones', level=1)
reconsideraciones = agrupado.xs('Reconsideraciones', level=1)
# reconsideraciones = cantidad.loc[:, 'Reconsideraciones']

def create_report(df, total_general):
    total = df.groupby(level='eif').sum()
    porcentaje = (df / total).rename('porcentaje').apply(lambda x: f'{x:.1%}')
    total.index = pd.MultiIndex.from_product([total.index, ['TOTAL']], names=['eif', 'tipo_reclamo'])
    cantidad = pd.concat([df, total]).astype(int)
    reporte = pd.DataFrame([cantidad, porcentaje]).T
    reporte = reporte.sort_values(by=['eif', 'cantidad'], ascending=False).reset_index()
    reporte.loc[len(reporte)] = ['TOTAL GENERAL', None, total_general, None]
    return reporte

reporte_reclamaciones = create_report(reclamaciones, total_mes['Reclamaciones'])
reporte_reconsideraciones = create_report(reconsideraciones,total_mes['Reconsideraciones'])


# lel.loc[len(lel)] = ['TOTAL GENERAL RECLAMACIONES', None, len(feb), None]
# lel = create_report(reconsideraciones)
#%%

back_claims = reclamos_reading.main('2022-01-01')
back_claims = back_claims[back_claims.activa]
back_claims = back_claims[back_claims.eif.str.contains('BANRESERVAS|BHD|POPULAR|SCOTIA')]
query = f"""
select * from RESULTADOS_RECLAMOS
where FECHA_CIERRE between date '{START_DATE}' and date '{END_DATE_SQL}'
and FAVORABILIDAD in ('F', 'D')
"""

results = query_reader(query, mode='all')
(results.favorabilidad.value_counts() / results.favorabilidad.size)['F']

results = pd.merge(results, back_claims[['codigo', 'eif']], on='codigo', how='left')
results_por_eif = results.pivot_table(index='eif', columns='favorabilidad', values='codigo', aggfunc='count').fillna(0)
favorabilidad = (results_por_eif.F / results_por_eif.sum(axis=1)).reset_index()
favorabilidad.columns = ['EIF', 'Favorabilidad']
favorabilidad.loc[len(favorabilidad)] =  ['GENERAL', (results.favorabilidad.value_counts() / results.favorabilidad.size)['F']]
#%%

top4 = pd.Series(claims.tipo_reclamo.value_counts().nlargest(4).index).rename().reset_index()
top4.columns = ['Orden', 'Top 4 Tipos de Reclamación Más Frecuentes']
top4['Orden'] = top4['Orden']+1
top4
#%%
with pd.ExcelWriter(f'{FOLDER_PATH}reclamos_2025_01.xlsx', engine='xlsxwriter') as writer:
    excel_formatter(writer, reporte_reclamaciones, 'Reclamaciones')
    excel_formatter(writer, reporte_reconsideraciones, 'Reconsideraciones')
    excel_formatter(writer, favorabilidad, 'Favorabilidad por EIF')
    excel_formatter(writer, top4, 'Reclamaciones más frecuentes')



#%%

