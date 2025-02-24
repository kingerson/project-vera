"""
Creado el 15/7/2022 a las 11:53 a. m.

@author: jacevedo
"""

import pandas as pd
import reclamos_reading, infofinanciera_reading
import sql_tools
from datetime import datetime

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

def get_pendientes(tipo='reclamos'):
    pendientes = {}
    if tipo == 'reclamos':
        entradas = reclamos_reading.main(start_date='2021-08-01')
        salidas = get_results('RESULTADOS_RECLAMOS')
        matriz = pd.merge(entradas, salidas, on='codigo', how='left')
        filtro_descartada = matriz['status_cierre'] != 'D'
        sin_inactiva = matriz.activa_x
        limpia = matriz[filtro_descartada & sin_inactiva]
        filtro_na = limpia['fecha_cierre'].isna()
        sin_cierre = limpia[filtro_na]
    elif tipo == 'info':
        entradas = infofinanciera_reading.main('2021-08-01')
        salidas = get_results('RESULTADOS_INFO')
        limpia = pd.merge(entradas, salidas, on='codigo', how='left')
        filtro_na = limpia['fecha_cierre'].isna()
        sin_cierre = limpia[filtro_na]
    mas60 = (datetime.today() - sin_cierre['fecha_verificacion']).dt.days > 60
    pendientes['pendiente'] = sin_cierre.shape[0]
    pendientes['fuera_sla'] = sin_cierre[mas60].shape[0]
    pendientes['a_tiempo'] = pendientes['pendiente'] - pendientes['fuera_sla']
    pendientes['a_tiempo_pct'] = pendientes['a_tiempo'] / pendientes['pendiente']
    pendientes['fuera_sla_pct'] = pendientes['fuera_sla'] / pendientes['pendiente']
    return pendientes
