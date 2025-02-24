"""
Creado el 19/5/2022 a las 9:31 p. m.

@author: jacevedo
"""

from tasas.proceso_tabla_tarjetas import get_cards
tarjetas = get_cards()

from tasas.proceso_tasas_tarjetas import get_fees
tasas = get_fees(mode='all')



#%%
import urllib
from sqlalchemy import create_engine
server = "sbprousuarioqa.database.windows.net"
database = "ProUsuarioQADB1"
username = "sbsa"
password = "/Ninguno01*"

driver = '{ODBC Driver 17 for SQL Server}'

odbc_str = 'DRIVER='+driver+';SERVER='+server+';PORT=1433;UID='+username+';DATABASE='+ database + ';PWD='+ password
connect_str = 'mssql+pyodbc:///?odbc_connect=' + urllib.parse.quote_plus(odbc_str)

print(connect_str)

engine = create_engine(connect_str)
tarjetas.to_sql('tarjetas', engine.connect(), if_exists='replace', index=False, chunksize=10000)