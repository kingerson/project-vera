"""
Creado el 15/6/2022 a las 4:12 p. m.

@author: jacevedo
"""
import pandas as pd
import infofinanciera_reading
import plotly.express as px
from plotly.offline import plot

def get_firmas_info():
    query = "select * from FIRMAS where tipo = 'info_financiera'"
    df = sql_tools.query_reader(query, mode='all')
    return df


def check_sign(x, firmas):
    try:
        result = firmas.loc[firmas.asunto.str.contains(x), 'fecha_firma'].values[-1]
    except IndexError:
        # print(e)
        result = None
    return result


def check_response(x, firmas):
    try:
        result = firmas.loc[firmas.asunto.str.contains(x), 'tipo_respuesta'].values[-1]
    except IndexError:
        result = None
    return result


def assign_response(asuntos, tipos):
    tipo_respuesta = pd.Series(None, index=asuntos.index, dtype=object)
    for tipo in tipos.keys():
        tipo_respuesta.loc[asuntos.str.contains(tipo)] = tipo
    favorabilidad = tipo_respuesta.map(tipos)
    return tipo_respuesta, favorabilidad
#%%
filepath = r"C:\Users\jacevedo\Documents\Métricas Transparencia\informacion_financiera\matriz_IF_junio_2022.xlsx"
df = pd.read_excel(filepath, sheet_name='Consolidado Revisado')


#%%
infos = infofinanciera_reading.main('2020-01-01')
no_central = infos.tipo_info_solicitada != 'Central de Riesgos'
infos = infos[no_central].reset_index(drop=True)
cierres = df[['codigo', 'fecha_cierre']]
mezcla = pd.merge(infos, cierres, on='codigo')

#%%

# infos['fecha_cierre'] = \




#%%
# firmas_info = get_firmas_info()
# tipos_viafirma = get_tipos_viafirma()['info_financiera']
# firmas_info['tipo_respuesta'], firmas_info['favorabilidad'] = assign_response(firmas_info.asunto, tipos_viafirma)
# infos['fecha_cierre'] = infos['codigo'].apply(lambda x: check_sign(x[-6:], firmas_info))
# infos['tipo_respuesta'] = infos['codigo'].apply(lambda x: check_response(x[-6:], firmas_info))
# infos['aprobacion'] = infos['tipo_respuesta'].map(tipos_viafirma)
# infos.dropna(subset='fecha_cierre').T

#%%
mezcla['yearmonth'] = mezcla.fecha_creacion.dt.strftime('%Y-%m')
mezcla['no_close'] = mezcla.fecha_cierre.isna()
abiertas = mezcla[mezcla.no_close].groupby('yearmonth').size().reset_index()

mezcla.loc[mezcla.no_close, 'fecha_cierre'] = mezcla.loc[mezcla.no_close, 'codigo'].apply(lambda x: check_sign(x[-6:], firmas_info))
mezcla['tipo_informe'] = mezcla['codigo'].apply(lambda x: check_response(x[-6:], firmas_info))
mezcla['aprobacion'] = mezcla['tipo_informe'].map(tipos_viafirma)



#%%

mezcla = mezcla.dropna(subset=['fecha_cierre']).reset_index(drop=True)
resultados = mezcla[['codigo', 'fecha_cierre', 'tipo_informe', 'aprobacion']]
# resultados.tipo_informe = resultados.tipo_informe.fillna('')
# resultados.aprobacion = resultados.aprobacion.fillna('')

dtypes = {
    'codigo': String(12),
    'tipo_informe': String(50),
    'aprobacion': String(25)
    }

#%%
conn = sql_tools.conn_creator()
resultados.to_sql('resultados_info', conn, index=False, dtype=dtypes, if_exists='append')
conn.close()


#%%
fig = px.bar(abiertas, x='yearmonth', y=0)
plot(fig)

#%%

query = "select * from RESULTADOS_INFO"
new_results = sql_tools.query_reader(query, mode='all')
new_results

#%%
data = new_results.fecha_cierre.dt.strftime('%Y-%m').value_counts()
fig = px.bar(data)
plot(fig)