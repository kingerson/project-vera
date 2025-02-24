"""
Creado el 24/5/2022 a las 6:51 p. m.

@author: jacevedo
"""

import locale
import numpy as np
from lectura_odata import get_reclamos
from general_tools import convert_time
from prousuario_tools import get_odata_parameters, get_bank_names, get_categories, get_categoria_producto, get_tipo_canal
from pandas import concat, merge, DataFrame
from datetime import timedelta

locale.setlocale(locale.LC_ALL, 'es_DO.UTF-8')


def clean_data(df, format_label, nuevos_nombres):
    columnas_formateadas = df.columns[df.columns.str.contains(format_label)]
    for c in columnas_formateadas:
        if c in df.columns:
            if c in {
                'createdon@OData.Community.Display.V1.FormattedValue',
                'new_fechadeverificaciondelcaso@OData.Community.Display.V1.FormattedValue',
                'new_montoreclamado1@OData.Community.Display.V1.FormattedValue',
                'new_montoacreditado1@OData.Community.Display.V1.FormattedValue',
                'new_montoreclamado2@OData.Community.Display.V1.FormattedValue',
                'new_montoacreditado2@OData.Community.Display.V1.FormattedValue',
                # "new_duracionetapa1@OData.Community.Display.V1.FormattedValue",
                # "new_duracionetapa2@OData.Community.Display.V1.FormattedValue",
                # "new_duracionetapa3@OData.Community.Display.V1.FormattedValue"
            }:
                df.drop(c, inplace=True, axis=1)
            else:
                df[c.split('@')[0]] = df[c]
                df.drop(c, inplace=True, axis=1)
    df.rename(nuevos_nombres, axis=1, inplace=True)
    return df

def normalizes_currencies_reclamos(df):
    monto1 = check_divisas_montos(df, ['codigo', 'divisa_reclamo1', 'monto_reclamo1'])
    monto2 = check_divisas_montos(df, ['codigo', 'divisa_reclamo2', 'monto_reclamo2'])
    monto1.columns = ['codigo', 'divisa', 'monto']
    monto2.columns = ['codigo', 'divisa', 'monto']
    montos = concat([monto1, monto2])
    montos.dropna(subset='divisa', inplace=True, how='all')
    montos = montos.pivot_table(index='codigo', columns='divisa', values='monto', aggfunc='sum')
    montos = montos.rename({'PESO DOMINICANO': 'monto_reclamado_dop', 'U.S. DOLAR': 'monto_reclamado_usd'}, axis=1)
    return montos.reset_index()


def check_divisas_montos(df, columns):
    try:
        monto1 = df[columns]
    except KeyError:
        presentes = np.array([x in df.columns for x in columns])
        columnas = np.array(columns)
        df[columnas[~presentes]] = np.nan
        monto1 = df[columns]
    return monto1


def normalizes_currencies_creditos(df):
    monto1 = check_divisas_montos(df, ['codigo', 'divisa_credito1', 'monto_credito1'])
    monto2 = check_divisas_montos(df, ['codigo', 'divisa_credito2', 'monto_credito2'])
    monto1.columns = ['codigo', 'divisa', 'monto']
    monto2.columns = ['codigo', 'divisa', 'monto']
    montos = concat([monto1, monto2])
    montos.dropna(subset='divisa', inplace=True, how='all')
    montos = montos.pivot_table(index='codigo', columns='divisa', values='monto', aggfunc='sum')
    montos = montos.rename({'PESO DOMINICANO': 'monto_acreditado_dop', 'U.S. DOLAR': 'monto_acreditado_usd'}, axis=1)
    return montos.reset_index()


def main(start_date = None, end_date = None, odata_key='reclamos', added_columns=None):
    params = get_odata_parameters()
    format_label = params['format_label']
    nuevos_nombres = params[odata_key]['nuevos_nombres_columnas']
    if added_columns:
        od_added_columns = list(added_columns.keys())
        for key, val in added_columns.items():
            columnas.update(val)
            nuevos_nombres[key] = list(val.keys())[0]
    else:
        od_added_columns = None
    df = get_reclamos(start_date=start_date, end_date=end_date, od_added_columns=od_added_columns)
    clean = clean_data(df, format_label, nuevos_nombres)
    reclamados = normalizes_currencies_reclamos(clean)
    clean = merge(clean, reclamados, on='codigo', how='left')
    acreditados = normalizes_currencies_creditos(clean)
    clean = merge(clean, acreditados, on='codigo', how='left')
    for key, val in columnas.items():
        if val == 'datetime':
            if key == 'fecha_firma_crm':
                clean['fecha_firma'] = convert_time(clean[key])
            else:
                clean[key] = convert_time(clean[key])
    clean.reconsideracion = clean.reconsideracion.map({'Si': True, "No": False})
    clean.activa = clean.activa.map({'Active': True, "Inactive": False})
    clean['eif'] = clean.entidad.map(get_bank_names())
    clean['categoria'] = clean.tipo_reclamo.str.title().map(get_categories())
    clean['categoria_producto'] = clean.tipo_producto.map(get_categoria_producto())
    clean['canal'] = clean.canal.map(get_tipo_canal())
    # clean['duracion_firma'] = clean['etapa1']+clean['etapa2']+clean['etapa3']
    # clean['fecha_firma_crm'] = clean['fecha_creacion'] + clean['duracion_firma'].apply(lambda x: timedelta(minutes=x))
    try:
        clean = clean.reindex(columnas, axis=1)
    except Exception as e:
        print(e)
        # clean = clean[list(columnas.keys())[:-2]]
    return clean


columnas = {
    'codigo':str,
    'fecha_creacion':'datetime',
    'activa':bool,
    'fecha_verificacion':'datetime',
    'reconsideracion':bool,
    'eif':str,
    'categoria':str,
    'tipo_producto':str,
    'tipo_reclamo': str,
    'categoria_producto': str,
    'canal':str,
    'genero': str,
    'provincia': str,
    'ciudad': str,
    'respuesta_crm':str,
    'monto_reclamado_dop':float,
    'monto_reclamado_usd':float,
    'monto_acreditado_dop':float,
    'monto_acreditado_usd':float,
}

#%%
if __name__ == "__main__":
    main(**kwargs)
# df = main(fecha_limite='2022-04-30')
