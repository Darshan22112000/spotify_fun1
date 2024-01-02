import pandas as pd
import requests
import json
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta
import msal
from config import Config

class PowerBi2():

    @classmethod
    def refresh_report(cls):
        # Replace with your values
        tenant_id = Config.tenant_id
        client_id = Config.client_id
        client_secret = Config.client_secret
        workspace_id = Config.workspace_id
        report_id = Config.report_id
        dataset_id = Config.dataset_id
        scope= ['https://analysis.windows.net/powerbi/api/.default']
        # Get OAuth token
        token_url = f'https://login.microsoftonline.com/{tenant_id}'
        app = msal.ConfidentialClientApplication(client_id, authority=token_url, client_credential=client_secret)
        result = app.acquire_token_for_client(scopes=scope)
        refresh_url = f'https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/datasets/{dataset_id}/refreshes?$top=1'
        if 'access_token' in result:
            access_token = result['access_token']
            header = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}'
            }
            api_call = requests.get(url=refresh_url, headers=header)
            result = api_call.json()['value']
            df = pd.DataFrame(result, columns=['requestId', 'id', 'refreshType', 'startTime', 'endTime', 'status'])
            df.set_index('id')

        if df['status'][0] == 'Unknown':
            return {
                'value': 0,
                'status': df['status'][0],
                'message':'Dataset is refreshing right now. Please wait until this refresh has finished to trigger a new one'
            }
        elif df['status'][0] == 'Disabled':
            return {
                'value': 0,
                'status': df['status'][0],
                'message': 'Kindly enable dataset refresh'
            }
        elif df['status'][0] == 'Failed':
            api_call = requests.post(url=refresh_url, headers=header)
            if api_call.status_code in [202, 200]:
                return {
                    'value': 1,
                    'status': df['status'][0],
                    'message': 'dataset refresh triggered'
                }
            else:
                return {
                    'value': 0,
                    'status': 'Failed after POST',
                    'message': 'dataset refresh failed'
                }
        elif df['status'][0] == 'Completed':
            api_call = requests.post(url=refresh_url, headers=header)
            if api_call.status_code in [202, 200]:
                return {
                    'value': 1,
                    'status': df['status'][0],
                    'message': 'dataset refresh triggered'
                }
            else:
                return {
                    'value': 0,
                    'status': 'Failed after POST',
                    'message': 'dataset refresh failed'
                }
        else:
            return {
                'value': 0,
                'status': df['status'][0],
                'message': 'not familiar with status, check logs'
            }

