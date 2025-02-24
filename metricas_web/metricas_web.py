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
    where ACTIVA = 1 and status_cierre = 'C' and favorabilidad in ('F', 'D')
    and FECHA_CIERRE between date '{START_DATE}' and date '{END_DATE_SQL}'
    group by FAVORABILIDAD
    """
    resultados = query_reader(query)
    favorabilidad = (resultados.cantidad / resultados.cantidad.sum())[0]
    return favorabilidad


START_DATE = '2020-08-16'
END_DATE = (date.today() - MonthEnd()).date()
# END_DATE = date(2024,3,31)
END_DATE_SQL = (date.today() - MonthBegin()).date()
# END_DATE_SQL = date(2024,3,31)


def main():
    print(f"""
    Al {END_DATE.strftime('%d de %b')}, lás métricas de la gestión son las siguientes:
    
    Cantidad de solicitudes de IF: {cantidad_infofinanciera():,}
    Cantidad de reclamaciones: {cantidad_reclamos():,}
    Monto total dispuesto a acreditar: ${get_monto_total():,.2f}
    Favorabilidad de los resultados: {get_favorabilidad():.1%}
    """
          )

#%%
if __name__ == '__main__':
    main()
