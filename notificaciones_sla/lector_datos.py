# %%

import locale
from datetime import date, timedelta

import pandas as pd
from prousuario_tools import get_odata
from general_tools import convert_time
import sql_tools

# %%
locale.setlocale(locale.LC_ALL, 'es_DO')


def clean_data(df, nombres_columnas):
    """Elimina las columas no"""
    columnas_formateadas = df.columns[df.columns.str.contains(FORMAT_LABEL)]
    for c in columnas_formateadas:
        short = c.split('@')[0]
        if c in df.columns:
            if c in {
                'createdon@OData.Community.Display.V1.FormattedValue',
                'new_fechaderespuestadestatustramite@OData.Community.Display.V1.FormattedValue',
                'new_fechadeverificaciondelcaso@OData.Community.Display.V1.FormattedValue'
            }:
                df.drop(c, inplace=True, axis=1)
            else:
                df.drop(short, inplace=True, axis=1)
                df.rename(columns={c: short}, inplace=True)
    df.columns = df.columns.map(nombres_columnas)
    return df


def creador_rangos(df):
    df['dias_abierto'] = (FECHA_HOY - df['fecha_verificacion'].dt.date).dt.days
    rangos = [60, 45, 30]
    for r in rangos:
        filtro = df.dias_abierto.between(r-6, r)
        df.loc[filtro, 'rango'] = f'{r} días'
    mayor_60 = df.dias_abierto.between(60, 180)
    df.loc[mayor_60, 'rango'] = "Mas de 60 días"
    df.dropna(subset='rango', inplace=True)
    return df


def busca_firmas(tabla):
    fecha_limite = date.today() - timedelta(180)
    query = (
        'select codigo, FECHA_CIERRE '
        'from RESULTADOS_INFO '
        f"where FECHA_CIERRE > to_date('{fecha_limite}', 'YYYY-MM-DD')"
    )
    if tabla == "new_reclamacins":
        query = (
            'select codigo, FECHA_CIERRE '
            'from RESULTADOS_RECLAMOS '
            f"where FECHA_CIERRE > to_date('{fecha_limite}', 'YYYY-MM-DD')"
        )
    result = sql_tools.query_reader(query, mode='all')
    return result


# %%
def main(parameters):
    droppable_columns = parameters['droppable_columns']
    query = parameters['query']
    nombres_columnas = parameters['nuevos_nombres_columnas']
    df = get_odata(query, HEADERS)
    if parameters['tabla'] == "new_reclamacins":
        df.insert(3, 'reclamante', df['new_nombre'] + ' ' + df['new_apellidos'])
        df.drop(['new_nombre', 'new_apellidos'], axis=1, inplace=True)
    df.drop(droppable_columns, axis=1, inplace=True)
    df = clean_data(df, nombres_columnas)
    df['fecha_creacion'] = convert_time(df.fecha_creacion)
    df['fecha_verificacion'] = convert_time(df.fecha_verificacion)
    print(df.columns)
    df.dropna(subset=['codigo', 'correo_solicitante'], inplace=True)
    result = busca_firmas(parameters['tabla'])
    mezcla = pd.merge(df, result, on='codigo', how='left')
    df = mezcla[mezcla.fecha_cierre.isna()]
    df = creador_rangos(df)
    return df


FECHA_HOY = date.today()
HEADERS = {
    "OData-MaxVersion": "4.0",
    "OData-Version": "4.0",
    "Accept": "application/json",
    "Content-Type": "application/json; charset=utf-8",
    "Prefer": "odata.include-annotations=OData.Community.Display.V1.FormattedValue"
}
FORMAT_LABEL = "OData.Community.Display.V1.FormattedValue"

