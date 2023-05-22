import json
import logging
import urllib3
from AppConfig import AppConfig
from AwsSsmClient import AwsSsmClient
from GhlBaseRepository import GhlBaseRepository

class GhlConversationRepository(GhlBaseRepository):

    @property
    def location_id(self):
        return self._location_id

    def __init__(self, location_id) -> None:
        super().__init__()
        self._location_id = location_id


    def get_by_id(self, conversation_id):
        api_path = f'/conversations/{conversation_id}'
        return self.ghl_request(api_path)


    def search(self, conversation_id):
        api_path = f'/conversations/search?locationId={self.location_id}&Version={self._ghl_api_version}&id={conversation_id}'
        return self.ghl_request(api_path)
