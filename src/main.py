import os
from datetime import datetime, timedelta
import json
import logging
import logging.config
import requests 
from AppConfig import AppConfig
from AwsS3Client import AwsS3Client
from AwsStsClient import AwsStsClient
from MgClient import MgClient
import ghl_refresh_token
import ghl_hook


CONFIG_DIR = './config'
LOG_DIR = './logs'

import http.client

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

def parse_email_messages(messages_string):
    """Usage:
    messages_str = '1st Reply Line #1 of 3 lines, created at 2023-05-03 10:51:00\n2nd Line #2 of Reply\n3rd Last Reply Line #3, 2023-05-03 10:51:00\n\n\n\nOn Tue, May 2, 2023 at 8:37 PM Alexander Shevchenko <alexander.shevchenko@toptal.com [alexander.shevchenko@toptal.com]> wrote:\n\n> First line of Reply created at 2023-05-02 20:36:54\n> Second line of the test Reply\n> 3rd line of Reply\n> \n> Best regards,\n> Alex Repliedoff, 2023-05-02 20:36:54\n> \n> \n> On Tue, May 2, 2023 at 9:23 AM <reply@send.dignamail.com [reply@send.dignamail.com]> wrote:\n> \n> > First line of Body created at 2023-05-02 09:22:41\n> > Second line of the test body\n> > 3rd line of Body \n> >  \n> > Best regards,\n> > John Testoff, 2023-05-02 09:22:41\n> > \n> >  \n> > \n> >  \n> > \n> > '
    messages = parse_email_messages(messages_str)
    for k, v in messages:
        print(f'{k}: {v}')
        print(32 * '-')
    """
    messages = []
    parts = messages_string.split('On ')
    for part in parts[1:]:
        lines = part.split('\n')
        date = datetime.strptime(lines[0].strip(), '%a, %b %d, %Y at %I:%M %p')
        body = '\n'.join(lines[2:-4]).strip()
        messages.append({'message_date': date, 'message_body': body})
    return messages

def mg_get(message_key):
    """View a message using it’s Mailgun storage key.

    Args:
        message_key (str): Message Key
    """

    mailgun_api_key = AppConfig.get_mailgun_api_key()
    output_file_path = f'{LOG_DIR}/message.eml' 
    domain = AppConfig.get_mailgun_domain()
    base_url = 'https://storage-us-east4.api.mailgun.net/v3'
    url = f'{base_url}/domains/{domain}/messages/{message_key}'
    # this will help us to get the raw MIME 
    headers = {'Accept': 'message/rfc2822'} 

    r = requests.get(url, auth=('api', mailgun_api_key), headers=headers) 

    if r.status_code == 200: 
        logging.info(f'Dumpping body to the file: "{output_file_path}"')
        with open(output_file_path, 'w') as message: 
            message.write(r.json()['body-mime']) 
    else: 
        logging.info(f'Oops! Something went wrong: {r.content}')

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
    
    # mg_get(message_key='BAABAAUUuvwGta7RJJ9Fy70BafdrjfXLYg==')

    # ghl_hook.lambda_handler(conversationUnreadUpdateBody, None)
    # ghl_refresh_token.lambda_handler(event, None)

    logging.debug('FINISH!!!')

if __name__ == '__main__':
    main()
