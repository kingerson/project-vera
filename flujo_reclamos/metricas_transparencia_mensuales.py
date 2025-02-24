"""
Creado el 4/8/2022 a las 3:59 p. m.

@author: jacevedo
"""

import sql_tools
import reclamos_reading
import pandas as pd

recibidas = reclamos_reading.main('2022-07-01', '2022-07-31')
query = (
    "select * from RESULTADOS_RECLAMOS "
    "where FECHA_CIERRE > to_date('2022-07-01', 'YYYY-MM-DD')"
    " and FECHA_CIERRE < to_date('2022-08-01', 'YYYY-MM-DD')"
)
completadas = sql_tools.query_reader(query, mode='all')

def get_results(dbase):
    query = (
        f"select * from {dbase}"
        " where"
        " fecha_cierre > to_date('2021-08-01', 'YYYY-MM-DD')"
        " OR"
        " fecha_cierre is null"
    )
    salidas = sql_tools.query_reader(query, mode='all')
    return salidas

def get_pendings():
    entradas = reclamos_reading.main(start_date='2021-08-01')
    salidas = get_results('RESULTADOS_RECLAMOS')
    matriz = pd.merge(entradas, salidas, on='codigo', how='left')
    filtro_descartada = matriz['status_cierre'] != 'D'
    sin_inactiva = matriz.activa_x
    limpia = matriz[filtro_descartada & sin_inactiva]
    filtro_na = limpia['fecha_cierre'].isna()
    filtro_fecha = limpia['fecha_cierre'] > '2022-08-01'
    sin_cierre = limpia[filtro_na | filtro_fecha]
    return sin_cierre

metricas = {}

metricas['recibidas'] = recibidas.shape[0]
try:
    metricas['descartadas'] = recibidas.activa.value_counts()[False]
except KeyError:
    metricas['descartadas'] = 0
metricas['completadas'] = completadas.shape[0]
metricas['pendientes'] = get_pendings().shape[0]
metricas['sin_decision'] = completadas.favorabilidad.value_counts()['O']
metricas['favorable'] = completadas.favorabilidad.value_counts()['F']
metricas['desfavorable'] = completadas.favorabilidad.value_counts()['D']
metricas['con_decision'] = metricas['favorable'] + metricas['desfavorable']
metricas['% favorable'] = metricas['favorable'] / metricas['con_decision']
metricas['% desfavorable'] = metricas['desfavorable'] / metricas['con_decision']

#%%

filepath = r"C:\Users\jacevedo\Documents\ProUsuario Project\cierres.xlsx"
cierres_roselis = pd.read_excel(filepath)

salidas = get_results('RESULTADOS_RECLAMOS')
mezcla_roselis = pd.merge(cierres_roselis, salidas, how='left', left_on='cr', right_on='codigo')
