"""
Creado el 25/5/2022 a las 12:44 p. m.

@author: jacevedo
"""

import locale

import pandas as pd
from lectura_odata import get_info_financiera
from prousuario_tools import get_odata_parameters
from general_tools import convert_time

import traceback

locale.setlocale(locale.LC_ALL, 'es_DO.UTF-8')

mapa_tipo = {
    "Balances de Productos": "Balances",
    "Contrato y/o Pagaré": "Contrato+Pagaré",
    "Contrato, Movimientos e Histórico de Pagos": "Contrato+Mov+Hist",
    "Contrato, Movimientos, Histórico de Pagos, Tabla de Amortización": "Contrato+Mov+Hist+Tabla",
    "Copia (s) de Documento (s)": "Copia Doc.",
    "Documentos Relacionados a Diligencias Legales": "Diligencias Legales",
    "Estado (s) del producto": "Estado Producto",
    "Existencia de producto (s), Balance (s) y Movimiento (s)": "Existencia+Balance+Mov",
    "Histórico de Pagos": "Historico Pagos",
    "Motivo (s) Restricción (es) Sobre Producto (s)": "Restricción",
    "movimientos": "Movimientos",
    "Pólizas de Seguro y Documentos Complementarios": "Polizas Seguro",
    "Recibo (s) de Pago": "Recibos",
    "Relación Productos Financieros y Pólizas de Seguro": "Relacion Prod+Polizas",
    "Solicitud Productos Financieros": "Solicitud Productos",
    "Central de Riesgos": "Central de Riesgos"
}


columnas = {
    'codigo': str,
    'fecha_creacion': 'datetime',
    'activa': bool,
    'fecha_verificacion': 'datetime',
    'fecha_condicionada': 'datetime',
    'tipo_info_solicitada': str,
    'tipo_persona': str,
    'tipo_solicitud': str,
    'etapa_actual': str
}

def clean_data(df, format_label, nuevos_nombres):
    columnas_formateadas = df.columns[df.columns.str.contains(format_label)]
    for c in columnas_formateadas:
        if c in df.columns:
            if c in {
                'createdon@OData.Community.Display.V1.FormattedValue',
                'new_fechaderespuestadestatustramite@OData.Community.Display.V1.FormattedValue',
                'new_fechadondeseestableceadmisioncondicionada@OData.Community.Display.V1.FormattedValue'
            } or ('fecha' in c and '@OData.Community.Display.V1.FormattedValue' in c):
                df.drop(c, inplace=True, axis=1)
            else:
                df[c.split('@')[0]] = df[c]
                df.drop(c, inplace=True, axis=1)
    df.rename(nuevos_nombres, axis=1, inplace=True)
    for f in df.columns:
        if 'fecha' in f:
            try:
                df[f] = pd.to_datetime(df[f], format='ISO8601')
            except ValueError as e:
                print(f)
                print(f"Error occurred: {e.args}")
                # traceback.print_exc()
    return df

# start_date = '2020-08-01'
# end_date = '2022-12-01'
def main(start_date = None, end_date = None, include_central=False, added_columns=None, expansions=None):
    params = get_odata_parameters()
    format_label = params['format_label']
    droppable_columns = params['info_financiera']['droppable_columns']
    nuevos_nombres = params['info_financiera']['nuevos_nombres_columnas']
    if added_columns:
        od_added_columns = added_columns.keys()
        for key, val in added_columns.items():
            columnas.update(val)
            nuevos_nombres[key] = list(val.keys())[0]
    else:
        od_added_columns = None
    df = get_info_financiera(start_date=start_date, end_date=end_date, include_central=include_central, od_added_columns=od_added_columns, expansions=expansions)
    df.drop(droppable_columns, axis=1, inplace=True)
    clean = clean_data(df.copy(), format_label, nuevos_nombres)
    for c in clean.columns[clean.columns.str.contains('fecha')]:
        clean[c] = convert_time(clean[c])
    # clean['tipo_info_solicitada'] = clean.tipo_info_solicitada.str.title().map(mapa_tipo)
    return clean
# infos = main('2020-08-16')
# print('termino')

