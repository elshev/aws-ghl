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
import ghl_refresh_token
import ghl_hook

CONFIG_DIR = './config'
LOG_DIR = './logs'

httpclient_logger = logging.getLogger("http.client")

def httpclient_logging_patch(level=logging.DEBUG):
    """Enable HTTPConnection debug logging to the logging framework"""

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

def main():
    setup_logging()

    logging.debug('START!!!')

    directory = os.getcwd()
    logging.info('CWD = %s', directory)

    start_date = datetime.utcnow().date() + timedelta(days=-1)
    end_date = datetime.utcnow()
    mg_client = MgClient()
    messages = mg_client.get_messages(begin_date=start_date, end_date=end_date)
    logging.info(json.dumps(messages, indent=2))
    
    # ghl_hook.lambda_handler(conversationUnreadUpdateBody, None)
    # ghl_refresh_token.lambda_handler(event, None)

    logging.debug('FINISH!!!')

if __name__ == '__main__':
    main()
