from twitter_tools_v1 import read_tweets
from pathlib import Path
from prousuario_tools import get_bank_users
import pandas as pd

DBASE = r"C:\Users\jacevedo\OneDrive - Superintendencia de Bancos de la Republica Dominicana\Documents\ProUsuario Project\databases\tweets_bancos.db"
START_DATE = '2022-05-01'
CURRENT_MONTH = START_DATE[:7].replace('-', '_')
FOLDER_NAME = f"C:\\Users\\jacevedo\\OneDrive - Superintendencia de Bancos de la Republica Dominicana\\Documents\\LaSuperTeEscucha\\{CURRENT_MONTH}\\"
END_DATE = '2022-06-01'
SAMPLE_SIZE = 100000
PROUSUARIO_USERS_STRING = 'prousuariord|superdebancosrd|sbfernandezw'
BANK_USERS = get_bank_users()

def count_prousuario_mentions(df):
    prousuario_counts = {}
    for b in BANK_USERS:
        bank = BANK_USERS[b]
        bank_filter = df.text.str.contains(b)
        prousuario_filter = df.text.str.contains(PROUSUARIO_USERS_STRING)
        count = len(df[bank_filter & prousuario_filter])
        if bank not in prousuario_counts:
            prousuario_counts[bank] = count
        else:
            prousuario_counts[bank] += count
    return pd.Series(prousuario_counts)


def main():
    df = read_tweets(
        dbase=DBASE, sample_size=SAMPLE_SIZE,
        date_limit=1, start_date=START_DATE, end_date=END_DATE
    )
    df = df.drop_duplicates(subset=['id_str'])
    df.text = df.text.str.lower()
    prousuario_counts = count_prousuario_mentions(df)
    prousuario_counts.to_excel(f"{FOLDER_NAME}prousuario_counts_{CURRENT_MONTH}.xlsx")



df.to_excel(f'{FOLDER_NAME}data_{CURRENT_MONTH}.xlsx')
# BANK_USERS = [f'@{u}' for u in USERNAME_FILTER_STRING.split('|')][:-3]


# print(df.columns)
# df
# .sort_values(by=['id_str', 'created_at', 'interactions'],ignore_index=True)
# .drop_duplicates(subset=['id_str', 'created_at'], keep='last', ignore_index=True)
