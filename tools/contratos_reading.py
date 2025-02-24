"""
Creado el 20/3/2024 a las 3:14 PM

@author: jacevedo
"""
from sql_tools import query_reader

"""
Creado el 24/5/2022 a las 6:51 p. m.

@author: jacevedo
"""

import locale
import numpy as np
from lectura_odata import get_reclamos
from general_tools import convert_time
from prousuario_tools import get_odata_parameters, get_bank_names, get_categories, get_categoria_producto, get_tipo_canal
import pandas as pd
from datetime import timedelta

locale.setlocale(locale.LC_ALL, 'es_DO.UTF-8')

#
# ['secuencial', 'codigo', 'fecha_creacion', 'fecha_notificacion',
#        'decision', 'tiempo_de_respuesta', 'estatus_tarde', 'eif',
#        'razon_social', 'producto_crudo', 'tipo_producto', 'consulta_cruda',
#        'tipo_consulta', 'no._consulta_sib_interactivo', 'descripcion',
#        'sustitucion_referencia']
def read_matriz():
    path = r"C:\Users\jacevedo\OneDrive - Superintendencia de Bancos de la Republica Dominicana\Shared Documents - ProUsuario Wiki\3. División Legal\Unidad Legal\Nueva Matriz Contratos.xlsm"
    contratos = pd.read_excel(path, sheet_name='Matriz Contratos', header=3)
    contratos.columns = contratos.columns.str.lower().str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8').str.replace(' ', '_')
    return contratos

def read_data():
    query = "select * from RESULTADOS_CONTRATOS"
    return query_reader(query, mode='all')

def get_contrato_kpi(terminadas):
    terminadas['mes'] = terminadas.fecha_notificacion.dt.to_period('M')
    promedio_dias = (
        terminadas[['mes', 'tiempo_de_respuesta', 'tipo_consulta']]
        .groupby(['mes', 'tipo_consulta'])
        .mean()['tiempo_de_respuesta']
        .rename('promedio_dias')
        .reset_index()
        .pivot(index='mes', columns='tipo_consulta', values='promedio_dias')
        )
    promedio_dias.columns = [len(promedio_dias.columns) * ['promedio_dias'], promedio_dias.columns]
    total_dias = (
        terminadas[['mes', 'tiempo_de_respuesta', 'tipo_consulta']]
        .groupby(['mes', 'tipo_consulta'])
        .mean()['tiempo_de_respuesta']
        .rename('total_dias')
        .reset_index()
        .pivot(index='mes', columns='tipo_consulta', values='total_dias')
        .fillna(0).astype(int)
        )
    total_dias.columns = [len(total_dias.columns) * ['total_dias'], total_dias.columns]
    total_casos = (
        terminadas[['mes', 'tiempo_de_respuesta', 'tipo_consulta']]
        .groupby(['mes', 'tipo_consulta'])
        .size()
        .rename('total_casos')
        .reset_index()
        .pivot(index='mes', columns='tipo_consulta', values='total_casos')
        .fillna(0).astype(int)
        )
    total_casos.columns = [len(total_casos.columns) * ['total_casos'], total_casos.columns]

    terminadas['meta'] = 30
    filtro_meta_nueva = terminadas.fecha_notificacion > '2023-12-01'
    terminadas.loc[filtro_meta_nueva, 'meta'] = terminadas.tipo_consulta.map({'SIB': 25, 'RA':22})
    terminadas['tarde'] = terminadas.tiempo_de_respuesta > terminadas['meta']
    casos_tarde = (
        terminadas[['mes', 'tarde']]
        .groupby(['mes', 'tarde'])
        .size()
        .reset_index()
        .pivot_table(index='mes', columns='tarde', values=0)[False]
        .fillna(0).astype(int).rename('casos_a_tiempo')
        .to_frame()
        )
    casos_tarde['porcentaje'] = casos_tarde['casos_a_tiempo'] / total_casos.sum(axis=1)

    kpi = pd.concat([
    promedio_dias,
    total_dias,
    total_casos,
    casos_tarde], axis=1)
    return kpi

#%%
# if __name__ == "__main__":
    # main(**kwargs)
# df = main(fecha_limite='2022-04-30')
