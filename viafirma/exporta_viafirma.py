"""
Creado el 20/5/2022 a las 5:27 p. m.

@author: jacevedo
"""

from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from general_tools import read_credentials, update_credentials
from pandas import read_csv, DataFrame
from pathlib import Path
from time import sleep
from selenium.common.exceptions import SessionNotCreatedException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
#%%


#%%


def read_attempt(file_path):
    retries = 10
    while retries > 0:
        try:
            df = read_csv(file_path, sep=';')
            file_to_rem = Path(file_path)
            file_to_rem.unlink()
            return df
        except FileNotFoundError:
            sleep(5)
            read_attempt(file_path)
            retries -= 1
    print('No file encountered')
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
        service = Service(ChromeDriverManager().install())
        driver = Chrome(service=service, options=get_options())
        update_credentials('viafirma', service)
    return driver


#%%
def main():
    # Opens browser
    driver = get_driver()
    viafirma_url = 'https://www.viafirma.com.do/inbox/app/sib/'
    driver.get(viafirma_url)

    print('obtuvo el driver')
    # Finds username input box and passes username
    login = driver.find_element(by=By.XPATH,
                                value='/html/body/div/div[2]/div/form/div/p/input'
                                )
    login.send_keys(
        read_credentials('viafirma')['user']
    )

    # Finds password input box and passes password
    password = driver.find_element(
        by=By.XPATH,
        value='/html/body/div/div[2]/div/form/div/div[1]/p/input[1]'
        )
    password.send_keys(
        read_credentials('viafirma')['pass']
    )

    login_button = driver.find_element(
        by=By.XPATH,
        value="/html/body/div/div[2]/div/form/div/div[2]/input"
    )
    login_button.click()
    print('entro a viafirma')

    # Finds terminadas link
    terminadas_link = driver.find_element(
        by=By.XPATH,
        value="/html/body/div[3]/div[2]/div[1]/ul/li[14]/ul/form/li[2]/a")
    terminadas_link.click()

    dl_path = r'C:\Users\jacevedo\Downloads'
    params = {'behavior': 'allow', 'downloadPath': dl_path}
    driver.execute_cdp_cmd('Page.setDownloadBehavior', params)
    WebDriverWait(driver, 5).until(ec.element_to_be_clickable((By.LINK_TEXT, 'Exportar a CSV'))).click()
    sleep(10)
    print('descargo el archivo')
    df = read_attempt(dl_path + r'\export.csv')
    driver.close()
    driver.quit()
    return df
