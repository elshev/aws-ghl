from enum import Enum
import json
from datetime import datetime, date
import logging
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
        

    def get_events(self, begin_date, end_date, event_type=MgEventType.ACCEPTED, limit=300):
        logging.debug('get_events(): Start Date = %s, End Date = %s', begin_date, end_date)
        begin_timestamp = MgClient._get_timestamp(begin_date)
        end_timestamp = MgClient._get_timestamp(end_date)

        events_url = f'{self._mg_domain_url}/events'
        request_body = {
            'begin': begin_timestamp,
            'end': end_timestamp,
            'event': event_type,
            'ascending': 'yes',
            'limit': 300,
            'pretty': 'yes',
        }
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
        

    def get_messages(self, begin_date, end_date):
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
