# %%
import sql_tools

from pandas import json_normalize, DataFrame, read_sql_query, concat, to_datetime, merge
from searchtweets import ResultStream
# from searchtweets import gen_rule_payload as payload_rule
from searchtweets import load_credentials as lc
from sqlalchemy import String, Integer
import re

from general_tools import convert_time


def twitter_premium_args():
    """
    Crea argumentos de authorización usando los tokens de Twitter Dev
    """
    premium_args = lc(
        # filename=(Path().resolve() / 'credentials/credenciales.yaml').as_posix(),
        filename=r'C:\Users\jacevedo\OneDrive - Superintendencia de Bancos de la Republica Dominicana\Documents\ProUsuario Project\credentials\credenciales.yaml',
        yaml_key='tw_search_basic',
        env_overwrite=False
        )
    return premium_args


def rule_creator(from_date, search_string):
    """
    Crea las reglas de busqueda
    """
    rule = payload_rule(
        search_string,
        from_date=from_date,
        results_per_call=100,
        )
    return rule


def stream_tweets(rule, premium_args, max_results=50000, max_pages=5000):
    """
    Genera un stream de tweets donde se capturará un numero definido de tweets,
    o un máximo de páginas. Lo que ocurra primero.
    """
    rs = ResultStream(
        rule_payload=rule,
        max_results=max_results,
        max_pages=max_pages,
        **premium_args
        )
    stream_result = rs.stream()
    stream_result = list(stream_result)
    stream_result = json_normalize(stream_result)
    return stream_result


def processes_tweets(data: DataFrame):
    data = data[TWITTER_COLS].copy()
    time_cols = ['created_at', 'user.created_at']
    data[time_cols] = data[time_cols].apply(convert_time).copy()
    data['source'] = data.source.str.split('>').str[1].str.split('<').str[0].copy()

    data.loc[data.truncated, 'text'] = data.loc[data.truncated, 'extended_tweet.full_text']
    data = data.drop('extended_tweet.full_text', axis=1)
    data.columns = data.columns.str.replace('.', '_', regex=False)
    return data


def find_last_tweet(dbase):
    """
    Busca el timestamp del ultimo tweet que se tiene registrado
    """
    query = (
        "SELECT MAX(created_at) created_at "
        f"FROM {dbase}"
    )
    with sql_tools.conn_creator() as conn:
        result = read_sql_query(query, conn, parse_dates=['created_at'])
    last_date = result.loc[0, 'created_at']
    return last_date


def extract_mentions(df, bank_users):
    mention_df = []
    for key in bank_users.keys():
        for pos, tweet in enumerate(df.text.str.lower()):
            if key in tweet:
                temp = df.loc[pos, ['created_at', 'id_str']].copy()
                temp['eif'] = bank_users[key]
                mention_df.append(temp)
    mention_df = concat(mention_df, axis=1).transpose().reset_index(drop=True)
    return mention_df


def extract_mentions2(df, bank_users):
    keys_pattern = '|'.join(re.escape(key) for key in bank_users.keys())
    matches = df.text.str.lower().str.contains(keys_pattern)
    mention_df = df[matches].copy()
    for key in bank_users.keys():
        for i, row in df[matches].iterrows():
            if key in row.text.lower():
                mention_df.loc[i, 'eif'] = bank_users[key]
    return mention_df.reset_index(drop=True)


def read_tweets(dbase='tweets_bancos', sample_size=None, columns='*',
                date_limit=2, start_date=None, end_date=None):
    """ Lee una muestra de los tweets """
    if date_limit == 1:
        if start_date is None:
            raise ValueError('Please provide a start date in YYYY-MM-DD format.')
        date_limit = f"WHERE created_at >= to_date('{start_date}', 'YYYY-MM-DD')"
    elif date_limit == 2:
        if start_date is None:
            raise ValueError('Please provide a start date in YYYY-MM-DD format.')
        if end_date is None:
            raise ValueError('Please provide an end date in YYYY-MM-DD format.')
        date_limit = f"WHERE created_at >= to_date('{start_date}', 'YYYY-MM-DD') AND created_at < to_date('{end_date}', 'YYYY-MM-DD') "
    elif date_limit == 0:
        date_limit = ''
    # query = f"SELECT {columns} FROM {dbase} {date_limit} ORDER BY created_at DESC"
    query = f"SELECT {columns} FROM {dbase} {date_limit}"
    if sample_size is not None:
        query += f" LIMIT {sample_size}"
    print(query)
    with sql_tools.conn_creator() as conn:
        result = read_sql_query(query, conn, parse_dates=['created_at'])
    return result


def send_to_sql(resultado, dbase):
    """Adjunta el dataframe resultado a la base de datos."""
    # dbase = "databases/super_escucha.db"
    with sql_tools.conn_creator() as conn:
        resultado.to_sql(dbase, conn, dtype=col_dtypes, index=False, if_exists='append')


def tweet_url_parser(record):
    """Return the URL of a tweet given a tweet record"""
    return f"https://www.twitter.com/{record.user_screen_name}/status/{record.id_str}"


def recreate_tweet(df, idx):
    user_screen_name = df.loc[idx, 'user_screen_name']
    id_str = df.loc[idx, 'id_str']
    return f"https://www.twitter.com/{user_screen_name}/status/{id_str}"



def check_username(user):
    if user not in USERNAME_FILTER_STRING:
        return USERNAME_FILTER_STRING + f'|{user}'
    else:
        print('usuario ya esta')
        return USERNAME_FILTER_STRING


def tweet_sampler(df):
    sample = df.sample()
    print(f'index {sample.index.values[0]}')
    print(sample.user_screen_name.str.lower().values[0])
    print(sample.text.values[0])
# %%


TWITTER_COLS = [
    'created_at', 'id_str', 'text', 'source', 'truncated', 'in_reply_to_status_id_str',
    'in_reply_to_user_id_str', 'in_reply_to_screen_name', 'quote_count', 'reply_count',
    'retweet_count', 'favorite_count', 'user.id_str', 'user.name', 'user.screen_name',
    'user.location', 'user.url', 'user.description', 'user.verified', 'user.followers_count',
    'user.friends_count', 'user.listed_count', 'user.favourites_count', 'user.statuses_count',
    'user.created_at', 'user.geo_enabled', 'extended_tweet.full_text']


col_dtypes = {
    'id_str': String(length=24),
    'text': String(length=1024),
    'source': String(length=32),
    'truncated': Integer(),
    'in_reply_to_status_id_str': String(length=24),
    'in_reply_to_user_id_str': String(length=24),
    'quote_count': Integer(),
    'reply_count': Integer(),
    'retweet_count': Integer(),
    'favorite_count': Integer(),
    'quoted_status_id_str': String(length=24),
    'user_id_str': String(length=24),
    'user_name': String(length=64),
    'user_screen_name': String(length=16),
    'user_location': String(length=132),
    'user_url': String(length=128),
    'user_description': String(length=300),
    'user_verified': Integer(),
    'user_followers_count': Integer(),
    'user_friends_count': Integer(),
    'user_listed_count': Integer(),
    'user_favourites_count': Integer(),
    'user_statuses_count': Integer(),
    'user_geo_enabled': Integer(),
    'in_reply_to_screen_name': String(length=16)
}


#%%

import ssl
context = ssl._create_unverified_context()
urllib.request.urlopen(req,context=context)

twitter_premium_args()


#%%

import requests as rs

#%%
url = 'https://api.twitter.com'
lel = rs.get(url, verify=False)
lel.status_code

#%%

from requests.utils import DEFAULT_CA_BUNDLE_PATH
print(DEFAULT_CA_BUNDLE_PATH)

#%%
import urllib.request as urlrq
url = 'https://api.twitter.com/2/tweets/search/recent'
resp = urlrq.urlopen(url, cafile=certifi.where())


#%%

import ssl, urllib
#%%
url = 'https://www.twitter.com'
context = ssl._create_unverified_context()
lel = urllib.request.urlopen(url,context=context)
lel.code


#%%

#%%

import requests
import os
import json
from general_tools import read_credentials
from general_tools import custom_timer


# To set your environment variables in your terminal run the following line:
# export 'BEARER_TOKEN'='<your_bearer_token>'

creds = read_credentials('tw_search_basic')

bearer_token = creds['token']

search_url = "https://api.twitter.com/2/tweets/search/recent"

#%%

# Optional params: start_time,end_time,since_id,until_id,max_results,next_token,
# expansions,tweet.fields,media.fields,poll.fields,place.fields,user.fields
terminos = (
               '@scotiabankrd OR @banreservasrd OR @bhdleon OR @bancobhd OR @bancobhdleon '
               'OR @popularenlinea OR @popularatulado OR @bsc_rd OR @bancocariberd '
               'OR @bancobdi OR @bancovimenca OR @bcolopezdeharo OR @bancamerica '
               'OR @promericard OR @banescord OR @bcolafiserd OR @ademibanco '
               'OR @bancoademi OR @bellbankdr OR @acapdom OR @asocperavia '
               'OR @asocromana OR @alaverrd OR @asocduarte OR @asomaprd OR @asomocana1 '
               'OR @abonap_ OR @asoclanacional OR @QikBanco'
           )
query_params = {
    'query': f'({terminos}) -is:retweet',
    'tweet.fields': (
        'created_at,id,public_metrics,text,source'
        # ',in_reply_to_user_id,conversation_id,referenced_tweets'
        # ',context_annotations,entities'
    ),
    'user.fields': 'name,username,created_at,description,public_metrics',
    'expansions': 'author_id',
    'max_results': 100
}


def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.HEADERS["Authorization"] = f"Bearer {bearer_token}"
    r.HEADERS["User-Agent"] = "v2RecentSearchPython"
    return r

def connect_to_endpoint(url, params):
    response = requests.get(url, auth=bearer_oauth, params=params, verify=False)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()


def main():
    json_response = connect_to_endpoint(search_url, query_params)
    print(json.dumps(json_response['data'], indent=4, sort_keys=True))


#%%
def parse_tweets(json_response):
    tweets = json_normalize(json_response['data'])
    users = json_normalize(json_response['includes']['users'])
    result = merge(tweets, users, how='left', left_on='author_id', right_on='id')
    return result

def processes_tweets(df):
    selected = df[columns]
    selected.columns = selected.columns.str.replace('public_metrics.', '')
    selected = selected.rename(col_rename_map, axis = 1)
    selected.created_at = to_datetime(selected.created_at).dt.tz_convert('America/Santo_Domingo')
    selected.user_created_at = to_datetime(selected.user_created_at).dt.tz_convert('America/Santo_Domingo')
    return selected



#%%
columns = ['id_x', 'created_at_x', 'text', 'public_metrics.retweet_count',
           'public_metrics.reply_count',
       'public_metrics.like_count', 'public_metrics.quote_count',
       'public_metrics.impression_count', 'description', 'author_id', 'name',
       'username', 'created_at_y', 'public_metrics.followers_count',
       'public_metrics.following_count', 'public_metrics.tweet_count',
       'public_metrics.listed_count']

col_rename_map = {
'id_x': 'id_str',
'created_at_x': 'created_at',
'author_id': 'user_id_str',
'name': 'user_name',
'username': 'user_screen_name',
'description': 'user_description',
'created_at_y': 'user_created_at'
}

#%%

selected.created_at = to_datetime(selected.created_at).dt.tz_convert('America/Santo_Domingo')
selected.user_created_at = to_datetime(selected.user_created_at).dt.tz_convert('America/Santo_Domingo')


#%%

@custom_timer
def get_tweets(search_url, query_params):
    """ Usa las credenciales de windows para conectarse al API OData del
    CRM y entregar un dataframe basado en el query definido.

    Parametros:
    query - El query a correr.
    headers = Los headers necesarios para el CRM.
    """
    resultados = []
    json_response = connect_to_endpoint(search_url, query_params)
    result = parse_tweets(json_response)
    resultados.append(result)
    total_resultados = len(result)
    print(f'{total_resultados} resultados')
    while 'next_token' in json_response['meta'].keys():
        query_params['next_token'] = json_response['meta']['next_token']
        json_response = connect_to_endpoint(search_url, query_params)
        result = parse_tweets(json_response)
        resultados.append(result)
        total_resultados += len(result)
        print(f'{total_resultados} resultados')
        try:
            query_params['next_token'] = json_response['meta']['next_token']
        except KeyError:
            print('No hay mas tweets')
    if len(resultados) > 0:
        df = concat(resultados).reset_index(drop=True)
        return df
    else:
        print('Sin resultados')

#%%


#%%

col_dtypes = {
    'id_str': String(length=24),
    'text': String(length=1024),
    'quote_count': Integer(),
    'reply_count': Integer(),
    'retweet_count': Integer(),
    'like_count': Integer(),
    'impression_count': Integer(),
    'user_id_str': String(length=24),
    'user_name': String(length=64),
    'user_screen_name': String(length=16),
    'user_description': String(length=300),
    'followers_count': Integer(),
    'following_count': Integer(),
    'tweet_count': Integer(),
    'listed_count': Integer(),
}

df = df[['id_str', 'created_at', 'text', 'retweet_count', 'reply_count',
       'like_count', 'quote_count', 'impression_count', 'user_id_str',
    'user_name', 'user_screen_name', 'user_description', 'user_created_at',
       'followers_count', 'following_count', 'tweet_count', 'listed_count']]


#%%

def find_last_tweet():
    """
    Busca el timestamp del ultimo tweet que se tiene registrado
    """
    query = (
        "SELECT MAX(id_str) id_str "
        f"FROM {dbase}"
    )
    with sql_tools.conn_creator() as conn:
        result = read_sql_query(query, conn, parse_dates=['created_at'])
    last_tweet = result.id_str[0]
    return last_tweet

#%%

last_tweet = find_last_tweet()
query_params['since_id'] = last_tweet
result = get_tweets(search_url, query_params)
result = processes_tweets(result)