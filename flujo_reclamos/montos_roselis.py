"""
Creado el 23/8/2022 a las 3:49 p. m.

@author: jacevedo
"""
import pandas as pd
import reclamos_reading
from datetime import datetime, timedelta

filepath = r"C:\Users\jacevedo\Documents\Salidas hasta 22 agosto 22.xlsx"
roselis = pd.read_excel(filepath)
#%%
roselis.columns = roselis.columns.str.lower().str.strip().str.replace(' ', '_').str.replace('us$', 'usd', regex=True).str.replace('dop$', 'dop', regex=True)
roselis.rename({'cr': 'codigo'}, axis=1, inplace=True)


#%%

claims = reclamos_reading.main(start_date='2021-06-01')
mezcla = pd.merge(roselis, claims, how='left', on='codigo')

#%%
['codigo', 'fecha', 'día', 'mes', 'año', 'recurso_reconsideracion',
       'recurrente', 'entidad', 'tipo_reclamación', 'producto', 'canal_x',
       'monto_reclamado_dop$', 'monto_reclamado_us$', 'monto_reclamado_eu',
       'monto_recuperado_dop$', 'monto_recuperado_us$', 'monto_recuperado_eu',
       'notificación', 'nueva_evidencia', 'complejo', 'tipo_respuesta',
       'vario_respuesta', 'fecha_salida_informe_final', 'unnamed:_23',
       'fecha_creacion', 'activa', 'fecha_verificacion', 'reconsideracion',
       'eif', 'categoria', 'tipo_producto', 'canal_y', 'monto_reclamado_dop',
       'monto_reclamado_usd', 'monto_acreditado_dop', 'monto_acreditado_usd']

#%%
mezcla['monto_recuperado_dop$'] = pd.to_numeric(mezcla['monto_recuperado_dop$'], errors='coerce')
mezcla['monto_reclamado_us$'] = pd.to_numeric(mezcla['monto_reclamado_us$'], errors='coerce')
mezcla['monto_reclamado_eu'] = pd.to_numeric(mezcla['monto_reclamado_eu'], errors='coerce')

mezcla['monto_en_pesos'] = pd.concat(
    [mezcla['monto_recuperado_dop$'],
     mezcla['monto_reclamado_us$']*54,
     mezcla['monto_reclamado_eu']*54], axis=1
).sum(1, min_count=1)

mezcla['monto_en_pesos']
#%%

cierres = mezcla[mezcla.fecha_salida_informe_final.between('2022-06-27', '2022-08-21')].copy()

cierres['tipo_respuesta'] = cierres['tipo_respuesta'].str.lower().copy()
cierres['favorabilidad'] = cierres.tipo_respuesta.map({'favorable': 'Favorable',
 'desfavorable': 'Desfavorable',
 'parcial favorable': 'Favorable',
 'inadmisible': 'Otra',
 'carta informativa': 'Favorable',
 '-': 'Otra'}).copy()
#%%
freq='W'
no_acreditacion = (cierres.monto_en_pesos == 0) & (cierres.monto_en_pesos.isna())
grouper = pd.Grouper(key='fecha_salida_informe_final', freq=freq)
favorable = cierres.favorabilidad == "Favorable"
reconsideracion = cierres.reconsideracion
result = (
    cierres[favorable & ~reconsideracion & ~no_acreditacion]
        .groupby(grouper)
        .sum()['monto_en_pesos']
        .sort_index()
)
result.index = result.index - timedelta(6)