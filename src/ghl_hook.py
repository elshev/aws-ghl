from typing import Any, Mapping
import datetime
import logging
import json
import os
import boto3
import urllib3
from botocore.exceptions import ClientError

from ConversationUnreadUpdate import ConversationUnreadUpdate

GHL_ACCESS_TOKEN_SSM_PARAMETER_NAME = '/GHL/Dev/CurlWisdom/AccessToken'
GHL_REFRESH_TOKEN_SSM_PARAMETER_NAME = '/GHL/Dev/CurlWisdom/RefreshToken'

GHL_HOSTNAME = 'https://services.leadconnectorhq.com'

logger = logging.getLogger()
logger.setLevel(logging.INFO)
s3_client = boto3.client('s3')

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



class AwsSsmClient:

    def __init__(self) -> None:
        self._ssm_client = boto3.client('ssm')


    def get_ssm_parameter(self, name):
        parameter = self._ssm_client.get_parameter(Name=name)
        return parameter['Parameter']['Value']


    def update_ssm_parameter(self, name, value):
        self._ssm_client.put_parameter(
            Name=name,
            Overwrite=True,
            Value=value,
        )


    def get_parameter(self, env_name, env_ssm_parameter_name):
        '''
        If 'env_name' exists in environment variables, returns its value
        Otherwise, goes to SSM Parameter Store and returns value for parameter with name = env_ssm_parameter_name
        '''
        result = ''
        if env_name in os.environ:
            result = os.environ[env_name]
        if result is None or result == '':
            result = self.get_ssm_parameter(env_ssm_parameter_name)
        return result



class ConversationRepository:
    @property
    def location_id(self):
        return self._location_id
    
    def __init__(self, location_id) -> None:
        self._ssm_client = AwsSsmClient()
        self._ghl_api_version = '2021-07-28'
        self._location_id = location_id

    def get_access_token(self):
        return self._ssm_client.get_parameter('GHL_ACCESS_TOKEN', GHL_ACCESS_TOKEN_SSM_PARAMETER_NAME)


    def ghl_request(self, path):
        url = GHL_HOSTNAME + path
        access_token = self.get_access_token()
        common_headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}',
            'Version': '2021-04-15'
        }

        logger.info('Making API Call to %s ...', url)
        http = urllib3.PoolManager(headers=common_headers)

        response = http.request("GET", url)
        data = json.loads(response.data)
        result = {
            'status': response.status,
            'reason': response.reason,
            'body': data
        }
        logger.info('Response:\n %s', result)

        return result
    
    def get_by_id(self, conversation_id):
        api_path = f'/conversations/{conversation_id}'
        return self.ghl_request(api_path)

    def search_by_id(self, conversation_id):
        api_path = f'/conversations/search?locationId={self.location_id}&Version={self._ghl_api_version}&id={conversation_id}'
        return self.ghl_request(api_path)


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
    if body != event:
        logger.info('Content: %s', body)

    conversation_unread_update = ConversationUnreadUpdate.from_dict(body)
    logger.info(conversation_unread_update)

    location_id = conversation_unread_update.location_id

    conversation_repository = ConversationRepository(location_id)
    conversation_repository.search_by_id(conversation_unread_update.id)

    # write_to_s3(content)

