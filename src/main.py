import os
from datetime import datetime
import json
import logging
import logging.config
import ghl_refresh_token
import ghl_hook


CONFIG_DIR = './config'
LOG_DIR = './logs'


def setup_logging():
    print(os.getcwd())
    log_configs = {'dev': 'logging.dev.ini', "prod": "logging.prod.ini"}
    config = log_configs.get(os.environ['STAGE'], log_configs['dev'])
    config_path = '/'.join([CONFIG_DIR, config])

    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')

    logging.config.fileConfig(
        config_path,
        disable_existing_loggers=False,
        defaults={'logfilename': f'{LOG_DIR}/{timestamp}.log'},
    )


eventBody = {
    'type': 'ContactCreate',
    'locationId': 'locacion123',
    'id': 'id12345',
    'email': 'mail@example.com',
    'country': 'US',
    'firstName': 'John',
    'lastName': 'Testoff'
}

event = {
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
    'body': json.dumps(eventBody),
    'isBase64Encoded': False
}

def main():
    setup_logging()

    logging.info('START!!!')

    directory = os.getcwd()
    logging.info('CWD = %s', directory)

    ghl_hook.lambda_handler(event, None)
    #ghl_refresh_token.lambda_handler(event, None)

    logging.info('FINISH!!!')

if __name__ == '__main__':
    main()
