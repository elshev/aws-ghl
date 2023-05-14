import json
from datetime import (
    datetime,
    date,
    timedelta
)
import logging
from typing import Iterable
from urllib.parse import urlencode
import urllib3
from AppConfig import AppConfig
from MgEvent import MgEvent
from MgMessage import MgMessage

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

    def _log_response(self, response, message='Response:\n'):
        data = json.loads(response.data)

        log_value = {
            'status': response.status,
            'reason': response.reason,
            'body': json.dumps(data, indent=2)
        }
        self._logger.debug('%s%s', message, log_value)
    
    
    def get_domains(self):
        domains_url = f'{self._mg_base_url}/domains'
        common_headers = urllib3.make_headers(basic_auth=f'api:{self._mg_api_key}')

        self._logger.info('get_domains(): Making API Call to %s ...', domains_url)
        http = urllib3.PoolManager(headers=common_headers)

        response = http.request('GET', url=domains_url)
        self._log_response(response)
        data_json = json.loads(response.data)

        return data_json

    
    def get_common_headers(self):
        common_headers = urllib3.make_headers(basic_auth=f'api:{self._mg_api_key}')
        common_headers['Content-Type'] = 'application/x-www-form-urlencoded'
        return common_headers


    def get_events(self, begin_date, end_date=None, filter_event_type=MgEventType.ACCEPTED, limit=300) -> Iterable[MgEvent]:
        """Get Message Events from MailGun for a period of time.

        Args:
            begin_date (date): start of period
            end_date (date, optional): end of period. If not defined the current time will be taken. Defaults to None.

        Returns:
            dict: dictionary: "eventId": "Event"
            See https://documentation.mailgun.com/en/latest/api-events.html#events for details
        """
        
        self._logger.info('get_events(): Start Date = %s, End Date = %s', begin_date, end_date)
        begin_timestamp = MgClient._get_timestamp(begin_date)

        request_body = {
            'begin': begin_timestamp,
            'event': filter_event_type,
            'ascending': 'yes',
            'limit': limit
        }
        if end_date:
            end_timestamp = MgClient._get_timestamp(end_date)
            request_body['end'] = end_timestamp

        events_url = f'{self._mg_domain_url}/events'
        body = urlencode(request_body)
        url = f'{events_url}?{body}'
        self._logger.info('get_events(): Making API Call to %s ...', events_url)
        http = urllib3.PoolManager(headers=self.get_common_headers())
        response = http.request('GET', url=url)
        self._log_response(response)
        events_json = json.loads(response.data)
        
        result = []
        for item in events_json['items']:
            mg_event = MgEvent.from_dict(item)
            # Exclude service events
            if mg_event.recipient.startswith('https://') or '/inbound_webhook' in mg_event.recipient:
                continue
            result.append(mg_event)
        
        return result
        

    def get_message_urls(self, events_json, filter_event_type=MgEventType.ACCEPTED):
        """Extract message URLs from the events retrieved.

        Args:
            events_json (dict): json representation of Events

        Returns:
            dict: dictionary: "messageKey": "messageURL"
        """
        result = {}
        events = events_json.get('items')
        if not events:
            return result
        for event in events:
            if event.get('event') != filter_event_type:
                continue
            storage = event.get('storage')
            if not storage:
                continue
            message_key = storage['key']
            message_url = storage['url']
            if message_key and message_url:
                result[message_key] = message_url

        self._logger.info('Message URLs:\n%s', json.dumps(result, indent=2))
        return result

    
    def get_message(self, mg_event: MgEvent) -> MgMessage:
        self._logger.info('get_message(): Making API Call to %s ...', mg_event.message_url)
        
        http = urllib3.PoolManager(headers=self.get_common_headers())
        response = http.request('GET', url=mg_event.message_url)
        self._log_response(response)
        data_json = json.loads(response.data)
        
        result = MgMessage.from_dict(data_json)
        result.mg_event = mg_event
        
        return result

    def get_mime_message(self, mg_event: MgEvent) -> MgMessage:
        self._logger.info('get_message_mime(): Making API Call to %s ...', mg_event.message_url)
        
        headers = self.get_common_headers()
        headers['Accept'] = 'message/rfc2822'
        http = urllib3.PoolManager(headers=headers)
        response = http.request('GET', url=mg_event.message_url)
        data_json = json.loads(response.data)
        self._logger.debug(json.dumps(data_json, indent=2))

        result = MgMessage.from_dict(data_json)
        result.mg_event = mg_event
        
        return result

    def get_messages(self, begin_date, end_date=None, limit=300):
        """
        First calls get_events() to get Message Events from MailGun for a period of time.
        Then get Message URLs from event and get Messages from MailGun for each URL.

        Args:
            begin_date (date): start of period
            end_date (date, optional): end of period. If not defined the current time will be taken. Defaults to None.

        Returns:
            dict: dictionary: "messageId": "Message JSON"
            See https://documentation.mailgun.com/en/latest/api-sending.html#retrieving-stored-messages for details
        """

        # First get message events
        filter_event_type = MgEventType.ACCEPTED
        mg_events = self.get_events(begin_date=begin_date, end_date=end_date, filter_event_type=filter_event_type, limit=limit)

        # Extract Message URLs from events json
        result = []
        for mg_event in mg_events:
            message = self.get_message(message_url=mg_event.message_url)
            self._logger.debug(json.dumps(message, indent=2))
            result.append(message)
        
        return result


    def get_messages_mime(self, begin_date, end_date=None, limit=300) -> Iterable[MgMessage]:
        """Get Messages from MailGun for a period of time in MIME format

        Args:
            begin_date (date): start of period
            end_date (date, optional): end of period. If not defined the current time will be taken. Defaults to None.

        Returns:
            dict: dictionary: "messageUrl": "MIME string"
            See https://documentation.mailgun.com/en/latest/api-sending.html#retrieving-stored-messages for details
        """
        # First get message events
        filter_event_type = MgEventType.ACCEPTED
        mg_events = self.get_events(begin_date=begin_date, end_date=end_date, filter_event_type=filter_event_type, limit=limit)

        # Extract Message URLs from events json
        result = []
        for mg_event in mg_events:
            message = self.get_mime_message(mg_event=mg_event)
            result.append(message)
            # self._logger.debug(json.dumps(message, indent=2, default=vars))
        
        return result
