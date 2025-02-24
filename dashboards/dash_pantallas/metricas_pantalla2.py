"""
Creado el 12/12/2023 a las 2:16 p. m.

@author: jacevedo
"""
"""
Creado el 11/11/2022 a las 1:49 p. m.

@author: jacevedo
"""

from datetime import date
from pandas.tseries.offsets import MonthEnd, MonthBegin
from general_tools import read_credentials
from requests_ntlm import HttpNtlmAuth
import requests as rs
import sql_tools
from sql_tools import query_reader
from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings

disable_warnings(InsecureRequestWarning)

CREDS = read_credentials('windows')
AUTH = HttpNtlmAuth(CREDS['user'], CREDS['pass'])
HEADER = {
    "OData-MaxVersion": "4.0",
    "OData-Version": "4.0",
    "Accept": "application/json",
    "Content-Type": "application/json; charset=utf-8",
}


def cantidad_infofinanciera():
    query = (
        "https://vmsvrcrm01.supernet.gov.do/Dynamics365-SIB/api/data/v9.0/"
        "new_procesodeinformacionfinancieras?"
        # "$select=_new_tipodeinformacionsolicitada_value"
        "$filter="
        "new_name ne null"
        " and _new_tipodeinformacionsolicitada_value ne 50286168-2c20-eb11-a2ea-005056a59c6f"
        " and Microsoft.Dynamics.CRM.OnOrAfter"
        f"(PropertyName='createdon',PropertyValue={START_DATE})"
        " and Microsoft.Dynamics.CRM.OnOrBefore"
        f"(PropertyName='createdon',PropertyValue={END_DATE})"
        "&"
        "$apply=aggregate($count as cantidad)"
    )
    response = rs.get(query, headers=HEADER, auth=AUTH, verify=False)
    return response.json()['value'][0]['cantidad']


def cantidad_central():
    query = (
        "https://vmsvrcrm01.supernet.gov.do/Dynamics365-SIB/api/data/v9.0/"
        "new_procesodeinformacionfinancieras?"
        # "$select=_new_tipodeinformacionsolicitada_value"
        "$filter="
        "new_name ne null"
        " and _new_tipodeinformacionsolicitada_value eq 50286168-2c20-eb11-a2ea-005056a59c6f"
        " and Microsoft.Dynamics.CRM.OnOrAfter"
        f"(PropertyName='createdon',PropertyValue={START_DATE})"
        " and Microsoft.Dynamics.CRM.OnOrBefore"
        f"(PropertyName='createdon',PropertyValue={END_DATE})"
        "&"
        "$apply=aggregate($count as cantidad)"
    )
    response = rs.get(query, headers=HEADER, auth=AUTH, verify=False)
    return response.json()['value'][0]['cantidad']

def cantidad_reclamos():
    query = (
        "https://vmsvrcrm01.supernet.gov.do/Dynamics365-SIB/api/data/v9.0/"
        "new_reclamacins?"
        "$filter="
        "new_codigo ne null"
        " and "
        "Microsoft.Dynamics.CRM.OnOrAfter"
        f"(PropertyName='createdon',PropertyValue={START_DATE})"
        " and Microsoft.Dynamics.CRM.OnOrBefore"
        f"(PropertyName='createdon',PropertyValue={END_DATE})"
        "&"
        "$apply=aggregate($count as cantidad)"
    )

    response = rs.get(query, headers=HEADER, auth=AUTH, verify=False)
    return response.json()['value'][0]['cantidad']


def get_salidas_reclamos():
    query = f"""
    select 
    count(CODIGO)
    from USRPROUSUARIO.RESULTADOS_RECLAMOS
    where ACTIVA = 1 and status_cierre = 'C'
    and FECHA_CIERRE between date '{START_DATE}' and date '{END_DATE_SQL}'
    """
    monto = sql_tools.query_reader(query)
    return monto.astype(int).values[0][0]


def get_salidas_info():
    query = f"""
    select 
    count(CODIGO)
    from USRPROUSUARIO.RESULTADOS_INFO
    where FECHA_CIERRE between date '{START_DATE}' and date '{END_DATE_SQL}'
    """
    monto = sql_tools.query_reader(query)
    return monto.astype(int).values[0][0]

def get_promedio_dias_claims():
    query = f"""
    select 
    avg(FECHA_CIERRE-FECHA_INICIO)
    from USRPROUSUARIO.RESULTADOS_RECLAMOS
    where ACTIVA = 1 and status_cierre = 'C'
    and FECHA_CIERRE between date '{START_DATE}' and date '{END_DATE_SQL}'
    """
    monto = sql_tools.query_reader(query)
    return monto.astype(float).values[0][0]

def get_casos_atiempo_reclamos():
    query = f"""
    select
    SUM(CASE WHEN floor(FECHA_CIERRE-FECHA_INICIO) <= 60 THEN 1 ELSE 0 END) / COUNT(codigo) AS total_records
    from USRPROUSUARIO.RESULTADOS_RECLAMOS
    where ACTIVA = 1 and status_cierre = 'C'
    and FECHA_CIERRE between date '{START_DATE}' and date '{END_DATE_SQL}' 
    """
    monto = sql_tools.query_reader(query)
    return monto.astype(float).values[0][0]


def get_promedio_dias_info():
    query = f"""
    select 
    avg(FECHA_CIERRE-FECHA_INICIO)
    from USRPROUSUARIO.RESULTADOS_INFO
    where FECHA_CIERRE between date '{START_DATE}' and date '{END_DATE_SQL}'
    """
    monto = sql_tools.query_reader(query)
    return monto.astype(float).values[0][0]

def get_casos_atiempo_info():
    query = f"""
    select
    SUM(CASE WHEN FECHA_CIERRE-FECHA_INICIO <= 60 THEN 1 ELSE 0 END) / COUNT(codigo) AS total_records
    from USRPROUSUARIO.RESULTADOS_INFO
    where FECHA_CIERRE between date '{START_DATE}' and date '{END_DATE_SQL}' 
    """
    monto = sql_tools.query_reader(query)
    return monto.astype(float).values[0][0]


def get_monto_total():
    query = f"""
    select 
    sum(monto_instruido_dop) + sum(monto_instruido_usd)*56 monto
    from USRPROUSUARIO.RESULTADOS_RECLAMOS
    where ACTIVA = 1 and status_cierre = 'C' and reconsideracion = 0 and favorabilidad = 'F'
    and FECHA_CIERRE between date '{START_DATE}' and date '{END_DATE_SQL}'
    """
    monto = sql_tools.query_reader(query)
    return monto.astype(float).values[0][0]


def get_favorabilidad():
    query = f"""
    select 
    FAVORABILIDAD, count(codigo) cantidad
    from USRPROUSUARIO.RESULTADOS_RECLAMOS
    where ACTIVA = 1 and status_cierre = 'C' and reconsideracion = 0 and favorabilidad in ('F', 'D')
    and FECHA_CIERRE between date '{START_DATE}' and date '{END_DATE_SQL}'
    group by FAVORABILIDAD
    """
    resultados = query_reader(query)
    favorabilidad = (resultados.cantidad / resultados.cantidad.sum())[0]
    return favorabilidad

#%%
START_DATE = (date.today() - MonthBegin()).date()
END_DATE_SQL = (date.today() + MonthBegin()).date()
END_DATE = (date.today() + MonthEnd()).date()
if date.today().day < 3:
    START_DATE = (START_DATE - MonthBegin()).date()
    END_DATE_SQL = (END_DATE_SQL - MonthBegin()).date()
    END_DATE = (END_DATE - MonthEnd()).date()

# print(START_DATE)
# print(END_DATE)
#
# START_DATE = '2022-07-01'
# END_DATE = '2022-12-31'
# END_DATE_SQL = '2023-01-01'

def main():
    metrics = dict(
        recibidas_claims=cantidad_reclamos(),
        salidas_claims = get_salidas_reclamos(),
        promedio_claims = get_promedio_dias_claims(),
        casos_claims = get_casos_atiempo_reclamos(),
        favorabilidad = get_favorabilidad(),
        monto = get_monto_total(),
        recibidas_info = cantidad_infofinanciera(),
        cantidad_central = cantidad_central(),
        salidas_info = get_salidas_info(),
        promedio_info = get_promedio_dias_info(),
        casos_info = get_casos_atiempo_info()
    )
    return metrics


# %%
if __name__ == '__main__':
    main()
