# %%

import json
import re

import requests
from pandas import json_normalize, read_sql_query, concat, to_datetime, merge
from sqlalchemy import String, Integer

import sql_tools
from general_tools import custom_timer
from general_tools import read_credentials


def send_to_sql(resultado, dbase):
    """Adjunta el dataframe resultado a la base de datos."""
    with sql_tools.conn_creator() as conn:
        resultado.to_sql(dbase, conn, dtype=col_dtypes, index=False, if_exists='append')


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

#%%
def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """
    r.HEADERS["Authorization"] = f"Bearer {bearer_token}"
    r.HEADERS["User-Agent"] = "v2RecentSearchPython"
    return r


def connect_to_endpoint(url, params):
    response = requests.get(url, auth=bearer_oauth, params=params, verify=False)
        # Exception(response.status_code, response.text):
        # print(response.text)
    if 'must be a tweet id created after' in response.text:
        print('Tuit muy lejano')
        del params['since_id']
        response = requests.get(url, auth=bearer_oauth, params=params, verify=False)
    # if response.status_code == 200:
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
    selected = df[key_columns]
    selected.columns = selected.columns.str.replace('public_metrics.', '')
    selected = selected.rename(col_rename_map, axis = 1)
    selected.created_at = to_datetime(selected.created_at).dt.tz_convert('America/Santo_Domingo')
    selected.user_created_at = to_datetime(selected.user_created_at).dt.tz_convert('America/Santo_Domingo')
    return selected



#%%
def find_last_tweet(dbase):
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
key_columns = ['id_x', 'created_at_x', 'text', 'public_metrics.retweet_count',
           'public_metrics.reply_count',
       'public_metrics.like_count_x', 'public_metrics.quote_count',
'public_metrics.bookmark_count',
       'public_metrics.impression_count', 'description', 'author_id', 'name',
       'username', 'created_at_y', 'public_metrics.followers_count',
       'public_metrics.following_count', 'public_metrics.tweet_count',
       'public_metrics.listed_count']

col_rename_map = {
'id_x': 'id_str',
'created_at_x': 'created_at',
'like_count_x': 'like_count',
'author_id': 'user_id_str',
'name': 'user_name',
'username': 'user_screen_name',
'description': 'user_description',
'created_at_y': 'user_created_at'
}

col_dtypes = {
    'id_str': String(length=24),
    'text': String(length=1024),
    'quote_count': Integer(),
    'reply_count': Integer(),
    'retweet_count': Integer(),
    'like_count': Integer(),
    'impression_count': Integer(),
    'bookmark_count': Integer(),
    'user_id_str': String(length=24),
    'user_name': String(length=64),
    'user_screen_name': String(length=16),
    'user_description': String(length=300),
    'followers_count': Integer(),
    'following_count': Integer(),
    'tweet_count': Integer(),
    'listed_count': Integer(),
}

creds = read_credentials('tw_search_basic')

bearer_token = creds['token']
search_url = "https://api.twitter.com/2/tweets/search/recent"

#%%

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
    ),
    'user.fields': 'name,username,created_at,description,public_metrics',
    'expansions': 'author_id',
    'max_results': 100
}





#%%

def tweet_updater():
    last_tweet = find_last_tweet('tweets_bancos_v2')
    query_params['since_id'] = last_tweet
    query_params['since_id'] = '1789987264777551872'
    result = get_tweets(search_url, query_params)
    final_result = processes_tweets(result)
    send_to_sql(final_result, 'tweets_bancos_v2')