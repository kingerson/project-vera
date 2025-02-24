"""
Creado el 29/7/2024 a las 3:04 PM

@author: jacevedo
"""

import requests as rs

base_url = 'http://sbs1srv358:9001/api/v1/'
historial = 'historialgeneral'
report = 'report/getresume-creditconsult?identificationCard'
headers = {
    'accept': 'text/plain'
}
user_id = '001-1391792-6'
response = rs.post(base_url + historial + '/' + user_id, headers = headers)
response.status_code
#%%

from sql_tools import query_reader
query = 'select * from USRPROUSUARIO.ID'
df = query_reader(query, mode='all')

#%%
def find_score(user_id):
    try:
        response = rs.get(base_url + historial + '/' + user_id, headers = headers)
        result= response.json()['peorClasificacion']
    except:
        result= None
    return result

def find_score_report(user_id):
    try:
        response = rs.get(base_url + report + '=' + user_id, headers = headers)
        result= response.json()
    except:
        result= None
    return result

#%%

df['score'] = df.cedula.apply(find_score)

lel = find_score_report('402-0061823-5')

rs.post(base_url + historial + '/' + '001-1391792-6', headers = headers)

#%%

df['score'] = None
batch_size = 10000

for x in range(0,len(df),batch_size):
    try:
        print(x, x+batch_size)
        df.loc[x:x+batch_size, 'score'] = df.loc[x:x+batch_size, 'cedula'].apply(find_score)
    except:
        print(f'it stopped at {x}')

#%%

rs.get(base_url + 'CalificationIndicator')