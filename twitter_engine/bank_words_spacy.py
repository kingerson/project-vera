"""
Creado el 5/7/2022 a las 4:55 p. m.

@author: jacevedo
"""

import spacy
import pandas as pd
from collections import Counter
from general_tools import custom_timer


eif_users = dict(
    popular = 'popularenlinea|popularatulado',
    reservas = 'banreservasrd',
    bhd = 'bhdleon|bancobhdleon|bancobhd',
    scotia = 'scotiabankrd'
)

def create_nlp_engine():
    """Since loading the Spacy model takes some time, it would be best to load
     it once and reuse the same instance across all calls to this function."""
    if not hasattr(create_nlp_engine, 'nlp'):
        create_nlp_engine.nlp = spacy.load('es_dep_news_trf')
        # create_nlp_engine.nlp = spacy.load('es_core_news_sm')
    return create_nlp_engine.nlp


def creates_bank_tokens(tweets, eif_users, username_filter_string):
    bank_tokens = {}
    for key, val in eif_users.items():
        filtro = (~tweets.user_screen_name.str.lower().str.contains(username_filter_string) &
                  ~tweets.text.str.contains('rt @' + '|rt @'.join(username_filter_string.split('|'))) &
                  tweets.text.str.contains(val))
        nlp = create_nlp_engine()
        # limpio = list(nlp.pipe(tweets[filtro].text.tolist()))
        limpio = nlp.pipe(tweets[filtro].text.tolist())
        filename = key.lower().replace(' ', '_')
        print(filename)
        bank_tokens[filename] = {'tweets': limpio, 'impact': tweets.loc[filtro, 'impact_index']}
    return bank_tokens


# def extract_lemmas(result):
#     palabras = {}
#     for key, val in result.items():
#         lemmas = (token.lemma_ for tweet in val for token in tweet
#                   if token.pos_ in {'NOUN', 'VERB', 'PROPN', 'ADJ'} and len(token.lemma_) > 2 and token.is_alpha)
#         palabras[key] = Counter(lemmas)
#         print('Conto palabras')
#     return palabras

# @custom_timer
def tokeniza_lemmas(val):
    lemmas = list()
    indexes = dict()
    for idx, tweet in enumerate(val['tweets']):
        for token in tweet:
            if token.pos_ in {'NOUN', 'VERB', 'PROPN', 'ADJ'} and len(token.lemma_) > 2 and token.is_alpha:
                lemmas.append(token.lemma_)
                try:
                    indexes[token.lemma_] += val['impact'].iloc[idx]
                except:
                    indexes[token.lemma_] = val['impact'].iloc[idx]
    return lemmas, indexes

# @custom_timer
def extract_lemmas(result):
    palabras = {}
    for key, val in result.items():
        lemmas, indexes = tokeniza_lemmas(val)
        palabras[key] = {'wordcount': Counter(lemmas), 'indexes': indexes}
        print(f'Termino tokenizacion de {key}')
    print('termino todo')
    return palabras





def word_counts(palabras):
    words_dfs = []
    for key, val in palabras.items():
        partial = pd.DataFrame(val)
        partial['rank'] = partial.sum(axis=1)
        partial = partial.nlargest(500, columns='rank').reset_index()
        partial.columns = ['palabras', 'cantidad', 'indice_impacto', 'rango']
        partial.insert(0, 'eif', key)
        words_dfs.append(partial)
    return pd.concat(words_dfs)

#%%
def main(tweets, FOLDER_PATH, USERNAME_FILTER_STRING):
    print('Inicia proceso de tokenizacion')
    # nlp = create_nlp_engine()
    print('Engine NLP creada')
    print('Inicia tokenizacion')
    result = creates_bank_tokens(tweets, eif_users, USERNAME_FILTER_STRING)
    # result = creates_bank_tokens(tweets, eif_users, nlp, USERNAME_FILTER_STRING)
    print('Tokens creados')
    lemmas = extract_lemmas(result)
    print('Lemmas extraidos')
    word_count = word_counts(lemmas)
    word_count.to_excel(f'{FOLDER_PATH}/palabras_bancos.xlsx')
    print('Conteo de palabras terminado')
