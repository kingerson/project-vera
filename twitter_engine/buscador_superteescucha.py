import logging
from datetime import datetime, timedelta
from twitter_tools_v2 import (
    find_last_tweet, processes_tweets, send_to_sql
)
from urllib3 import disable_warnings, exceptions
disable_warnings(exceptions.InsecureRequestWarning)

logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(message)s')


#%%
def buscado_superteescucha(modo):
    """Corre los procesos de autorización, creación de reglas, corrida del query
    y normalización de los tweets para luego anexar a las respectivas bases de datos"""
    search_string = modo['terminos']
    dbase = modo['dbase']
    logging.info('Resolvió base de datos')
    from_date = find_last_tweet(dbase)
    if (datetime.today() - from_date).days >= 30:
        from_date = datetime.today() - timedelta(days=30)
    from_date_str = from_date.strftime('%Y-%m-%d %H:%M')
    logging.info(f'Última fecha: {from_date_str}')
    args = twitter_premium_args()
    rule = rule_creator(from_date_str, search_string)
    result = stream_tweets(rule, args, max_results=100000)
    logging.info('Trajo los tweets')
    result = processes_tweets(result)
    logging.info('Procesó los tweets')
    send_to_sql(result, dbase)
    logging.info('Actualizó la base de datos')


def main():
    """Corre el proceso de buscado para los dos escenarios establecidos."""
    search_modes = dict(
        bancos=dict(
            terminos=(
                '@scotiabankrd OR @banreservasrd OR @bhdleon OR @bancobhd OR @bancobhdleon '
                'OR @popularenlinea OR @popularatulado OR @bsc_rd OR @bancocariberd '
                'OR @bancobdi OR @bancovimenca OR @bcolopezdeharo OR @bancamerica '
                'OR @promericard OR @banescord OR @bcolafiserd OR @ademibanco '
                'OR @bancoademi OR @bellbankdr OR @acapdom OR @asocperavia '
                'OR @asocromana OR @alaverrd OR @asocduarte OR @asomaprd OR @asomocana1 '
                'OR @abonap_ OR @asoclanacional OR @QikBanco'
            ),
            dbase="tweets_bancos"
        ),
        prousuario=dict(

            terminos='#LaSuperTeEscucha OR @prousuariord OR @SuperdeBancosRD OR @SBFernandezW',
            dbase="tweets_sb"
        )
    )
    for key, value in search_modes.items():
        logging.info(f'Corriendo para el modo {key}')
        buscado_superteescucha(value)


if __name__ == '__main__':
    main()
