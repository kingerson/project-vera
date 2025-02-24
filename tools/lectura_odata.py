"""
Creado el 20/5/2022 a las 5:34 p. m.

@author: jacevedo
"""

from datetime import date, timedelta

from prousuario_tools import get_odata, get_odata_parameters, odata_query_creator


def get_reclamos(start_date=None, end_date=None, od_added_columns=None):
    if not end_date:
        end_date = date.today().strftime('%Y-%m-%d')
    if not start_date:
        start_date = (date.today() - timedelta(14)).strftime('%Y-%m-%d')
    filters = (
        "new_codigo ne null"
        " and Microsoft.Dynamics.CRM.OnOrAfter"
        f"(PropertyName='createdon',PropertyValue={start_date})"
        " and Microsoft.Dynamics.CRM.OnOrBefore"
        f"(PropertyName='createdon',PropertyValue={end_date})"
    )
    params = get_odata_parameters()
    header = params['headers']
    reclamos = params['reclamos']
    query_cols = reclamos['query_cols']
    if od_added_columns:
        query_cols.extend(od_added_columns)
    # query_cols.append('new_etapaactiva')
    # query_cols.append('new_apellidos')
    tabla = reclamos['tabla']
    query = odata_query_creator(tabla, columns=query_cols, filters=filters)
    df = get_odata(query, header)
    return df


def get_info_financiera(start_date=None, end_date=None, include_central=False, od_added_columns=None, expansions=None):
    if not end_date:
        end_date = date.today().strftime('%Y-%m-%d')
    if not start_date:
        start_date = (date.today() - timedelta(14)).strftime('%Y-%m-%d')
    filtro_central = ' and _new_tipodeinformacionsolicitada_value ne 50286168-2c20-eb11-a2ea-005056a59c6f'
    filters = (
        "new_name ne null"
        f"{filtro_central}"
        " and Microsoft.Dynamics.CRM.OnOrAfter"
        f"(PropertyName='createdon',PropertyValue={start_date})"
        " and Microsoft.Dynamics.CRM.OnOrBefore"
        f"(PropertyName='createdon',PropertyValue={end_date})"
    )
    if include_central:
        filters = filters.replace(filtro_central, '')
    params = get_odata_parameters()
    header = params['headers']
    info_financiera = params['info_financiera']
    query_cols = info_financiera['query_cols']
    if od_added_columns:
        query_cols.extend(od_added_columns)
    tabla = info_financiera['tabla']
    query = odata_query_creator(tabla, columns=query_cols, filters=filters)
    if expansions:
        query = f"{query}&$expand={expansions}"
        print(query)
    df = get_odata(query, header)
    return df
