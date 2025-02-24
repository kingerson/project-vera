"""
Creado el 13/12/2023 a las 3:06 p. m.

@author: jacevedo
"""
import requests
from pandas import json_normalize, read_sql_query, concat, to_datetime, merge
from sqlalchemy import String, Integer
import sql_tools
from general_tools import custom_timer, read_credentials

# Global constants and configurations
DB_NAME = 'tweets_bancos_v2'
SEARCH_URL = "https://api.twitter.com/2/tweets/search/recent"
BEARER_TOKEN = read_credentials('tw_search_basic')['token']


def send_to_sql(df, db_name):
    """
    Append dataframe to the specified database.
    """
    with sql_tools.conn_creator() as conn:
        df.to_sql(db_name, conn, dtype=col_dtypes, index=False, if_exists='append')


def make_paginated_get_request(url, params):
    """
    Make a paginated GET request to a given URL with the specified parameters.
    Continues to make requests as long as 'next_token' is provided in the response.
    Handles specific error case related to 'since_id'.

    Args:
    url (str): The URL to make the GET request to.
    params (dict): Dictionary of parameters to be sent in the query string.
    bearer_token (str): Bearer token for authorization.

    Returns:
    list: A list of JSON responses from the API.
    """

    def get_request():
        headers = {
            "Authorization": f"Bearer {BEARER_TOKEN}",
            "User-Agent": "v2RecentSearchPython"
        }
        response = requests.get(url, headers=headers, params=params, verify=False)
        response.raise_for_status()
        return response.json()

    responses = []
    total_resultados = 0
    while True:
        try:
            response = get_request()
            responses.append(response)
            total_resultados += response['meta']['result_count']
            print(f'{total_resultados} resultados')

            # Check if there's a next page
            next_token = response.get('meta', {}).get('next_token')
            if not next_token:
                break
            params['next_token'] = next_token

        except requests.HTTPError as e:
            # Check if error message is in the response and 'since_id' is in the parameters
            if 'must be a tweet id created after' in str(e) and 'since_id' in params:
                print("Encountered 'since_id' error, retrying without 'since_id' parameter.")
                del params['since_id']
            else:
                raise
    print(total_resultados)
    return dict(responses=responses, total_resultados=total_resultados)


# Rest of your functions (main, parse_tweets, processes_tweets, find_last_tweet, get_tweets) goes here
# Make sure to replace repeated code with get_request function

def parse_tweets(json_response):
    tweets = json_normalize(json_response['data'])
    users = json_normalize(json_response['includes']['users'])
    result = merge(tweets, users, how='left', left_on='author_id', right_on='id')
    return result


def processes_tweets(df):
    selected = df[key_columns]
    selected.columns = selected.columns.str.replace('public_metrics.', '')
    selected = selected.rename(col_rename_map, axis=1)
    selected.created_at = to_datetime(selected.created_at).dt.tz_convert('America/Santo_Domingo')
    selected.user_created_at = to_datetime(selected.user_created_at).dt.tz_convert('America/Santo_Domingo')
    return selected


# %%
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

def find_last_date(dbase):
    """
    Busca el timestamp del ultimo tweet que se tiene registrado
    """
    query = (
        "SELECT MAX(created_at) created_at "
        f"FROM {dbase}"
    )
    with sql_tools.conn_creator() as conn:
        result = read_sql_query(query, conn, parse_dates=['created_at'])
    last_tweet = result.created_at[0]
    return last_tweet


# %%

@custom_timer
def get_tweets(search_url, query_params):
    """ Usa las credenciales de windows para conectarse al API OData del
    CRM y entregar un dataframe basado en el query definido.

    Parametros:
    query - El query a correr.
    headers = Los headers necesarios para el CRM.
    """
    responses = make_paginated_get_request(search_url, query_params)
    total_resultados = responses['total_resultados']
    responses = responses['responses']
    if total_resultados != 0:
        resultados = [parse_tweets(x) for x in responses]
        df = concat(resultados).reset_index(drop=True)
        return df
    else:
        return total_resultados
        print('Sin resultados')


# %%
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

# %%

TERMINOS = (
    '@scotiabankrd OR @banreservasrd OR @bhdleon OR @bancobhd OR @bancobhdleon '
    'OR @popularenlinea OR @popularatulado OR @bsc_rd OR @bancocariberd '
    'OR @bancobdi OR @bancovimenca OR @bcolopezdeharo OR @bancamerica '
    'OR @promericard OR @banescord OR @bcolafiserd OR @ademibanco '
    'OR @bancoademi OR @bellbankdr OR @acapdom OR @asocperavia '
    'OR @asocromana OR @alaverrd OR @asocduarte OR @asomaprd OR @asomocana1 '
    'OR @abonap_ OR @asoclanacional OR @QikBanco'
)
QUERY_PARAMS = {
    'query': f'({TERMINOS}) -is:retweet',
    'tweet.fields': (

        'created_at,id,public_metrics,text,source'
    ),
    'user.fields': 'name,username,created_at,description,public_metrics',
    'expansions': 'author_id',
    'max_results': 100
}


def tweet_updater():
    last_tweet = find_last_tweet('tweets_bancos_v2')
    last_date = find_last_date('tweets_bancos_v2')
    QUERY_PARAMS['since_id'] = last_tweet
    result = get_tweets(SEARCH_URL, QUERY_PARAMS)
    # if not result == 'Sin resultados':
    print(result)
    if len(result) == 0:
        print('Sin resultados')
    else:
        final_result = processes_tweets(result)
        send_to_sql(final_result, 'tweets_bancos_v2')


#%%
# Main execution
if __name__ == "__main__":
    # Define query parameters and execute main logic
    tweet_updater()
