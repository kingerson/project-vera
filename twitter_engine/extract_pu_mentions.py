"""
Creado el 4/7/2022 a las 5:20 p. m.

@author: jacevedo
"""
#%%


from datetime import date
# import twitter_tools_v3 as tt
import twitter_tools_v2 as tt
import prousuario_tools as pt
import pandas as pd
from pandas.tseries.offsets import MonthEnd, MonthBegin
from twitter_engine import extract_sentiment
from twitter_engine import top_tweets
from twitter_engine import bank_words_spacy
from win32com.shell import shell, shellcon
from os import mkdir
from timeit import default_timer as timer
from general_tools import custom_timer
import re
from general_tools import excel_formatter

#%%
START_DATE = (date.today() - MonthBegin(2)).strftime('%Y-%m-%d')
END_DATE = (date.today() - MonthBegin()).strftime('%Y-%m-%d')
# START_DATE = '2023-10-01'
# END_DATE = '2023-11-01'
FOLDER_NAME = START_DATE[:7].replace('-', '_')
DOCS_PATH = shell.SHGetFolderPath(0, shellcon.CSIDL_PERSONAL, None, 0)
FOLDER_PATH = f"{DOCS_PATH}/LaSuperTeEscucha/{FOLDER_NAME}/"

USERNAME_FILTER_STRING = (
    'popularenlinea|popularatulado|banreservasrd|scotiabankrd|bhdleon'
    '|bancobhdleon|bsc_rd|bancocariberd|bancobdi|bancovimenca|bcolopezdeharo'
    '|bancamerica|promericard|banescord|bcolafiserd|ademibanco|bancoademi'
    '|bellbankdr|asocpopular|acapdom|asocperavia|asocromana|alaverrd'
    '|asocduarte|asomaprd|asocmocana1|abonap_|asoclanacional|prousuariord'
    '|superdebancosrd|sbfernandez|fansvipfotocron|elnuevodiariord|listindiario'
    '|cdn37|z101digital|antena7oficial|diputadosrd|carolinamejiag|presidenciard'
    '|senadord|rodrigmarchena|agoramallrd|mananerord|elreydelaradio|super7fm'
    '|megacentrord|gloriareyesg|eduardoestrella|vicerdo|tusambildo|intrant_rd'
    '|rdbseleccion|mlbdominicana|miderec_rd|alcaldiadn|domexcourier|anoticias7'
    '|scotiabankhelps|estonoesradiotw|edesurrd|tpago|reconocidosnet'
    '|carlosgabrielgc|laurabonnellyv|visaiberiablh|spereyrarojas|condesatv1'
    '|lnbf_rd|itobisono|lidomrd|unstoppable8672|fuegoalalata|epascarc|cambiasoel'
    '|fansfielesncdn1|faraonrafael|observa27401323|felixhe12181981|laurabonnellyv'
    '|notidigitalrd1|nopierdo|bolivar33766257|andresvander|juvbalaguerista'
    '|alopezvalerio|leemanzanillo|eventsinfluenc1|jusanz11|el_bid|elradar_do'
    '|wendysantosb|sensacionalrd|guasabaraeditor|fuegoalalata|aquilesjimenez'
    '|fedombalrd|yocreoenfaride|carlosgabrielgc|mic_rd|lopezm00|conluisemilio'
    '|aplatanaonews|jompear|precisionportal|josebaezguerre1|jusanz11'
    '|infoturdom|arsreservas|gabsocialrd|prousuariord|superdebancosrd|sbfernandezw|bancobhd'
    '|fansreflexiones|fansfielesncdn|victors10966516|RafaelGrullon9'
)

@custom_timer
def count_mentions(df, prousuario=False):
    bank_counts = {}
    bank_users = pt.get_bank_users()
    criteria = 'prousuariord|superdebancosrd|sbfernandezw'
    for b in bank_users:
        bank = bank_users[b]
        if prousuario:
            pu_filter = df.text.str.contains(criteria)
            bank_filter = df.text.str.contains(b)
            filter = pu_filter & bank_filter
        else:
            filter = df.text.str.contains(b)
        count = len(df[filter])
        if bank not in bank_counts:
            bank_counts[bank] = count
        else:
            bank_counts[bank] += count
    return pd.Series(bank_counts)

def count_mentions(df, prousuario=False):
    bank_counts = {}
    bank_users = pt.get_bank_users()
    criteria = 'prousuariord|superdebancosrd|sbfernandezw'
    for b in bank_users:
        bank = bank_users[b]
        filter = df.text.str.contains(b) & (df.text.str.contains(criteria) if prousuario else True)
        count = sum(1 for _ in filter if _)
        bank_counts.setdefault(bank, 0)
        bank_counts[bank] += count
    return pd.Series(bank_counts)


@custom_timer
def count_mentions2(df, prousuario=False):
    bank_counts = {}
    bank_users = pt.get_bank_users()
    criteria = 'prousuariord|superdebancosrd|sbfernandezw'
    pattern = re.compile('|'.join(bank_users.keys()) + '|' + criteria)
    for _, tweet in df.iterrows():
        if pattern.search(tweet['text'].lower()):
            bank_name = tweet['text'].lower().split()[-1]
            if bank_name in bank_users.values():
                if bank_name not in bank_counts:
                    bank_counts[bank_name] = 1
                else:
                    bank_counts[bank_name] += 1
    return pd.Series(bank_counts)

#%%

def main():
    tweets = tt.read_tweets(dbase='tweets_bancos_v2', start_date=START_DATE, end_date=END_DATE)
    tweets = tweets.drop_duplicates(subset=['id_str'], ignore_index=True)
    tweets.text = tweets.text.str.lower()
    prousuario_mentions = count_mentions(tweets, prousuario=True)
    bank_mentions = count_mentions(tweets)
    feelings, tweets = extract_sentiment.main(tweets, filter=True)
    tweets['sentimiento'] = 'Neutro'
    tweets.loc[tweets.negativo.astype(bool), 'sentimiento'] = 'Negativo'
    tweets.loc[tweets.positivo.astype(bool), 'sentimiento'] = 'Positivo'
    print(feelings)
    cantidad_negativas = (feelings.negative * bank_mentions)
    percent_negativas = cantidad_negativas / cantidad_negativas.sum()
    metrics = pd.concat(
        [prousuario_mentions,
        bank_mentions,
        feelings,
        cantidad_negativas,
        percent_negativas], axis=1
    )
    print(metrics.head())
    metrics.columns=['menciones_prousuario', 'menciones_entidad', '%positivas', '%neutrales', '%negativas', 'cantidad_negativas', 'porcentaje_del_sector']
    try:
        metrics.to_excel(f'{FOLDER_PATH}twitter_metrics_{START_DATE}.xlsx')
    except OSError:
        mkdir(FOLDER_PATH)
        metrics.to_excel(f'{FOLDER_PATH}twitter_metrics_{START_DATE}.xlsx')

    prime_tik = timer()
    tik = timer()
    tweets = top_tweets.main(tweets, FOLDER_PATH, USERNAME_FILTER_STRING)
    bank_words_spacy.main(tweets, FOLDER_PATH, USERNAME_FILTER_STRING)
    print(f'implementacion tardo {timer() - tik:.3f}')
    print(f'total de tiempo {timer() - prime_tik:.3f}')




#%%
if __name__ == "__main__":
    main()


