"""
Creado el 18/6/2023 a las 3:07 p. m.

@author: jacevedo
"""
import locale
from datetime import datetime

from general_tools import convert_time
from lectura_odata import get_odata_parameters, get_odata

locale.setlocale(locale.LC_ALL, 'es_DO.UTF-8')

etapas_map = {
    1: "recepcion",
    2: "analisis",
    3: "revision_tecnica",
    4: "revision_legal",
    5: "aprobacion",
    6: "notificacion",
}

etapas_duration_map = {
    1: 1,
    2: 32,
    3: 3,
    4: 3,
    5: 2,
    6: 2,
}

## auxiliary materials

params = get_odata_parameters()
headers = params['headers']
format_label = params['format_label']

mapa_columnas = {
    "_new_informacionfinanciera_value@OData.Community.Display.V1.FormattedValue": "codigo",
    "new_etapafaseinformacionfinanciera@OData.Community.Display.V1.FormattedValue": "nombre_etapa",
    "new_etapafaseinformacionfinanciera": "orden_etapa",
    "new_fechahoraentradafase": "inicio_etapa",
    "new_fechahorasalidafase": "cierre_etapa",
    "_modifiedby_value": "modificado",
    "new_InformacionFinanciera._new_tipodeinformacionsolicitada_value@OData.Community.Display.V1.FormattedValue":'tipo_info',
    "new_InformacionFinanciera._new_analista_value@OData.Community.Display.V1.FormattedValue":'analista'
}

# new_tiempoporetapas

query_cierres = (
    "https://vmsvrcrm01.supernet.gov.do/Dynamics365-SIB/api/data/v9.0/"
    "new_tiempoporetapas?"
    "$select="
    "_new_informacionfinanciera_value, new_etapafaseinformacionfinanciera"
    ",new_fechahoraentradafase, new_fechahorasalidafase"
    ",_modifiedby_value"
    "&"
    "$filter=Microsoft.Dynamics.CRM.LastXDays(PropertyName='new_fechahorasalidafase',PropertyValue=7)"
    " and new_etapafaseinformacionfinanciera ne null"
    " and new_etapafaseinformacionfinanciera ne 6"
    " and _new_informacionfinanciera_value ne null"
    "&"
    "$expand=new_InformacionFinanciera($select=_new_tipodeinformacionsolicitada_value, _new_analista_value)"

)

#%%
query_pendientes = (
    "https://vmsvrcrm01.supernet.gov.do/Dynamics365-SIB/api/data/v9.0/"
    "new_tiempoporetapas?"
    "$select="
    "_new_informacionfinanciera_value, new_etapafaseinformacionfinanciera"
    ",new_fechahoraentradafase, new_fechahorasalidafase"
    ",_modifiedby_value"
    "&"
    "$filter=Microsoft.Dynamics.CRM.LastXDays(PropertyName='new_fechahoraentradafase',PropertyValue=7)"
    " and new_fechahorasalidafase eq null"
    " and new_etapafaseinformacionfinanciera ne null"
    " and new_etapafaseinformacionfinanciera ne 6"
    " and _new_informacionfinanciera_value ne null"
    "&"
    "$expand=new_InformacionFinanciera($select=_new_tipodeinformacionsolicitada_value, _new_analista_value)"
)

def consolida_etapas(df):
    agrupado = df.groupby(['codigo', 'analista', 'tipo_info', 'orden_etapa', 'nombre_etapa'])
    # result = (agrupado.sum()/86400).duracion_etapa.reset_index()
    result = (agrupado.duracion_etapa.sum()/86400).reset_index()
    result.insert(3, 'inicio_etapa',agrupado.min().inicio_etapa.values)
    result.insert(4, 'cierre_etapa',agrupado.max().cierre_etapa.values)
    return result

def get_etapas(tipo='pendientes', dias=14):
    query = query_pendientes
    if tipo == 'cierres':
        query = query_cierres
    if dias != 14:
        query = query.replace('PropertyValue=7', f'PropertyValue={dias}')
    df = get_odata(query, headers)
    df = df[mapa_columnas.keys()]
    df.columns = df.columns.map(mapa_columnas)
    df['inicio_etapa'] = convert_time(df['inicio_etapa'])
    df['cierre_etapa'] = convert_time(df['cierre_etapa'])
    c = 'orden_etapa'
    df['nombre_etapa'] = df[c].map(etapas_map)
    filtro_central = df['tipo_info'] != 'Central de Riesgos'
    # filtro_central = df['tipo_info'] == 'Central de Riesgos'
    df = df[filtro_central].reset_index(drop=True)
    if query == query_pendientes:
        df['cierre_etapa'] = datetime.today()
    df.loc[df.cierre_etapa.isna(), 'cierre_etapa'] = datetime.today()
    df['duracion_etapa'] = (df.cierre_etapa - df.inicio_etapa).dt.total_seconds()
    consolidado = consolida_etapas(df)
    consolidado['duracion_estandar'] = consolidado.orden_etapa.map(etapas_duration_map)
    consolidado['proporcion_duracion'] = consolidado.duracion_etapa / consolidado.duracion_estandar
    return consolidado
