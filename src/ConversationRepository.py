import json
import logging
import urllib3
from AwsSsmClient import AwsSsmClient

GHL_HOSTNAME = 'https://services.leadconnectorhq.com'

class ConversationRepository:
    @property
    def location_id(self):
        return self._location_id

    def __init__(self, location_id) -> None:
        self._ssm_client = AwsSsmClient()
        self._ghl_api_version = '2021-07-28'
        self._location_id = location_id
        self._logger = logging.getLogger()
        self._base_url = GHL_HOSTNAME

    def get_access_token(self):
        return self._ssm_client.get_access_token()


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
        result = {
            'status': response.status,
            'reason': response.reason,
            'body': data
        }

        return result

    def get_by_id(self, conversation_id):
        api_path = f'/conversations/{conversation_id}'
        return self.ghl_request(api_path)

    def search_by_id(self, conversation_id):
        api_path = f'/conversations/search?locationId={self.location_id}&Version={self._ghl_api_version}&id={conversation_id}'
        return self.ghl_request(api_path)