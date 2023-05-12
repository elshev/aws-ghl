import datetime
import logging
import json
import os
from http import HTTPStatus
from urllib.parse import urlencode
import boto3
import urllib3

from AppConfig import AppConfig


GHL_REFRESH_TOKEN_SSM_PARAMETER_NAME = '/GHL/Dev/CurlWisdom/RefreshToken'
GHL_ACCESS_TOKEN_EXPIRE_SSM_PARAMETER_NAME = '/GHL/Dev/CurlWisdom/AccessTokenExpire'
GHL_CLIENT_ID_SSM_PARAMETER_NAME = '/GHL/Dev/CurlWisdom/ClientId'
GHL_CLIENT_SECRET_SSM_PARAMETER_NAME = '/GHL/Dev/CurlWisdom/ClientSecret'

GHL_HOSTNAME = 'https://services.leadconnectorhq.com'

logger = logging.getLogger()
logger.setLevel(logging.INFO)
ssm_client = boto3.client('ssm')


def time_to_str(date_time):
    if not isinstance(date_time, datetime.date):
        date_time = datetime.datetime.now()
    return date_time.strftime('%Y%m%d-%H%M%S')


def get_ssm_parameter(name):
    parameter = ssm_client.get_parameter(Name=name, WithDecryption=True)
    return parameter['Parameter']['Value']


def get_parameter(env_name, env_ssm_parameter_name):
    '''
    If 'env_name' exists in environment variables, returns its value
    Otherwise, goes to SSM Parameter Store and returns value for parameter with name = env_ssm_parameter_name
    '''
    result = ''
    if env_name in os.environ:
        result = os.environ[env_name]
    if result is None or result == '':
        result = get_ssm_parameter(env_ssm_parameter_name)
    return result


def update_ssm_parameter(name, value, value_type):
    if value_type is None or value_type == '':
        value_type = 'SecureString'
    ssm_client.put_parameter(
        Name=name,
        Value=value,
        Type=value_type,
        Overwrite=True
    )

def update_ssm_string_parameter(name, value):
    update_ssm_parameter(name, value, 'String')


def update_ssm_secure_string_parameter(name, value):
    update_ssm_parameter(name, value, 'SecureString')


def get_client_id():
    return get_parameter('GHL_CLIENT_ID', GHL_CLIENT_ID_SSM_PARAMETER_NAME)


def get_client_secret():
    return get_parameter('GHL_CLIENT_SECRET', GHL_CLIENT_SECRET_SSM_PARAMETER_NAME)


def get_refresh_token():
    return get_parameter('GHL_REFRESH_TOKEN', GHL_REFRESH_TOKEN_SSM_PARAMETER_NAME)


def ghl_refresh_token():
    '''
    Refreshes Access Token as described here: https://highlevel.stoplight.io/docs/integrations/00d0c0ecaa369-get-access-token.
    Stores new Access and Refresh Tokens in SSM Parameter Store
    '''
    url = GHL_HOSTNAME + '/oauth/token'
    refresh_token = get_refresh_token()
    client_id = get_client_id()
    client_secret = get_client_secret()
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
    logger.info('Response:\n %s', result)

    if response.status == HTTPStatus.OK:
        access_token = data['access_token']
        refresh_token = data['refresh_token']
        logger.info('Refresh Token: %s', refresh_token)
        expires_in = int(data['expires_in']) - 10
        expire_date = datetime.datetime.now() + datetime.timedelta(seconds=expires_in)
        expire_timestamp = datetime.datetime.timestamp(expire_date)
        update_ssm_string_parameter(AppConfig.GHL_ACCESS_TOKEN_SSM_PARAMETER_NAME, access_token)
        update_ssm_string_parameter(GHL_REFRESH_TOKEN_SSM_PARAMETER_NAME, refresh_token)
        update_ssm_string_parameter(GHL_ACCESS_TOKEN_EXPIRE_SSM_PARAMETER_NAME, str(expire_timestamp))

    return result


def lambda_handler(event, context):
    logger.info('Event: %s', event)
    if not context is None:
        logger.info('Context: %s', context)

    ghl_refresh_token()
