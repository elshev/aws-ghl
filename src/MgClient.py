import json
from datetime import datetime, date
import logging
from urllib.parse import urlencode
import urllib3
from AppConfig import AppConfig

class MgClient:

    def __init__(self) -> None:
        self._logger = logging.getLogger()
        self._mg_base_url = AppConfig.get_mailgun_api_url()
        self._mg_domain = AppConfig.get_mailgun_domain()
        self._mg_domain_url = f'{self._mg_base_url}/{self._mg_domain}'
        self._mg_api_key = AppConfig.get_mailgun_api_key()

    def _get_timestamp(dt):
        result_date = dt
        if isinstance(result_date, date):
            result_date = datetime(dt.year, dt.month, dt.day, 0, 0, 0)
        return result_date.timestamp()


    def get_domains(self):
        domains_url = f'{self._mg_base_url}/domains'
        common_headers = urllib3.make_headers(basic_auth=f'api:{self._mg_api_key}')

        self._logger.info('Making API Call to %s ...', domains_url)
        http = urllib3.PoolManager(headers=common_headers)

        response = http.request('GET', url=domains_url)
        data = json.loads(response.data)

        log_value = {
            'status': response.status,
            'reason': response.reason,
            'body': data
        }
        self._logger.info('Response:\n%s ...', log_value)

        return data
    
    def get_events(self, begin_date, end_date):
        logging.info('Start Date = %s', begin_date)
        logging.info('End Date = %s', end_date)
        begin_timestamp = MgClient._get_timestamp(begin_date)
        end_timestamp = MgClient._get_timestamp(end_date)

        events_url = f'{self._mg_domain_url}/events'
        common_headers = urllib3.make_headers(basic_auth=f'api:{self._mg_api_key}')
        common_headers['Content-Type'] = 'application/x-www-form-urlencoded'

        request_body = {
            'begin': begin_timestamp,
            'end': end_timestamp,
            'events': 'accepted',
            'ascending': 'yes',
            'limit': 300,
            'pretty': 'yes',
        }
        body = urlencode(request_body)

        self._logger.info('Making API Call to %s ...', events_url)
        http = urllib3.PoolManager(headers=common_headers)

        response = http.request('GET', url=events_url, body=body)
        data = json.loads(response.data)

        log_value = {
            'status': response.status,
            'reason': response.reason,
            'body': data
        }
        self._logger.debug('Response:\n%s ...', log_value)

        return data
