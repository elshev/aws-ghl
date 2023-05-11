import os
from datetime import datetime, timedelta
import json
import logging
import logging.config
import http.client
from AppConfig import AppConfig
from AwsS3Client import AwsS3Client
from AwsStsClient import AwsStsClient
from MgClient import MgClient
from MgMessage import MgMessage
import mg_store_messages
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


ghlEventBody = {
    'type': 'ContactCreate',
    'locationId': 'locacion123',
    'id': 'id12345',
    'email': 'mail@example.com',
    'country': 'US',
    'firstName': 'John',
    'lastName': 'Testoff'
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
    'body': json.dumps(ghlEventBody),
    'isBase64Encoded': False
}

conversationUnreadUpdateBody = {
    'type': 'ConversationUnreadUpdate',
    'locationId': 'dFUlfpB0VzwguRGR3IB3',
    'id': 'VH12UQXitFFdkA7tC6wX',
    'contactId': 'X1PraMGEWrprg9GoJAZp',
    'deleted': False,
    'inbox': True,
    'unreadCount': 0
}


def get_messages(begin_date=None):
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


def get_message_mime(message_url):
    mg_client = MgClient()
    message: MgMessage = mg_client.get_mime_message(message_url=message_url)
    output_file_path = f'{LOG_DIR}/{datetime.now().strftime("%Y%m%d-%H%M%S")}-message.eml'
    logging.info(f'Dumpping MIME to the file: "{output_file_path}"')
    with open(output_file_path, 'w', newline='\n') as output_file:
        output_file.write(message.body_mime)
        


def main():
    setup_logging()

    logging.debug('START!!!')

    directory = os.getcwd()
    logging.info('CWD = %s', directory)

    simple_message_url = 'https://storage-us-east4.api.mailgun.net/v3/domains/send.dignamail.com/messages/BAABAAUClIpJD1mBTJFBUI8k9O1umS99Yw=='
    image_message_url = 'https://storage-us-east4.api.mailgun.net/v3/domains/send.dignamail.com/messages/BAABAQXnBYIdw7zaAqhGtojzqVlAljyQZA=='
    reply_with_image_attachment_url = 'https://storage-us-west1.api.mailgun.net/v3/domains/send.dignamail.com/messages/BAABAQUlwG92Py50ElpITJuKKR_LQV1AYQ=='
    message_url = reply_with_image_attachment_url
    # get_mime_message_to_file(message_url)
    # get_message_mime(message_url=message_url)
    # get_messages()
    # get_messages_mime()
    
    mg_store_messages.handler({}, None)

    # ghl_hook.lambda_handler(conversationUnreadUpdateBody, None)
    # ghl_refresh_token.lambda_handler(event, None)

    logging.debug('FINISH!!!')

if __name__ == '__main__':
    main()
