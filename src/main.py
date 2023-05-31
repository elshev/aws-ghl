import os
from datetime import datetime, timedelta
import json
import logging
import logging.config
import http.client
import time
from AppConfig import AppConfig
from AwsS3Client import AwsS3Client
from AwsSqsClient import AwsSqsClient
from AwsStsClient import AwsStsClient
from GhlOutboundMessage import GhlOutboundMessage
from MgClient import MgClient
from MgMessage import MgMessage
from Util import Util
import mg_process_mailgun_events_queue
import mg_process_mailgun_events
import ghl_refresh_token
import ghl_hook

CONFIG_DIR = './config'
LOG_DIR = './logs'

httpclient_logger = logging.getLogger("http.client")

def httpclient_logging_patch(level=logging.DEBUG):
    """
    Enable HTTPConnection debug logging to the logging framework
    https://stackoverflow.com/questions/16337511/log-all-requests-from-the-python-requests-module
    """

    def httpclient_log(*args):
        httpclient_logger.log(level, " ".join(args))

    # mask the print() built-in in the http.client module to use logging instead
    http.client.print = httpclient_log
    # enable debugging
    http.client.HTTPConnection.debuglevel = 1
    
def setup_logging():
    httpclient_logging_patch()
    
    print(os.getcwd())
    log_configs = {'dev': 'logging.dev.ini', 'prod': 'logging.prod.ini'}
    config = log_configs.get(os.environ['STAGE'], log_configs['dev'])
    config_path = '/'.join([CONFIG_DIR, config])

    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')

    logging.config.fileConfig(
        config_path,
        disable_existing_loggers=False,
        defaults={'logfilename': f'{LOG_DIR}/{timestamp}.log'},
    )


contactCreateBody = {
    'type': 'ContactCreate',
    'locationId': 'locacion123',
    'id': 'id12345',
    'email': 'mail@example.com',
    'country': 'US',
    'firstName': 'John',
    'lastName': 'Testoff'
}

inboundSmsBody = {
  "type": "InboundMessage",
  "locationId": "dFUlfpB0VzwguRGR3IB3",
  "attachments": [],
  "body": "Test Inbound SMS from local",
  "contactId": "yQt7wzy5pVDbds94pEpq",
  "contentType": "text/plain",
  "conversationId": "jnHaVcGxKq6OEkIJDd6q",
  "dateAdded": "2023-05-31T11:31:45.750Z",
  "direction": "inbound",
  "messageType": "SMS"
}

outboundSmsBody = {
    "type": "OutboundMessage",
    "locationId": "dFUlfpB0VzwguRGR3IB3",
    "attachments": [],
    "body": "\"SMS\" Message Test",
    "contactId": "yQt7wzy5pVDbds94pEpq",
    "contentType": "text/plain",
    "conversationId": "jnHaVcGxKq6OEkIJDd6q",
    "dateAdded": "2023-05-22T06:51:16.000Z",
    "direction": "outbound",
    "messageType": "SMS",
    "userId": "8tMrecTfd0N6egSO3bYT"
}

ghlEvent = {
    'resource': '/gohighlevel',
    'path': '/gohighlevel',
    'httpMethod': 'POST',
    'headers': {
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json;charset=utf-8',
        'Host': 'sxmz4whd3h.execute-api.us-east-1.amazonaws.com',
        'User-Agent': 'axios/0.21.1'
    },
    'queryStringParameters': '',
    'requestContext': {
        'resourceId': '5lllcr',
        'resourcePath': '/gohighlevel',
        'httpMethod': 'POST'
    },
    'body': json.dumps(outboundSmsBody),
    'isBase64Encoded': False
}


def get_mailgun_messages(begin_date=None):
    if not begin_date:
        begin_date = datetime.utcnow().date()# + timedelta(days=-1)
    mg_client = MgClient()
    
    messages = mg_client.get_messages(begin_date=begin_date)

    messages_json = json.dumps(messages, indent=2)
    logging.info(messages_json)
    output_file_path = f'{LOG_DIR}/{datetime.now().strftime("%Y%m%d-%H%M%S")}-message.json'
    logging.info(f'Dumpping messages to the file: "{output_file_path}"')
    with open(output_file_path, 'w') as output_file:
        output_file.write(messages_json)


def get_mailgun_message_mime(message_url):
    mg_client = MgClient()
    message: MgMessage = mg_client.get_mime_message(message_url=message_url)
    output_file_path = f'{LOG_DIR}/{datetime.now().strftime("%Y%m%d-%H%M%S")}-message.eml'
    logging.info(f'Dumpping MIME to the file: "{output_file_path}"')
    Util.write_file(output_file_path, message.body_mime, newline='\n')


def process_mailgun_events():
    begin_date = datetime.utcnow().date() + timedelta(days=-1)
    end_date = datetime.utcnow().date() + timedelta(days=1)
    event = {
        'begin_date': begin_date.isoformat(),
        'end_date': end_date.isoformat()
    }
    event = {
        'begin_date': '2023-05-30T09:00:00',
        'end_date': '2023-05-31T23:59:59'
    }
    mg_process_mailgun_events.handler(event=event, context=None)


def get_message_from_queue():
    sqs_client = AwsSqsClient()
    sqs_response = sqs_client.get_from_mailgun_events_queue()
    messages = sqs_response.get('Messages')
    if not messages:
        return None
    message = sqs_response['Messages'][0]
    return message


def process_mailgun_events_queue():
    logging.info('Getting a message from the Queue...')
    message = get_message_from_queue()
    if not message:
        logging.info('Messages were not found in SQS. Exiting...')
        return
    logging.info('Message was found in SQS response.')
    event = { 'Records': [message] }

    mg_process_mailgun_events_queue.handler(event=event, context=None)


def main():
    setup_logging()

    logging.debug('START!!!')

    directory = os.getcwd()
    logging.info('CWD = %s', directory)

    # process_mailgun_events()

    # sleep_seconds = 3
    # logging.info('Sleeping for %s seconds', sleep_seconds)
    # time.sleep(sleep_seconds)
    
    # process_mailgun_events_queue()

    ghl_hook.handler(inboundSmsBody, None)
    # ghl_refresh_token.handler({}, None)

    logging.debug('FINISH!!!')

if __name__ == '__main__':
    main()
