"""
Creado el 9/6/2022 a las 5:59 p. m.

@author: jacevedo
"""
import pandas as pd
from sqlalchemy import String
from datetime import date, timedelta

import infofinanciera_reading
import sql_tools
from prousuario_tools import get_tipos_viafirma


def get_firmas_info():
    query = "select * from FIRMAS where tipo = 'info_financiera'"
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


dtypes = {
    'codigo': String(12),
    'tipo_informe': String(50),
    'aprobacion': String(25)
    }


#%%
def main():
    end_date = (date.today() + timedelta(1)).strftime('%Y-%m-%d')
    query = 'select * from RESULTADOS_INFO'
    resultados = sql_tools.query_reader(query, mode='all')
    info = infofinanciera_reading.main('2022-01-01', end_date)
    mezcla = pd.merge(info, resultados, on='codigo', how='left')
    mezcla.fecha_inicio = mezcla.fecha_verificacion.copy()
    firmas = get_firmas_info()
    tipos_viafirma = get_tipos_viafirma()['info_financiera']
    firmas['tipo_respuesta'], firmas['favorabilidad'] = assign_response(firmas.asunto, tipos_viafirma)
    sin_firma = mezcla.fecha_cierre.isna()
    sin_inactivas = mezcla.activa != 'Inactive'
    sin_central = mezcla.tipo_info_solicitada != 'Central de Riesgos'
    sin_resultado = sin_firma & sin_inactivas & sin_central
    sin_resultado = mezcla[sin_resultado].copy()
    sin_resultado.loc[:, 'fecha_cierre'] = sin_resultado['codigo'].apply(lambda x: check_sign(x[-6:], firmas))
    sin_resultado.loc[:, 'tipo_informe'] = sin_resultado['codigo'].apply(lambda x: check_response(x[-6:], firmas))
    sin_resultado.loc[:, 'aprobacion'] = sin_resultado['tipo_informe'].map(tipos_viafirma)
    new_results = sin_resultado[resultados.columns]
    new_results = new_results.dropna(subset='fecha_cierre')
    with sql_tools.conn_creator() as conn:
        new_results.to_sql('resultados_info', conn, index=False, dtype=dtypes, if_exists='append')
    cantidad = len(new_results)
    print(f'Hubo {cantidad} nuevos resultados')
    print('Termino actualizando resultados de informacion financiera')

#%%
if __name__ == "__main__":
    main()