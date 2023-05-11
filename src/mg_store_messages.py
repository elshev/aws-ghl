from datetime import datetime, timedelta
import logging
import json
from typing import Dict, Iterable, List
from AwsS3Client import AwsS3Client
from MgClient import MgClient
from AppConfig import AppConfig
from MgMessage import MgMessage

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_messages_mime(begin_date=None) -> Iterable[MgMessage]:
    if not begin_date:
        begin_date = datetime.utcnow().date() + timedelta(days=-1)
    end_date = datetime.utcnow().date()
 
    mg_client = MgClient()
    messages = mg_client.get_messages_mime(begin_date=begin_date, end_date=end_date)
    # messages_json = json.dumps(messages, indent=2)
    # logging.debug(messages_json)

    return messages


def save_message_as_mime(message_key: str, message_mime: str):
        message_key = message_key.strip('=').lower()
        output_file_name = f'{datetime.now().strftime("%Y%m%d-%H%M%S")}-{message_key}.eml'
        output_file_path = AppConfig.get_temp_file_path(output_file_name)
        logging.info(f'Dumpping MIME to the file: "{output_file_path}"')
        with open(output_file_path, 'w', newline='\n') as output_file:
            output_file.write(message_mime)
    

def save_messages_as_mime(messages: Iterable[MgMessage]):
    for message in messages:
        message_key = message.url.rsplit('/', 1)[-1]
        message_mime = message.body_mime
        
        save_message_as_mime(message_key, message_mime)


def handler(event, context):
    logger.info('Event: %s', event)
    if not context is None:
        logger.info('Context: %s', context)

    messages = get_messages_mime()
    save_messages_as_mime(messages)

    s3_client = AwsS3Client()
    # s3_client.write_to_s3(location_id, contact_id, conversation)
