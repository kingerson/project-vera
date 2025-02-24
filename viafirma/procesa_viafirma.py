"""
Creado el 30/5/2022 a las 4:57 p. m.

@author: jacevedo
"""
# import sys
# sys.path.append(r'C:\Users\jacevedo\Documents\ProUsuario Project\tools')
import sql_tools
from general_tools import json_reader
from sqlalchemy.types import String
from pandas import to_datetime


# %%

def sub_24(x):
    hour = x.split('2022')[-1][1:4]
    if hour == '24:':
        # print(x[-5:-3])
        x = x.replace(hour, '00:')
    return x


def get_last_date():
    query = '''
    select * from FIRMAS inner join(
        select max(fecha_firma) ultima_fecha from firmas
    ) b on b.ultima_fecha = fecha_firma'''

    last_record = (
        sql_tools.query_reader(query, mode='many')
        .ultima_fecha
        .drop_duplicates()[0]
    )
    return last_record


def convert_time(series):
    series = to_datetime(series, format='%d/%m/%Y %H:%M')
    series = (
        series
        .dt.tz_localize(tz='UTC')
        .dt.tz_convert(tz='America/Santo_Domingo')
        .dt.tz_localize(None)
    )
    return series


def main(df):
    df.columns = df.columns.str.lower()
    columnas_fecha = {
        'fecha de envío': 'fecha_envio',
        'fecha de modificación': 'fecha_firma'
    }
    df.rename(columnas_fecha, axis=1, inplace=True)
    cols = ['csv', 'remitente', 'asunto', 'fecha_envio', 'fecha_firma', 'estado']
    df = df[cols].copy()
    df.remitente = df.remitente.str.replace('[\s]+', ' ')
    df.fecha_firma = df.fecha_firma.apply(sub_24)
    df.fecha_envio = df.fecha_envio.apply(sub_24)
    df.fecha_firma = convert_time(df.fecha_firma)
    df.fecha_envio = convert_time(df.fecha_firma)
    last_date = get_last_date()
    mas_recientes = df.fecha_firma > last_date
    # mas_recientes = df.fecha_firma > '2022-05-25'
    df = df[mas_recientes]
    proceso_mapa = json_reader('mapa_viafirma.json')
    # proceso_mapa = json_reader(r'C:\Users\jacevedo\Documents\ProUsuario Project\viafirma\mapa_viafirma.json')
    df['tipo'] = df.remitente.map(proceso_mapa)
    finalizadas = df.estado == "Finalizada"
    sin_recursos = ~df.asunto.str.contains('Notificación Recurso')
    df = df[finalizadas & sin_recursos].reset_index(drop=True)
    print(df.head())
    print(df.shape)
    with sql_tools.conn_creator() as conn:
        df.to_sql('firmas', conn, index=False, dtype=dtypes, if_exists='append')
        # df.to_sql('firmas', conn, index=False, dtype=dtypes, if_exists='replace')


dtypes = {
    'csv': String(20),
    'remitente': String(100),
    'asunto': String(256),
    'estado': String(20),
    'tipo': String(20)
}

#%%

if __name__ == "__main__":
    main()