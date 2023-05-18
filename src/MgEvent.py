import json
from datetime import datetime
from typing import Any, Iterable
from dataclasses import dataclass

from Util import Util


@dataclass
class MgEvent:
    """ MailGun event """
    id: str
    timestamp: float
    sender: str
    recipient: str
    recipient_domain: str
    subject: str
    message_size: int
    sender_message_id: str
    event_type: str
    message_key: str
    message_url: str
    location_id: str

    @staticmethod
    def from_dict(obj: Any) -> 'MgEvent':
        _id = str(obj.get("id"))
        _timestamp = Util.get_dict_float_value(obj, ['timestamp'])
        _sender = Util.get_dict_value(obj, ['envelope', 'sender'])
        _recipient = str(obj.get("recipient"))
        _recipient_domain = str(obj.get("recipient-domain"))
        _subject = Util.get_dict_value(obj, ['message', 'headers', 'subject'])
        _message_size = Util.get_dict_int_value(obj, ['message', 'size'])
        _sender_message_id = Util.get_dict_value(obj, ['message', 'headers', 'message-id'])
        _event_type = str(obj.get("event"))
        _message_key = Util.get_dict_value(obj, ['storage', 'key'])
        _message_url = Util.get_dict_value(obj, ['storage', 'url'])
        _location_id = Util.get_dict_value(obj, ['user-variables', 'loc_id'])
        
        return MgEvent(
            id=_id,
            timestamp=_timestamp,
            sender=_sender,
            recipient=_recipient,
            recipient_domain=_recipient_domain,
            subject = _subject,
            message_size=_message_size,
            sender_message_id=_sender_message_id,
            event_type=_event_type,
            message_key=_message_key,
            message_url=_message_url,
            location_id=_location_id
        )
