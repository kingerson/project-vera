import numpy as np
import pandas as pd
from general_tools import excel_formatter

def min_max(series):
    minimo = series.min()
    maximo = series.max()
    return series.apply(lambda x: (x - minimo) / (maximo - minimo))

def impact_index(df):
    impact_index = (
    df['quote_count'] * 100 +
    df['reply_count'] * 50 +
    df['retweet_count'] * 20 +
    df['like_count'] * 10 +
    np.log10(df['followers_count'].replace(0,1)) +
    np.log10(df['impression_count'].replace(0,1))
    )
    impact_index = np.sqrt(impact_index)
    return impact_index

def find_top_tweets(df, user_string, eif, username_filter_string, n=5):
    filtro = df.text.str.contains(user_string)
    user_filter = df.user_screen_name.str.contains(username_filter_string)
    top5 = df[filtro & ~user_filter].nlargest(n, 'impact_index')
    top5['entidad'] = eif
    # print(top5.interactions)
    return top5


#%%

def main(tweets, FOLDER_PATH, USERNAME_FILTER_STRING):
    eif_users = dict(
        popular = 'popularenlinea|popularatulado',
        reservas = 'banreservasrd',
        bhd = 'bhdleon|bancobhdleon|bancobhd',
        scotia = 'scotiabankrd'
    )
    tweets['impact_index'] = impact_index(tweets)
    top_tweets = pd.concat([find_top_tweets(tweets, val, key, USERNAME_FILTER_STRING, n=150) for key, val in eif_users.items()])
    top_tweets['tweet_url'] = top_tweets.apply(lambda x: f'https://www.twitter.com/{x.user_screen_name}/status/{x.id_str}', axis=1)
    top_tweets['interactions'] = top_tweets[['quote_count', 'reply_count', 'retweet_count', 'like_count']].sum(axis=1)
    top_tweets['views'] = top_tweets['impression_count']
    with pd.ExcelWriter(f'{FOLDER_PATH}/top_tweets_{FOLDER_PATH.split("/")[-2]}.xlsx', engine='xlsxwriter') as writer:
        excel_formatter(writer, top_tweets[top_columns], 'Top Reclamaciones')
    return tweets


top_columns = [
    'text',
    'interactions',
    'user_screen_name',
    'user_name',
    'user_description',
    'followers_count',
    'impact_index',
    'entidad',
    'tweet_url'
    ]

