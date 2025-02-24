"""
Creado el 9/6/2022 a las 5:59 p. m.

@author: jacevedo
"""

import pandas as pd
from datetime import date, timedelta
import sql_tools
from sqlalchemy import String, Float, Boolean
import reclamos_reading
from prousuario_tools import get_tipos_viafirma

#%%


def get_firmas_reclamos():
    query = "select * from FIRMAS where tipo = 'reclamos'"
    df = sql_tools.query_reader(query, mode='all')
    return df


def check_sign(x, firmas):
    try:
        result = firmas.loc[firmas.asunto.str.contains(x), 'fecha_firma'].values[-1]
    except IndexError:
        # print(e)
        result = None
    return result


def check_response(x, firmas):
    try:
        result = firmas.loc[firmas.asunto.str.contains(x), 'tipo_respuesta'].values[-1]
    except IndexError:
        result = None
    return result


def assign_response(asuntos, tipos):
    tipo_respuesta = pd.Series(None, index=asuntos.index, dtype=object)
    for tipo in tipos.keys():
        tipo_respuesta.loc[asuntos.str.contains(tipo)] = tipo
    favorabilidad = tipo_respuesta.map(tipos)
    return tipo_respuesta, favorabilidad
#%%


def get_results():
    query = 'select * from RESULTADOS_RECLAMOS'
    resultados = sql_tools.query_reader(query, mode='all')
    resultados.activa = resultados.activa.astype(bool)
    return resultados


def process_results(sin_resultado, firmas, tipos_viafirma):
    sin_resultado.loc[:, 'fecha_cierre'] = sin_resultado['codigo'].apply(lambda x: check_sign(x[-6:], firmas))
    sin_resultado.loc[:, 'tipo_respuesta'] = sin_resultado['codigo'].apply(lambda x: check_response(x[-6:], firmas))
    sin_resultado.loc[:, 'favorabilidad'] = sin_resultado['tipo_respuesta'].map(tipos_viafirma)
    sin_resultado.loc[~sin_resultado.fecha_cierre.isna(), 'status_cierre'] = 'C'
    sin_resultado.loc[~sin_resultado.activa, 'status_cierre'] = 'D'
    return sin_resultado


def get_sin_resultados(mezcla):
    sin_firma = mezcla.fecha_cierre.isna()
    sin_descartes = mezcla.status_cierre.isna()
    sin_resultado = sin_firma & sin_descartes & mezcla.activa
    sin_resultado = sin_firma & sin_descartes
    sin_resultado = mezcla[sin_resultado].copy()
    return sin_resultado


def create_fecha_inicio(data):
    sin_verificacion = data.fecha_verificacion.isna()
    data.loc[sin_verificacion, 'fecha_inicio'] = data.loc[sin_verificacion, 'fecha_creacion'].copy()
    data.loc[~sin_verificacion, 'fecha_inicio'] = data.loc[~sin_verificacion, 'fecha_verificacion'].copy()
    return data['fecha_inicio']


def create_fecha_inicio(data):
    sin_verificacion = data.fecha_verificacion.isna()
    fecha_inicio = data['fecha_creacion'].copy()
    fecha_inicio.loc[~sin_verificacion] = data.loc[~sin_verificacion, 'fecha_verificacion'].copy()
    return fecha_inicio

#%%


dtypes = {
    'activa': Boolean(),
    'codigo': String(12),
    'favorabilidad': String(1),
    'monto_instruido_dop': Float(),
    'monto_instruido_usd': Float(),
    'status_cierre': String(1),
    'tipo_respuesta': String(50)
    }

favorabilidad_map = {'Favorable': 'F', 'Desfavorable': 'D', 'Otra': 'O'}
#%%


def main():
    end_date = (date.today() + timedelta(1)).strftime('%Y-%m-%d')
    resultados = get_results()
    claims = reclamos_reading.main(start_date='2021-01-01', end_date=end_date)
    mezcla = pd.merge(claims, resultados, on=['codigo', 'activa'], how='left')
    mezcla.loc[~mezcla.activa, 'status_cierre'] = 'D'
    firmas = get_firmas_reclamos()
    tipos_viafirma = get_tipos_viafirma()['reclamos']
    firmas['tipo_respuesta'], firmas['favorabilidad'] = assign_response(firmas.asunto, tipos_viafirma)
    sin_resultado = get_sin_resultados(mezcla)
    new_results = process_results(sin_resultado, firmas, tipos_viafirma).copy()
    new_results['fecha_inicio'] = create_fecha_inicio(new_results[['fecha_creacion', 'fecha_verificacion']])
    new_results = new_results[resultados.columns]
    new_results = new_results.dropna(subset=['fecha_cierre', 'status_cierre'])
    new_results.favorabilidad = new_results.favorabilidad.map(favorabilidad_map)
    with sql_tools.conn_creator() as conn:
        new_results.to_sql('resultados_reclamos', conn, index=False, dtype=dtypes, if_exists='append')
    cantidad = len(new_results)
    print(f'Hubo {cantidad} nuevos resultados')
    print('Termino actualizando resultados de reclamos')


if __name__ == "__main__":
    main()
