import sql_tools
from general_tools import json_reader, read_credentials
from pandas import DataFrame
from requests_ntlm import HttpNtlmAuth
import requests as rs
from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings
disable_warnings(InsecureRequestWarning)
import pandas as pd
from pathlib import Path

# base_path = (Path(__file__).parent.parent / 'dicts').as_posix()

# base_path = (Path(__file__).parent / 'dicts').as_posix()

# base_path = (Path().absolute() / 'dicts').as_posix()

# base_path = "../dicts"
# import os
# base_path = os.path.abspath('./dicts')
# base_path = 'C:/Users/jacevedo/OneDrive - Superintendencia de Bancos de la Republica Dominicana/Documents/ProUsuario Project/dicts'
# base_path = 'C:/Users/jacevedo/OneDrive - Superintendencia de Bancos de la Republica Dominicana/Documents/ProUsuario Project/dicts'

base_path = Path(__file__).parent.parent / 'dicts'


def get_odata(query, header):
    """ Usa las credenciales de windows para conectarse al API OData del
    CRM y entregar un dataframe basado en el query definido.
    
    Parametros:
    query - El query a correr.
    headers = Los headers necesarios para el CRM.
    """
    mas_5000 = True
    resultados = []
    creds = read_credentials(key='windows')
    auth = HttpNtlmAuth(creds['user'], creds['pass'])
    while mas_5000:
        response = rs.get(query, headers=header, auth=auth, verify=False)
        if response.status_code == 200:
            df = pd.json_normalize(response.json()['value'], max_level=10).iloc[:, 1:]
            resultados.append(df)
            if len(df) < 5000:
                mas_5000 = False
            else:
                query = response.json()['@odata.nextLink']
        else:
            print(response.text)
            mas_5000 = False
    if len(resultados) > 0:
        df = pd.concat(resultados).reset_index(drop=True)
        return df
    else:
        print('Sin resultados')


def get_tipos_viafirma():
    """Entrega los tipos de respuestas posibles en Viafirma y sus implicaciones de aprobación."""
    path = base_path / 'tipos_viafirma.json'
    result = json_reader(path)
    return result

def get_dash_port(dash):
    """Entrega los tipos de respuestas posibles en Viafirma y sus implicaciones de aprobación."""
    path = base_path / 'dash_ports.json'
    result = json_reader(path)[dash]
    return result


def get_odata_parameters():
    """Entrega los parametros necesarios para hacer consultas ODATA"""
    path = base_path / 'odata_parameters.json'
    parameters = json_reader(path)
    return parameters


def get_bank_names():
    """Entrega los nombres cortos para cada entidad mapeados
    a los nombres encontrados en el CRM post Abril 2021
    """
    path = base_path / 'nombres_cortos.json'
    bank_names = json_reader(path)
    return bank_names


def get_sb_colors():
    """Entrega los colores oficiales de la SB"""
    path = base_path / 'colores_sb.json'
    bank_names = json_reader(path)
    return bank_names


def get_bank_reverse_users(path=base_path / 'bank_reverse_users.json'):
    """Entrega los nombres cortos de cada entidad mapeados
    a los usuarios de Twitter de cada una."""
    data = json_reader(path)
    return data

def get_bank_users(path=base_path / 'bank_users.json'):
    """Entrega los nombres cortos de cada entidad mapeados
    a los usuarios de Twitter de cada una."""
    data = json_reader(path)
    return data


def get_bank_codes(path=base_path / 'bank_codes.json'):
    """Entrega los codigos asignados por la SB para cada entidad
    mapeados a los nombres cortos"""
    data = json_reader(path)
    return data


def get_bank_colors(path=base_path / 'bank_colors.json'):
    """Entrega los colores para cada entidad mapeados a los nombres cortos"""
    data = json_reader(path)
    return data


def get_category_colors(path=base_path / 'category_colors.json'):
    """Entrega los colores para cada entidad mapeados a los nombres cortos"""
    data = json_reader(path)
    return data


def get_product_names(path=base_path / 'product_names.json'):
    """Entrega los nombres de producto"""
    data = json_reader(path)
    return data

def get_categoria_producto(path=base_path / 'categorias_productos.json'):
    """Entrega los nombres de producto"""
    data = json_reader(path)
    return data

def get_tipo_canal(path=base_path / 'tipo_canal.json'):
    """Entrega los nombres de producto"""
    data = json_reader(path)
    return data


def get_categories(path=base_path / 'categorias_reclamos.json'):
    """Entrega las categorias de reclamos mapeados a los tipos
     de reclamos encontrados en el CRM post Abril 2021"""
    data = json_reader(path)
    return data


def get_tipos_long_names(path=base_path / 'tipos_names.json'):
    """Entrega los nombres cortos de los tipos de reclamos 
    mapeados a los tipos encontrados en el CRM post Abril 2021"""
    data = json_reader(path)
    return data


def get_tipo_respuesta(path=base_path / 'tipo_respuestas.json'):
    """Entrega los tipos de respuesta"""
    data = json_reader(path)
    return data


def claims_sql_reader(target_cols, conn, start_date, end_date):
    """
    Lee la base de datos de reclamaciones y extrae la columna relevante para conteos
    """
    query = '''SELECT
    CreatedOn, new_codigo'''+target_cols+'''
    FROM new_reclamacin
    WHERE CreatedOn > \''''+start_date+'\' and CreatedOn < \''+end_date+'\''
    result = conn.execute(query)
    df = DataFrame(result.fetchall())
    return df


def odata_query_creator(table: str, columns: list = None , filters: str = None):
    query = (
        "https://vmsvrcrm01.supernet.gov.do/Dynamics365-SIB/api/data/v9.0/"
        f"{table}?"
    )
    if columns:
        query += (
        "$select="
        f"{','.join(columns)}")
    if filters:
        query += (
        "&$filter="
        f"{filters}"
        )
    return query

# def tweet_rank_grapher(data, color_map=None):
#     """
#     Grafica las EIF por su rango de cantidad de menciones semanales
#     """
#     fig = px.line(
#         data,
#         x='created_at',
#         y='rank',
#         color='eif',
#         text='count',
#         height=600,
#         width=900,
#         color_discrete_map=color_map,
#         template='xgridoff'
#         )
#     fig.update_traces(
#         mode='lines+markers',
#         marker=dict(size=20),
#         hovertemplate=
#         "Cantidad: %{text}<br>"
#         )
#     fig.update_layout(
#         # hovermode='closest',
#         yaxis=dict(
#             tickmode='array',
#             tickvals = [1,2,3,4,5],
#             autorange='reversed',
#             title=None
#         ),
#         xaxis=dict(
#             title=None
#         )
#         )
#     plot(fig)


# print(get_sb_colors())
def get_results(start_date, end_date, tabla='RESULTADOS_RECLAMOS'):
    query = (f"select * from {tabla}"
             f" where"
             f" FECHA_CIERRE >= to_DATE('{start_date}', 'yyyy-mm-dd')"
             f" and FECHA_CIERRE <= to_DATE('{end_date}', 'yyyy-mm-dd')"
             )
    result = sql_tools.query_reader(query, mode='all')
    return result


def get_period_data(df, date_col, start_date, end_date, include_last=True):
    inicio = df[date_col] >= start_date
    final = df[date_col] <= end_date
    if not include_last:
        final = df[date_col] < end_date
    result = df[inicio & final]
    return result
