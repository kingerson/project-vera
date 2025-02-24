"""
Creado el 6/7/2022 a las 2:55 p. m.

@author: jacevedo
"""

import twitter_tools_v2 as tt
from win32com.shell import shell, shellcon
import pandas as pd
from general_tools import excel_formatter

eif_users = dict(
    popular = 'popularenlinea|popularatulado',
    reservas = 'banreservasrd',
    bhd = 'bhdleon|bancobhdleon|bancobhd',
    scotia = 'scotiabankrd'
)

FOLDER_NAME = START_DATE[:7].replace('-', '_')
DOCS_PATH = shell.SHGetFolderPath(0, shellcon.CSIDL_PERSONAL, None, 0)
FOLDER_PATH = f"{DOCS_PATH}/LaSuperTeEscucha/{FOLDER_NAME}/"

df = tweets.copy()

#%%

# df = tt.read_tweets('tweets_bancos_v2', start_date=START_DATE, end_date=END_DATE)
df.text = df.text.str.lower()
df.user_screen_name = df.user_screen_name.str.lower()
# user_filter = df.user_screen_name.str.contains(USERNAME_FILTER_STRING)
user_filter = df.user_screen_name.str.contains('victors10966516')
# user_filter = df.text.str.contains('rt @joeltorresdo')
# df = df[~user_filter]

sin_esquea = ~df.text.str.contains('emmanuelesquea|spereyrarojas')
df = df[~user_filter & sin_esquea]

#%%

topics = {
    'tarje': 'tarjetas',
    'reclam': 'reclamaciones',
    'servicio': 'servicio',
    'cajero': 'cajeros',
    'llama': 'llamadas',
}

relevant_cols = ['entidad', 'tema', 'sentimiento', 'user_screen_name', 'text', 'created_at', 'tweet_url']

frames = []
for k in eif_users.keys():
    user_string = eif_users[k]
    for t in topics.keys():
        filtro_eif = df.text.str.lower().str.contains(user_string)
        filtro_rt_eif = ~df.text.str.startswith('rt @' + '|rt @'.join(user_string.split('|')))
        filtro_propia_eif = ~df.user_screen_name.str.lower().str.contains(user_string)
        df_filtered = df[filtro_eif & filtro_rt_eif]
        filtro_termino = df_filtered.text.str.lower().str.contains(t)
        df_filtered = df_filtered[filtro_termino]
        try:
            df_filtered['tweet_url'] = df_filtered.apply(lambda x: f'https://www.twitter.com/{x.user_screen_name}/status/{x.id_str}', axis=1)
            df_filtered['tema'] = topics[t]
            df_filtered['entidad'] = k
            frames.append(df_filtered[relevant_cols])
        except:
            pass

#%%

relevant_cols = ['entidad', 'sentimiento', 'user_screen_name', 'text', 'created_at', 'tweet_url']

frames = []
for k in eif_users.keys():
    user_string = eif_users[k]
    filtro_eif = df.text.str.lower().str.contains(user_string)
    filtro_rt_eif = ~df.text.str.startswith('rt @' + '|rt @'.join(user_string.split('|')))
    filtro_propia_eif = ~df.user_screen_name.str.lower().str.contains(user_string)
    df_filtered = df[filtro_eif & filtro_rt_eif]
    # df_filtered = df_filtered[filtro_termino]
    df_filtered['tweet_url'] = df_filtered.apply(lambda x: f'https://www.twitter.com/{x.user_screen_name}/status/{x.id_str}', axis=1)
    # df_filtered['tema'] = topics[t]
    df_filtered['entidad'] = k
    frames.append(df_filtered[relevant_cols])


#%%

filename = f'{FOLDER_PATH}tuits_para_temas_{START_DATE}.xlsx'
# filename = f'{FOLDER_PATH}tuits_para_temas_reservas_{START_DATE}.xlsx'
result = pd.concat(frames)

with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
    excel_formatter(writer, result, 'Temas Mas Frecuentes')


# print('Cantidad:', len(df_filtered.text.values))
# try:
#     for v in df_filtered.text.values:
#         print(v)
#         print('-' * 30)
#     print(df_filtered.user_screen_name.value_counts())
# except ValueError:
#     for a, b, c in zip(df_filtered.index,df_filtered.user_screen_name,  df_filtered.text.values):
#         print(a, b, c)




#%%

eif_users = dict(
    banesco = 'banescord',
)

topics = {
    'tarje': 'tarjetas',
    'reclam': 'reclamaciones',
    'servicio': 'servicio',
    'cajero': 'cajeros',
    'llama': 'llamadas',
}

relevant_cols = ['tema', 'user_screen_name', 'text', 'created_at', 'tweet_url']

frames = []
for k in eif_users.keys():
    user_string = eif_users[k]
    for t in topics.keys():
        filtro_eif = df.text.str.lower().str.contains(user_string)
        filtro_rt_eif = ~df.text.str.startswith('rt @' + '|rt @'.join(user_string.split('|')))
        filtro_propia_eif = ~df.user_screen_name.str.lower().str.contains(user_string)
        df_filtered = df[filtro_eif & filtro_rt_eif]
        filtro_termino = df_filtered.text.str.lower().str.contains(t)
        df_filtered = df_filtered[filtro_termino]
        try:
            df_filtered['tweet_url'] = df_filtered.apply(lambda x: f'https://www.twitter.com/{x.user_screen_name}/status/{x.id_str}', axis=1)
            df_filtered['tema'] = topics[t]
            df_filtered['entidad'] = k
            frames.append(df_filtered[relevant_cols])
        except:
            pass

#%%


filename = f'{FOLDER_PATH}tuits_para_temas_{START_DATE}.xlsx'
filename = f'temas_banesco_2024.xlsx'
# filename = f'{FOLDER_PATH}tuits_para_temas_reservas_{START_DATE}.xlsx'
result = pd.concat(frames)

with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
    excel_formatter(writer, result, 'Temas Mas Frecuentes')