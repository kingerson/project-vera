"""
Creado el 20/5/2022 a las 5:27 p. m.

@author: jacevedo
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from time import sleep

import pandas as pd
from pandas import read_csv, DataFrame
from pandas import to_datetime, read_sql_query
from selenium.common.exceptions import SessionNotCreatedException
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from sqlalchemy.types import String
from webdriver_manager.chrome import ChromeDriverManager

# import sys
# sys.path.append(r'C:\Users\jacevedo\OneDrive - Superintendencia de Bancos de la Republica Dominicana\Documents\ProUsuario Project\tools')
import sql_tools
from general_tools import json_reader, custom_timer
from general_tools import read_credentials, update_credentials

logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(message)s')


# %%


def exporta_viafirma():
    def read_attempt(file_path):
        retries = 10
        while retries > 0:
            try:
                df = read_csv(file_path, sep=';', encoding='latin-1')
                file_to_rem = Path(file_path)
                with open('viafirma_log.txt', 'a') as f:
                    fecha = datetime.now().isoformat()
                    f.write(f'{fecha},True,{df.shape[0]}\n')
                return df
            except FileNotFoundError:
                sleep(5)
                # read_attempt(file_path)
                retries -= 1
                if retries > 60:
                    break
        logging.info('No file encountered')
        return DataFrame()


    def get_options():
        options = ChromeOptions()
        options.use_chromium = True
        options.add_argument('headless')
        return options


    def get_driver():
        try:
            service = Service(read_credentials('chromedriver'))
            driver = Chrome(service=service, options=get_options())
        except SessionNotCreatedException:
            with Service(ChromeDriverManager().install()) as service:
                driver = Chrome(service=service, options=get_options())
                if service.path != read_credentials('chromedriver'):
                    update_credentials('viafirma', service.path)
        return driver


    # %%
    def main():
        # Opens browser

        driver = get_driver()
        try:
            viafirma_url = 'https://www.viafirma.com.do/inbox/app/sib/'
            driver.get(viafirma_url)

            logging.info('obtuvo el driver')
            # Finds username input box and passes username
            login = driver.find_element(by=By.XPATH, value='/html/body/div/div/div[2]/div/form/div/p/input')

            login.send_keys(read_credentials('viafirma')['user'])

            # Finds password input box and passes password
            password = driver.find_element(by=By.XPATH, value='/html/body/div/div/div[2]/div/form/div/div[1]/p/input[1]')
            password.send_keys(read_credentials('viafirma')['pass'])

            login_button = driver.find_element(by=By.XPATH, value="/html/body/div/div/div[2]/div/form/div/div[2]/input")
            login_button.click()
            logging.info('entro a viafirma')

            # Finds terminadas link
            terminadas_link = driver.find_element(
                by=By.XPATH,
                value="/html/body/div[3]/div[2]/div[1]/ul/li[14]/ul/form/li[2]/a")
            terminadas_link.click()

            terminadas_link = driver.find_element(
                by=By.CSS_SELECTOR,
                value="[title='Peticiones pertenecientes a comunicaciones internas que ya han sido finalizadas']")
            terminadas_link.click()

            dl_path = r'C:\Users\jacevedo\OneDrive - Superintendencia de Bancos de la Republica Dominicana\Documents\ProUsuario Project\viafirma\export_logs'
            params = {'behavior': 'allow', 'downloadPath': dl_path}
            driver.execute_cdp_cmd('Page.setDownloadBehavior', params)
            WebDriverWait(driver, 5).until(ec.element_to_be_clickable((By.LINK_TEXT, 'Exportar a CSV'))).click()
            # sleep(5)
            logging.info('descargo el archivo')
            df = read_attempt(dl_path + r'\export.csv')
            logging.info('Leyó el archivo')
            # Specify the current file name and the new file name
            current_file_name = dl_path + r'\export.csv'
            new_file_name = dl_path + f"\\{datetime.today().strftime('%Y%m%d_%H%M%S')}_export.csv"
            # Check if the file exists before renaming
            print(new_file_name)
            if os.path.exists(current_file_name):
                # Rename the file
                os.rename(current_file_name, new_file_name)
                print(f"File '{current_file_name}' has been renamed to '{new_file_name}'.")
            else:
                print(f"The file '{current_file_name}' does not exist.")
            return df
        except Exception as e:
            logging.info('Hubo un error')
            logging.info(e.__traceback__)
            with open('viafirma_log.txt', 'a') as f:
                fecha = datetime.now().isoformat()
                f.write(f'{fecha},False,None\n')
        driver.close()
        driver.quit()



def sub_24(x):
    hour = x[-5:-2]
    if hour == '24:':
        x = x.replace(hour, '00:')
    return x

@custom_timer
def get_last_date():
    query = '''
    select * from FIRMAS inner join(
        select max(fecha_firma) ultima_fecha from firmas
    ) b on b.ultima_fecha = fecha_firma'''

    last_record = (
        sql_tools.query_reader(query, mode='many')
        .ultima_fecha
        .drop_duplicates()[0]
    )
    return last_record

@custom_timer
def get_last_date2():
    query = '''
    SELECT * FROM FIRMAS
    INNER JOIN (
        SELECT MAX(fecha_firma) ultima_fecha FROM firmas
    ) b ON b.ultima_fecha = fecha_firma'''

    engine = sql_tools.conn_creator(return_engine=True)[1]
    last_record = read_sql_query(query, engine)['ultima_fecha'].iloc[0]
    return last_record


def convert_time(series):
    series = to_datetime(series, format='%d/%m/%Y %H:%M')
    series = (
        series
        .dt.tz_localize(tz='UTC')
        .dt.tz_convert(tz='America/Santo_Domingo')
        .dt.tz_localize(None)
    )
    return series


def procesa_viafirma(df):
    df.columns = df.columns.str.lower()
    columnas_fecha = {
        'fecha de envío': 'fecha_envio',
        'fecha de modificación': 'fecha_firma'
    }
    df.rename(columnas_fecha, axis=1, inplace=True)
    # cols = ['csv', 'remitente', 'asunto', 'fecha_envio', 'fecha_firma', 'estado']
    # columnas_fecha = {
    #     'send date': 'fecha_envio',
    #     'modification date': 'fecha_firma'
    # }
    # df.rename(columnas_fecha, axis=1, inplace=True)
    # english_cols = {
    #     'security code':'csv',
    #     'sender':'remitente',
    #     'subject':'asunto',
    #     'send date': 'fecha_envio',
    #     'modification date': 'fecha_firma',
    #     'status':'estado'
    # }
    # df.columns = df.columns.map(english_cols)
    cols = ['csv', 'remitente', 'asunto', 'fecha_envio', 'fecha_firma', 'estado']
    try:
        df = df[cols].copy()
    except KeyError:
        en_cols = ['security code', 'sender', 'subject', 'send date', 'modification date', 'status']
        df = df[en_cols].copy()
        df.columns = df.columns.map({'security code': 'csv',
         'sender': 'remitente',
         'subject': 'asunto',
         'send date': 'fecha_envio',
         'modification date': 'fecha_firma',
         'status': 'estado'})

    df.remitente = df.remitente.str.replace(r'[\s]+', ' ', regex=True)
    df[['fecha_firma', 'fecha_envio']] = df[['fecha_firma', 'fecha_envio']].map(sub_24)
    df.fecha_firma = pd.to_datetime(df.fecha_firma, dayfirst=True)
    df.fecha_envio = pd.to_datetime(df.fecha_envio, dayfirst=True)
    last_date = get_last_date()
    mas_recientes = df.fecha_firma > last_date
    nuevas = df[mas_recientes]
    # proceso_mapa = json_reader('mapa_viafirma.json')
    proceso_mapa = json_reader(r'C:\Users\jacevedo\OneDrive - Superintendencia de Bancos de la Republica Dominicana\Documents\ProUsuario Project\viafirma\mapa_viafirma.json')
    nuevas['tipo'] = nuevas.remitente.map(proceso_mapa)
    finalizadas = nuevas.estado.isin(["Finalizada", "Completed"])
    # finalizadas = df.estado == "Completed"
    sin_recursos = ~nuevas.asunto.str.contains('Notificación Recurso')
    nuevas = nuevas[finalizadas & sin_recursos].reset_index(drop=True)
    df = nuevas.copy()
    print(df.tail())
    print(df.shape)
    with sql_tools.conn_creator() as conn:
        df.to_sql('firmas', conn, index=False, dtype=dtypes, if_exists='append')
        # df.to_sql('firmas', conn, index=False, dtype=dtypes, if_exists='replace')


dtypes = {
    'csv': String(20),
    'remitente': String(100),
    'asunto': String(256),
    'estado': String(20),
    'tipo': String(20)
}

#
# if __name__ == '__main__':
#     main_df = main()
