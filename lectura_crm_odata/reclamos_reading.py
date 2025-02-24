"""
Creado el 24/5/2022 a las 6:51 p. m.

@author: jacevedo
"""

import locale
from datetime import date, timedelta
from lectura_crm_odata.lectura_odata import get_reclamos
from tools.general_tools import convert_time
from prousuario_tools import get_odata_parameters, get_bank_names, get_categories

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
                'new_montoacreditado2@OData.Community.Display.V1.FormattedValue'
            }:
                df.drop(c, inplace=True, axis=1)
            else:
                df[c.split('@')[0]] = df[c]
                df.drop(c, inplace=True, axis=1)
    df.rename(nuevos_nombres, axis=1, inplace=True)
    return df


def main(fecha_limite: str = None):
    df = get_reclamos(fecha_limite=fecha_limite)
    params = get_odata_parameters()
    format_label = params['format_label']
    droppable_columns = params['entradas']['reclamos']['droppable_columns'][:-1]
    nuevos_nombres = params['entradas']['reclamos']['nuevos_nombres_columnas']
    df.drop(droppable_columns, axis=1, inplace=True)
    clean = clean_data(df, format_label, nuevos_nombres)
    clean.fecha_creacion = convert_time(clean.fecha_creacion)
    clean.fecha_verificacion = convert_time(clean.fecha_verificacion)
    clean.reconsideracion = clean.reconsideracion.map({'Si': True, "No": False})
    clean.activa = clean.activa.map({'Active': True, "Inactive": False})
    clean['eif'] = clean.entidad.map(get_bank_names())
    clean['categoria'] = clean.tipo_reclamo.str.title().map(get_categories())
    clean.drop(['entidad', 'tipo_reclamo'], axis=1, inplace=True)
    return clean

# df = main(fecha_limite='2021-04-25')