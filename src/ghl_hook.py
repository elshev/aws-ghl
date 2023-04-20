import datetime
import logging
import json
import os
import boto3
import urllib3
from botocore.exceptions import ClientError

GHL_ACCESS_TOKEN_SSM_PARAMETER_NAME = '/GHL/Dev/CurlWisdom/AccessToken'
GHL_REFRESH_TOKEN_SSM_PARAMETER_NAME = '/GHL/Dev/CurlWisdom/RefreshToken'

logger = logging.getLogger()
logger.setLevel(logging.INFO)
s3_client = boto3.client('s3')
ssm_client = boto3.client('ssm')

def time_to_str(date_time):
    if not isinstance(date_time, datetime.date):
        date_time = datetime.datetime.now()
    return date_time.strftime('%Y%m%d-%H%M%S')


def get_s3_key_name():
    return f'{time_to_str(None)}.txt'


def get_tmp_file_path(file_name):
    tmp_folder_path = '/tmp'
    if not file_name.startswith(f'{tmp_folder_path}/'):
        return f'/tmp/{file_name}'
    return file_name


def remove_tmp_file(file_name):
    lambda_path = get_tmp_file_path(file_name)
    try:
        if os.path.isfile(lambda_path):
            os.remove(lambda_path)
        else:
            logger.error('Error: %s file not found', lambda_path)
    except OSError as e:
        logger.error('Error while removing file: %s - %s', e.filename, e.strerror)


def data_to_tmp_file(data, file_name):
    lambda_path = get_tmp_file_path(file_name)
    with open(lambda_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return lambda_path


def write_to_s3(data):
    bucket_name = 'test-489440259680'
    key_name = get_s3_key_name()
    s3_path = f'{bucket_name}/{key_name}'
    tmp_file_path = data_to_tmp_file(data, key_name)

    logger.info('Starting S3.putObject to %s ...', s3_path)
    try:
        response = s3_client.upload_file(tmp_file_path, bucket_name, key_name)
    except ClientError as e:
        logger.error(e)
        return False
    finally:
        remove_tmp_file(tmp_file_path)
    logger.info('Successfully saved object to %s', s3_path)
    logger.info('Response: %s', response)
    return True


def get_ssm_parameter(name):
    parameter = ssm_client.get_parameter(Name=name)
    return parameter['Parameter']['Value']


def update_ssm_parameter(name, value):
    ssm_client.put_parameter(
        Name=name,
        Overwrite=True,
        Value=value,
    )


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


def get_access_token():
    return get_parameter('GHL_ACCESS_TOKEN', GHL_ACCESS_TOKEN_SSM_PARAMETER_NAME)


def get_refresh_token():
    return get_parameter('GHL_REFRESH_TOKEN', GHL_REFRESH_TOKEN_SSM_PARAMETER_NAME)


def ghl_request(path):
    hostname = 'https://services.leadconnectorhq.com'
    url = hostname + path
    access_token = get_access_token()
    common_headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}',
        'Version': '2021-04-15'
    }

    logger.info('Making API Call to %s ...', url)
    http = urllib3.PoolManager(headers=common_headers)

    response = http.request("GET", url)
    response_body = response.data
    logger.info(response_body)
    result = {
        'status': response.status,
        'reason': response.reason,
        'body': response_body
    }
    logger.info('Response:\n %s', result)

    return result


def get_body_from_event(event):
    value = event.get('body', None)
    if value is None:
        value = event
    body = json.loads(value) if isinstance(value, str) else value
    return body


def lambda_handler(event, context):
    logger.info('Event: %s', event)
    if not context is None:
        logger.info('Context: %s', context)
    body = get_body_from_event(event)
    content = json.dumps(body)
    logger.info('Content: %s', content)

    api_path = '/conversations/9325cLcgqmhJVyfITS7g'
    ghl_request(api_path)

    write_to_s3(content)

