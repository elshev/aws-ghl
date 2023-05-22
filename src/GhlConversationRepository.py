import json
import logging
import urllib3
from AppConfig import AppConfig
from AwsSsmClient import AwsSsmClient

class GhlConversationRepository:
    @property
    def location_id(self):
        return self._location_id

    def __init__(self, location_id) -> None:
        self._ssm_client = AwsSsmClient()
        self._ghl_api_version = '2021-07-28'
        self._location_id = location_id
        self._logger = logging.getLogger()
        self._base_url = AppConfig.get_ghl_base_url()


    def get_access_token(self):
        return AppConfig.get_ghl_access_token()


    def ghl_request(self, path):
        url = self._base_url + path
        access_token = self.get_access_token()
        common_headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}',
            'Version': '2021-04-15'
        }

        self._logger.info('Making API Call to %s ...', url)
        http = urllib3.PoolManager(headers=common_headers)

        response = http.request("GET", url)
        data = json.loads(response.data)

        log_value = {
            'status': response.status,
            'reason': response.reason,
            'body': data
        }
        self._logger.info('Response:\n%s ...', log_value)

        return data

    def get_by_id(self, conversation_id):
        api_path = f'/conversations/{conversation_id}'
        return self.ghl_request(api_path)

    def search(self, conversation_id):
        api_path = f'/conversations/search?locationId={self.location_id}&Version={self._ghl_api_version}&id={conversation_id}'
        return self.ghl_request(api_path)
