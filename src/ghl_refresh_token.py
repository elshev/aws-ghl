import datetime
import logging
import json
from http import HTTPStatus
from urllib.parse import urlencode
import urllib3

from AppConfig import AppConfig
from AwsSsmClient import AwsSsmClient
from Util import Util


logger = logging.getLogger()
logger.setLevel(logging.INFO)
ssm_client = AwsSsmClient()


def time_to_str(date_time):
    if not isinstance(date_time, datetime.date):
        date_time = datetime.datetime.now()
    return date_time.strftime('%Y%m%d-%H%M%S')


def ghl_refresh_token():
    '''
    Refreshes Access Token as described here: https://highlevel.stoplight.io/docs/integrations/00d0c0ecaa369-get-access-token.
    Stores new Access and Refresh Tokens in SSM Parameter Store
    '''
    url = f'{AppConfig.get_ghl_base_url()}/oauth/token'
    refresh_token = ssm_client.get_ghl_refresh_token()
    client_id = ssm_client.get_ghl_client_id()
    client_secret = ssm_client.get_ghl_client_secret()
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    request_body = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }
    body = urlencode(request_body)

    logger.info('Making Refresh Token API Call to %s ...', url)
    http = urllib3.PoolManager()
    response = http.request('POST', url, headers=headers, body=body)
    data = json.loads(response.data.decode('utf-8'))
    result = {
        'status': response.status,
        'reason': response.reason,
        'data': data
    }

    if AppConfig.is_local_execution():
        logger.info('Response:\n %s', result)

    if response.status == HTTPStatus.OK:
        access_token = data['access_token']
        refresh_token = data['refresh_token']
        expires_in = int(data['expires_in']) - 10
        expire_date = datetime.datetime.now() + datetime.timedelta(seconds=expires_in)
        if AppConfig.is_local_execution():
            logger.info('Access Token: %s', access_token)
            logger.info('Access Token Expire: %s', expire_date.isoformat())
            logger.info('Refresh Token: %s', refresh_token)
        ssm_client.set_ghl_access_token(access_token)
        ssm_client.set_ghl_refresh_token(refresh_token)
        ssm_client.set_ghl_access_token_expire(expire_date.isoformat())
        logger.info('Success! Access Token, Refresh Token, Access Token Expire were successfully updated in SSM Parameter Store')

    return result


def handler(event, context):
    Util.log_lambda_event(event, context)

    ghl_refresh_token()
