"""
Creado el 30/3/2023 a las 3:34 p. m.

@author: jacevedo
"""
from msal import ConfidentialClientApplication
from msrest.authentication import Authentication
from datetime import datetime, timedelta
from dateutil import tz
from azure.cosmosdb.table.tableservice import TableService
import requests
import json

def read_dynamics365(table_name, start_date, end_date, columns=None, filters=None):
    # MSAL credentials
    tenant_id = 'your_tenant_id'
    client_id = 'your_client_id'
    client_secret = 'your_client_secret'
    authority_url = f'https://login.microsoftonline.com/{tenant_id}'

    # Authentication
    app = ConfidentialClientApplication(client_id=client_id, client_credential=client_secret, authority=authority_url)
    result = app.acquire_token_for_client(scopes=['https://database.windows.net/.default'])
    credentials = Authentication(lambda: result['access_token'])

    # Date formatting
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('Eastern Standard Time')
    start_date = start_date.replace(tzinfo=from_zone).astimezone(to_zone).strftime('%Y-%m-%dT%H:%M:%SZ')
    end_date = end_date.replace(tzinfo=from_zone).astimezone(to_zone).strftime('%Y-%m-%dT%H:%M:%SZ')

    # Table service
    table_service = TableService(account_name='your_account_name', account_key='your_account_key')

    # Query construction
    filter_string = ''
    if filters:
        for key, value in filters.items():
            filter_string += f"{key} eq '{value}' and "
        filter_string = filter_string[:-5]

    query = f"Timestamp ge datetime'{start_date}' and Timestamp le datetime'{end_date}'"
    if filter_string:
        query += f" and {filter_string}"

    if not columns:
        columns = None

    # Execute query
    results = table_service.query_entities(table_name, filter=query, select=columns, num_results=-1, timeout=None, marker=None,
                                           next_partition_key=None, next_row_key=None, partition_key=None, row_key=None,
                                           custom_headers=None, **operation_kwargs)
    return results



def read_dynamics365_api(table_name, start_date, end_date, columns=None, filters=None):
    # Web API credentials
    tenant_id = 'your_tenant_id'
    client_id = 'your_client_id'
    client_secret = 'your_client_secret'
    resource = 'https://your_dynamics_instance.api.crm.dynamics.com'

    # Authentication
    url = f'https://login.microsoftonline.com/{tenant_id}/oauth2/token'
    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'resource': resource
    }
    response = requests.post(url, data=data)
    access_token = json.loads(response.text)['access_token']
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'OData-MaxVersion': '4.0',
        'OData-Version': '4.0'
    }

    # Date formatting
    start_date = datetime.strftime(start_date, '%Y-%m-%dT%H:%M:%S.%fZ')
    end_date = datetime.strftime(end_date, '%Y-%m-%dT%H:%M:%S.%fZ')

    # Query construction
    filter_string = ''
    if filters:
        for key, value in filters.items():
            filter_string += f"{key} eq '{value}' and "
        filter_string = filter_string[:-5]

    query = f"{table_name}?$filter=modifiedon ge {start_date} and modifiedon le {end_date}"
    if filter_string:
        query += f" and {filter_string}"
    if columns:
        select_string = ','.join(columns)
        query += f"&$select={select_string}"

    # Execute query
    url = f"{resource}/api/data/v9.1/{query}"
    response = requests.get(url, headers=headers)
    results = json.loads(response.text)['value']
    return results
