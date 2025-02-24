"""
Creado el 6/2/2024 a las 5:26 p. m.

@author: jacevedo
"""

import pyodbc
from general_tools import read_credentials

credentials = read_credentials('azure_db_prod')
db_user = credentials['db_user']
db_pass = credentials['db_pass']
db_server = credentials['db_server']
db_port = credentials['db_port']
db_name = credentials['db_name']
driver = credentials['driver']
driver= '{ODBC Driver 17 for SQL Server}'  # Update this to your ODBC driver version

# Construct connection string
cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+db_server+';PORT=1433;DATABASE='+db_name+';UID='+db_user+';PWD='+ db_pass)
cursor = cnxn.cursor()

# Sample query
cursor.execute("SELECT TOP 10 * FROM ProUsuarioPRODDB1.dbo.InactiveOrAbandonedAccounts")
row = cursor.fetchone()
while row:
    print(row)
    row = cursor.fetchone()

#%%

import pymssql

db_user = credentials['db_user']
db_pass = credentials['db_pass']
db_server = credentials['db_server']
db_port = credentials['db_port']
db_name = credentials['db_name']
driver = credentials['driver']
# driver= '{ODBC Driver 17 for SQL Server}'  # Update this to your ODBC driver version

# Connect to your database
conn = pymssql.connect(db_server, db_user, db_pass, db_name)
cursor = conn.cursor()

# Sample query
cursor.execute("SELECT TOP 10 * FROM ProUsuarioPRODDB1.dbo.InactiveOrAbandonedAccounts")
for row in cursor:
    print(row)

# Close the connection
conn.close()

