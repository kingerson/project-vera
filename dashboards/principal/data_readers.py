"""
Creado el 27/6/2022 a las 4:48 p. m.

@author: jacevedo
"""
import prousuario_tools as pt
import reclamos_reading
import infofinanciera_reading
from pandas import merge, to_datetime
from datetime import timedelta


def get_data(reader, start_date, end_date, **kwargs):
    data = reader.main(start_date=start_date, end_date=end_date)
    # print(data.head())
    data = pt.get_period_data(data, 'fecha_creacion', start_date, end_date)
    if 'tabla' in kwargs.keys():
        results = pt.get_results(start_date, end_date, tabla=kwargs['tabla'])
    else:
        results = pt.get_results(start_date, end_date)
    mezcla = merge(data, results, on='codigo', how='outer', suffixes=(None, '_result')).to_dict('records')
    return mezcla


def main(tipo, start_date, end_date):
    end_date = (to_datetime(end_date) + timedelta(1)).strftime('%Y-%m-%d')
    if tipo == "reclamos":
        data = get_data(reclamos_reading, start_date, end_date)
        return data
    elif tipo == "info":
        data = get_data(infofinanciera_reading, start_date, end_date, tabla='RESULTADOS_INFO')
        return data


