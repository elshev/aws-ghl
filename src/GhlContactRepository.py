import json
import logging
import urllib3
from AppConfig import AppConfig
from AwsSsmClient import AwsSsmClient
from GhlBaseRepository import GhlBaseRepository
from GhlContact import GhlContact


class GhlContactRepository(GhlBaseRepository):

    def __init__(self) -> None:
        super().__init__()


    def get_by_id(self, contact_id):
        api_path = f'/contacts/{contact_id}'
        data = self.ghl_request(api_path)
        
        ghl_contact = GhlContact.from_dict(data['contact'])
        return ghl_contact
