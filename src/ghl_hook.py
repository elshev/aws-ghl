from typing import Any, Mapping
import datetime
import logging
import json
import os
import boto3
from botocore.exceptions import ClientError
from ConversationRepository import ConversationRepository

from ConversationUnreadUpdate import ConversationUnreadUpdate


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
    conversation = conversation_repository.search_by_id(conversation_unread_update.id)
    logger.info('Search Conversation by ID result: \n%s', conversation)

    # write_to_s3(content)


