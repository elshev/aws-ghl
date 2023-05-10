from datetime import datetime, timedelta
import logging
import json
from AwsS3Client import AwsS3Client
from MgClient import MgClient
from AppConfig import AppConfig

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_messages_mime(begin_date=None):
    if not begin_date:
        begin_date = datetime.utcnow().date()# + timedelta(days=-1)
 
    mg_client = MgClient()
    messages = mg_client.get_messages_mime(begin_date=begin_date)
    # messages_json = json.dumps(messages, indent=2)
    # logging.debug(messages_json)

    return messages


def save_message(message_key, message_mime):
        message_key = message_key.strip('=').lower()
        output_file_name = f'{datetime.now().strftime("%Y%m%d-%H%M%S")}-{message_key}.eml'
        output_file_path = AppConfig.get_temp_file_path(output_file_name)
        logging.info(f'Dumpping MIME to the file: "{output_file_path}"')
        with open(output_file_path, 'w', newline='\n') as output_file:
            output_file.write(message_mime)
    

def save_messages(messages):
    for message_url, message_mime in messages.items():
        message_key = message_url.rsplit('/', 1)[-1]
        save_message(message_key, message_mime)


def handler(event, context):
    logger.info('Event: %s', event)
    if not context is None:
        logger.info('Context: %s', context)

    mime_messages = get_messages_mime()
    save_messages(mime_messages)

    s3_client = AwsS3Client()
    # s3_client.write_to_s3(location_id, contact_id, conversation)
