# -*- coding: utf-8 -*-
"""
Created on Tue Dec  1 11:51:11 2020

@author: jacevedo
"""

from json import load
from pathlib import Path

import pandas as pd
from yaml import safe_load, safe_dump
from timeit import default_timer as timer
from pandas import to_datetime
from datetime import datetime


def json_reader(json_file):
    """Lee un archivo json con codificación Unicode"""
    with open(json_file, encoding='utf-8') as f:
        data = load(f)
    return data


from pandas.tseries.offsets import MonthEnd

def update_credentials(key, val):
    today_str = datetime.today().strftime("%Y_%m_%d %H_%M")
    creds_file = Path(__file__).parent.parent.parent / 'credentials/credenciales.yaml'
    backup_file = Path(__file__).parent.parent.parent / f'credentials/cred_backups_{today_str}.yaml'
    with creds_file.open() as stream:
        credentials = safe_load(stream)
    with backup_file.open('w') as f:
        safe_dump(credentials, f)
    credentials[key] = val
    with creds_file.open('w') as f:
        safe_dump(credentials, f)
    print('Credenciales actualizadas')


def read_credentials(key=None, verbose=False):
    """Lee credenciales de la fuente"""
    creds_file = Path(__file__).parent.parent.parent / 'credentials/credenciales.yaml'
    with creds_file.open() as stream:
        credentials = safe_load(stream)
    if key:
        credentials = credentials[key]
    if verbose:
        message = f'Credenciales de {key}' if key else 'Todas las credenciales'
        print(message)
    return credentials


def custom_timer(function):
    """Temporizador de funciones para pruebas"""
    def wrapper(*args, **kwargs):
        start_time = timer()
        result = function(*args, **kwargs)
        elapsed_time = timer() - start_time
        print(f'Se tomo {elapsed_time:.3f} segundos realizar {function.__name__}')
        return result
    return wrapper


def convert_time(series, formato=None):
    """Convierte Serie pandas a tipo datetime, y si tiene información
    de zona horaria, la convierte a la hora local"""
    series = to_datetime(series, format=formato)
    if series.dt.tz:
        series = series.dt.tz_convert('America/Santo_Domingo').dt.tz_localize(None)
    return series

# def convert_time(series):
#     """Convierte Serie pandas a tipo datetime, y si tiene información
#     de zona horaria, la convierte a la hora local"""
#     series = to_datetime(series)
#     if series.tz:
#         series = (
#             series
#             .tz_convert(tz='America/Santo_Domingo')
#             .tz_localize(None)
#         )
#         return series
#     else:
#         return series


def peaks_labeler(series):
    """Crea una lista de etiquetas para ser usada en la gráfica de modo
    que solo se reflejen los puntos que son picos"""
    peaks = [None] * len(series)
    peaks[0] = series[0]
    peaks[-1] = series[-1]
    for i in range(1, len(series)-1):
        if series[i] > series[i-1] and series[i] > series[i+1]:
            peaks[i] = series[i]
    return peaks


def na_percent(x):
    total = len(x)
    try:
        result = round(x.isna().value_counts()[True] / total*100, 2)
    except KeyError:
        result = 0
        pass
    return result


def excel_formatter(writer, sheet, sheet_name, reset_index=False, print_columns=False):
    for f in sheet.columns:
        if 'fecha' in f:
            sheet[f] = pd.to_datetime(sheet[f])
            sheet[f] = sheet[f].dt.date
    sheet.columns = sheet.columns.str.replace('_', ' ').str.title()
    if reset_index:
        sheet.reset_index(inplace=True)
    sheet.to_excel(writer, sheet_name=sheet_name, index=False)
    workbook = writer.book
    worksheet = writer.sheets[sheet_name]
    worksheet.autofilter(0, 0, sheet.shape[0], sheet.shape[1])
    # worksheet.hide_gridlines(2)
    format_title = workbook.add_format(
        {'bold': True, 'text_wrap': True, 'valign': 'vcenter', 'align': 'center', 'bg_color': '#203764',
         'font_color': 'white'})
    worksheet.autofit()
    if print_columns:
        print(sheet.columns)
    for col_num, data in enumerate(sheet.columns):
        worksheet.write(0, col_num, data, format_title)

import socket
import psutil

def get_ip_address():
    ip_addresses = {}
    lista_ip = psutil.net_if_addrs()
    for address in lista_ip['Ethernet']:
        # print(address)
        if address.family.name == 'AF_INET':
            ip_addresses['Ethernet'] = address.address
    # for interface_name, interface_addresses in psutil.net_if_addrs().items():
    #     print(interface_name)
    #     print(interface_addresses)
    #     for address in psutil.net_if_addrs()['Ethernet']:
    #     #     if str(address.family) == 'AddressFamily.AF_INET':
    #             ip_addresses[interface_name] = address.address
    try:
        print(f'IP Ethernet encontrada: {ip_addresses["Ethernet"]}')
        return ip_addresses['Ethernet']
    except KeyError:
        print('No se encntró una IP apropiada')

# # Use this function to get all IP addresses
# ip_addresses = get_ip_address()
#
# # Filter or select the IP address based on your criteria (e.g., non-virtual, specific interface name)
# for interface_name, ip_address in ip_addresses.items():
#     print(f"{interface_name}: {ip_address}")
