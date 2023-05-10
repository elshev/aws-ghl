from enum import Enum
import inspect
import json
from datetime import (
    datetime,
    date,
    timedelta
)
import logging
import re
from urllib.parse import urlencode
import urllib3
from AppConfig import AppConfig

class MgEventType:
    ACCEPTED = 'accepted'
    DELIVERED = 'delivered'
    OPENED = 'opened'
    

class MgClient:

    def __init__(self) -> None:
        self._logger = logging.getLogger()
        self._mg_base_url = AppConfig.get_mailgun_api_url()
        self._mg_domain = AppConfig.get_mailgun_domain()
        self._mg_domain_url = f'{self._mg_base_url}/{self._mg_domain}'
        self._mg_api_key = AppConfig.get_mailgun_api_key()

    def _get_timestamp(dt):
        result_date = dt
        if type(result_date) == date:
            result_date = datetime(dt.year, dt.month, dt.day, 0, 0, 0)
        result = result_date.timestamp()
        return result


    def get_domains(self):
        domains_url = f'{self._mg_base_url}/domains'
        common_headers = urllib3.make_headers(basic_auth=f'api:{self._mg_api_key}')

        self._logger.info('get_domains(): Making API Call to %s ...', domains_url)
        http = urllib3.PoolManager(headers=common_headers)

        response = http.request('GET', url=domains_url)
        data = json.loads(response.data)

        log_value = {
            'status': response.status,
            'reason': response.reason,
            'body': data
        }
        self._logger.debug('Response:\n%s ...', log_value)

        return data
    
    def get_common_headers(self):
        common_headers = urllib3.make_headers(basic_auth=f'api:{self._mg_api_key}')
        common_headers['Content-Type'] = 'application/x-www-form-urlencoded'
        return common_headers
        

    def get_events(self, begin_date, end_date=None, event_type=MgEventType.ACCEPTED, limit=300):
        logging.debug('get_events(): Start Date = %s, End Date = %s', begin_date, end_date)
        begin_timestamp = MgClient._get_timestamp(begin_date)

        request_body = {
            'begin': begin_timestamp,
            'event': event_type,
            'ascending': 'yes',
            'limit': limit
        }
        if (end_date):
            end_timestamp = MgClient._get_timestamp(end_date)
            request_body['end'] = end_timestamp

        events_url = f'{self._mg_domain_url}/events'
        body = urlencode(request_body)
        url = f'{events_url}?{body}'
        self._logger.info('get_events(): Making API Call to %s ...', events_url)
        http = urllib3.PoolManager(headers=self.get_common_headers())
        response = http.request('GET', url=url)
        data = json.loads(response.data)

        log_value = {
            'status': response.status,
            'reason': response.reason,
            'body': data
        }
        logging.debug('Response:\n%s ...', log_value)

        return data

    def get_message(self, message_url):
        logging.debug('get_message(): URL = %s', message_url)

        self._logger.info('get_message(): Making API Call to %s ...', message_url)
        http = urllib3.PoolManager(headers=self.get_common_headers())
        response = http.request('GET', url=message_url)
        data = json.loads(response.data)

        log_value = {
            'status': response.status,
            'reason': response.reason,
            'body': json.dumps(data, indent=2)
        }
        logging.debug('get_message(): Response:\n%s ...', log_value)

        return data

    def extract_mime_from_response_json(response):
        body_mime = response["body-mime"]
        # Workaround for MailGun bug: 'body-mime' contains mixed line endings '\n' and '\r\n'
        # Replace single '\n' to '\r\n\' (but not '\n' in '\r\n')
        pattern = '(?<!\\r)\\n'
        replacement = '\r\n'
        result = re.sub(pattern, replacement, body_mime)
        return result
        

    def get_message_mime(self, message_url):
        method_name = inspect.currentframe().f_code.co_name
        logging.debug('%s(): URL = %s', method_name, message_url)

        self._logger.info('%s(): Making API Call to %s ...', method_name, message_url)
        headers = self.get_common_headers()
        headers['Accept'] = 'message/rfc2822'
        http = urllib3.PoolManager(headers=headers)
        response = http.request('GET', url=message_url)
        data = json.loads(response.data)

        log_value = {
            'status': response.status,
            'reason': response.reason,
            'body': json.dumps(data, indent=2)
        }
        logging.info('%s(): Response:\n%s ...', method_name, log_value)

        mime = MgClient.extract_mime_from_response_json(data)
        
        return mime

    def get_message_attachment(self, attachment_url):
        logging.debug('get_message_attachment(): URL = %s', attachment_url)

        self._logger.info('get_message_attachment(): Making API Call to %s ...', attachment_url)
        http = urllib3.PoolManager(headers=self.get_common_headers())
        response = http.request('GET', url=attachment_url)
        data = json.loads(response.data)

        log_value = {
            'status': response.status,
            'reason': response.reason,
            'body': json.dumps(data, indent=2)
        }
        logging.debug('get_message(): Response:\n%s ...', log_value)

        return data
        

    def get_messages(self, begin_date, end_date=None):
        result = {}
        events = self.get_events(begin_date=begin_date, end_date=end_date)
        for item in events['items']:
            event_type = item['event']
            if (event_type != MgEventType.ACCEPTED):
                continue
            storage = item['storage']
            message_url = storage['url']
            message = self.get_message(message_url=message_url)
            logging.debug(json.dumps(message, indent=2))
            message_id = message['Message-Id']
            result[message_id] = message
        
        return result
