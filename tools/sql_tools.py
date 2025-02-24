import sqlalchemy as sql
from yaml import safe_load
from pandas import DataFrame
from pathlib import Path
from urllib.parse import quote_plus
from general_tools import read_credentials
from timeit import default_timer as timer
# import oracledb
# oracledb.init_oracle_client()
# connection = oracledb.connect(user=db_user, password=db_pass,
#                               host=db_server, port=db_port, service_name=db_name)
# def conn_creator(creds='oracle_pu', return_engine=False, return_string=False):
#     credentials = read_credentials(creds)
#     db_user = credentials['db_user']
#     db_pass = credentials['db_pass']
#     db_server = credentials['db_server']
#     db_port = credentials['db_port']
#     db_name = credentials['db_name']
#     driver = credentials['driver']
#     service_name = 'your_service_name'
#     auth = f'oracle+cx_oracle://{db_user}:{db_pass}@{db_server}:{db_port}/?service_name={db_name}'
#     engine = sql.create_engine(auth, max_identifier_length=128)
#     if creds == 'oracle':
#         auth = f'oracle+cx_oracle://{db_user}:{db_pass}@{db_server}:{db_port}/?service_name={db_name}'
#     elif creds == 'azure_db_qa':
#         odbc_str = f'DRIVER={driver};SERVER={db_server};PORT=1433;UID={db_user};DATABASE={db_name};PWD={db_pass}'
#         auth = 'mssql+pyodbc:///?odbc_connect=' + quote_plus(odbc_str)
#         engine = sql.create_engine(auth, max_identifier_length=128, fast_executemany=True)
#     elif creds == 'azure_db_prod' or creds == 'azure_db_user_report':
#         odbc_str = f'DRIVER={driver};SERVER={db_server};PORT=1433;UID={db_user};DATABASE={db_name};PWD={db_pass};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
#         # odbc_str = 'Driver={ODBC Driver 17 for SQL Server};' + f'Server={db_server},1433;Database={db_name};UID={db_user};PWD={db_pass};Encrypt=yes;Connection Timeout=30;'
#         auth = 'mssql+pyodbc:///?odbc_connect=' + quote_plus(odbc_str)
#         engine = sql.create_engine(auth, max_identifier_length=128, fast_executemany=True)
#     elif creds == 'ms_sql':
#         driver = '{ODBC Driver 17 for SQL Server}'
#         # driver = 'ODBC+Driver+17+for+SQL+Server'
#         odbc_str = quote_plus(f'DRIVER={driver};SERVER={db_server};UID={db_user};PASS={db_pass};DATABASE={db_name};Trusted_Connection=yes')
#         # odbc_str = (f'@{db_server}/{db_name}?driver={driver}&Trusted_Connection=yes')
#         # odbc_str = f'DRIVER={driver};SERVER={db_server};PORT=1433;UID={db_user};DATABASE={db_name};PWD={db_pass};TrustServerCertificate=no;Connection Timeout=30;'
#         # odbc_str = f'{db_user}:{db_pass}@{db_server}/{db_name}?driver={driver}'
#         # odbc_str = 'Driver={ODBC Driver 17 for SQL Server};' + f'Server={db_server},1433;Database={db_name};UID={db_user};PWD={db_pass};Encrypt=yes;Connection Timeout=30;'
#         auth = 'mssql+pyodbc:///?odbc_connect=' + quote_plus(odbc_str)
#         # auth = 'mssql+pyodbc://' + odbc_str
#         engine = sql.create_engine(auth, max_identifier_length=128, fast_executemany=True)
#         # connection_string = (
#         #     f"""mssql+pyodbc://{db_user}:{db_pass}@{db_server}/{db_name}?driver=ODBC+Driver+17+for+SQL+Server&encrypt=yes&trustServerCertificate=no&connection+timeout=30"""
#         # )
#         # engine = sql.create_engine(connection_string, max_identifier_length=128, fast_executemany=True)
#         # engine.connect()
#         # odbc_str = 'Driver={ODBC Driver 17 for SQL Server};'+f'Server={db_server}:1433;Database={db_name};UID={db_user};PWD={db_pass};'
#     elif creds == 'azure':
#         # params = quote_plus(
#         #     f"Driver={driver};"
#         #     f"Server=tcp:{db_server},1433;"
#         #     f"Database={db_name};"
#         #     f"UID={db_user};"
#         #     f"Pass={db_pass};"
#         #     f"Authentication=ActiveDirectoryInteractive;"
#         #     f"TrustServerCertificate=yes;"
#         # )
#         connection_string = (
#             f"mssql+pyodbc://{db_user}:{db_pass}@{db_server}/{db_name}?"
#             "driver=ODBC+Driver+17+for+SQL+Server&authentication=ActiveDirectoryPassword"
#             "&fast_executemany=True"
#
#         )
#         # engine = sql.create_engine(f"mssql+pyodbc:///?odbc_connect={params}")
#         engine = sql.create_engine(
#             connection_string,
#             pool_size=10,  # Number of connections to keep in the pool
#             max_overflow=20,  # Extra connections allowed if the pool is full
#             pool_timeout=30,  # Time to wait for a connection from the pool
#             pool_recycle=3600  # Timeout to recycle connections, avoids stale ones
#         )
#
#     conn = engine.connect()
#     if return_engine:
#         return conn, engine
#     elif return_string:
#         return conn, auth
#     elif return_engine and return_string:
#         return conn, engine, auth
#     else:
#         return conn


def conn_creator(creds='oracle_pu', return_engine=False, return_string=False):
    credentials = read_credentials(creds)
    db_user = credentials['db_user']
    db_pass = credentials['db_pass']
    db_server = credentials['db_server']
    db_port = credentials.get('db_port', '1433')  # Default port for SQL Server
    db_name = credentials['db_name']
    driver = credentials.get('driver', '{ODBC Driver 17 for SQL Server}')

    # Initialize variables
    auth = None
    engine = None

    if creds in ['oracle_pu', 'oracle']:
        # Construct Oracle connection string
        auth = f'oracle+cx_oracle://{db_user}:{db_pass}@{db_server}:{db_port}/?service_name={db_name}'
        engine = sql.create_engine(auth, max_identifier_length=128)

    elif creds in ['azure_db_qa', 'azure_db_prod', 'azure_db_user_report', 'ms_sql']:
        # Build ODBC connection string
        odbc_str = (
            f'DRIVER={driver};'
            f'SERVER={db_server};'
            f'PORT={db_port};'
            f'DATABASE={db_name};'
            f'UID={db_user};'
            f'PWD={db_pass};'
            'Encrypt=yes;'
            'TrustServerCertificate=no;'
            'Connection Timeout=30;'
        )

        # Encode the ODBC string
        encoded_odbc_str = quote_plus(odbc_str)

        # Build the SQLAlchemy connection string
        auth = f'mssql+pyodbc:///?odbc_connect={encoded_odbc_str}'

        # Create the engine with optimized settings
        engine = sql.create_engine(
            auth,

            pool_size=10,
            max_overflow=20,
            pool_timeout=30,
            pool_recycle=3600
        )
    elif creds == 'azure':
        connection_string = (
                f"mssql+pyodbc://{db_user}:{db_pass}@{db_server}/{db_name}?"
                "driver=ODBC+Driver+17+for+SQL+Server&authentication=ActiveDirectoryPassword"
                )
        engine = sql.create_engine(
                connection_string,
                max_identifier_length=128,
                fast_executemany=True,
                pool_size=10,  # Number of connections to keep in the pool
                max_overflow=20,  # Extra connections allowed if the pool is full
                pool_timeout=30,  # Time to wait for a connection from the pool
                pool_recycle=3600  # Timeout to recycle connections, avoids stale ones
            )
    else:
        raise ValueError(f"Unsupported credentials: {creds}")

    # Establish the connection
    conn = engine.connect()

    # Return the requested objects
    if return_engine and return_string:
        return conn, engine, auth
    elif return_engine:
        return conn, engine
    elif return_string:
        return conn, auth
    else:
        return conn

def query_reader(query, mode='many', nrows=100, creds='oracle_pu'):
    with conn_creator(creds) as conn:
        conn.autocommit = False
        # set_date_format = "ALTER SESSION SET NLS_DATE_FORMAT = 'DD/MM/YYYY'"
        # conn.execute(set_date_format)
        result = conn.execute(sql.text(query))
        try:
            if mode == 'all':
                df = DataFrame(result.fetchall(), columns=result.keys())
            else:
                df = DataFrame(result.fetchmany(nrows), columns=result.keys())
            return df
        except Exception as e:
            print(e)
        conn.close()


def send_to_oracle(resultado, dbase, dtypes, index=False, if_exists='append'):
    """Adjunta el dataframe resultado a la base de datos."""
    with conn_creator() as conn:
        resultado.to_sql(dbase, conn, dtype=dtypes, index=index, if_exists=if_exists)
