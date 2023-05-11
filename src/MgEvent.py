import json
from datetime import datetime
from typing import Any, Iterable
from dataclasses import dataclass


@dataclass
class MgEvent:
    """ MailGun event """
    id: str
    timestamp: float
    sender: str
    recipient: str
    subject: str
    message_size: int
    sender_message_id: str
    event_type: str
    message_key: str
    message_url: str

    @staticmethod
    def get_str_value(dic: dict, keys: Iterable[str]):
        cur_dict = dic
        for key in keys:
            val = cur_dict.get(key)
            if key == keys[-1]:
                return str(val)
            cur_dict = val
        return None

    @staticmethod
    def get_float_value(dic: dict, keys: Iterable[str]):
        s = MgEvent.get_str_value(dic, keys)
        try:
            return float(s)
        except ValueError:
            return None

    @staticmethod
    def get_int_value(dic: dict, keys: Iterable[str]):
        s = MgEvent.get_str_value(dic, keys)
        return int(s) if s.isdecimal() else None

    @staticmethod
    def from_dict(obj: Any) -> 'MgEvent':
        _id = str(obj.get("id"))
        _timestamp = MgEvent.get_float_value(obj, ['timestamp'])
        _sender = MgEvent.get_str_value(obj, ['envelope', 'sender'])
        _recipient = str(obj.get("recipient"))
        _subject = MgEvent.get_str_value(obj, ['message', 'headers', 'subject'])
        _message_size = MgEvent.get_int_value(obj, ['message', 'size'])
        _sender_message_id = MgEvent.get_str_value(obj, ['message', 'headers', 'message-id'])
        _event_type = str(obj.get("event"))
        _message_key = MgEvent.get_str_value(obj, ['storage', 'key'])
        _message_url = MgEvent.get_str_value(obj, ['storage', 'url'])
        
        return MgEvent(
            id=_id,
            timestamp=_timestamp,
            sender=_sender,
            recipient=_recipient,
            subject = _subject,
            message_size=_message_size,
            sender_message_id=_sender_message_id,
            event_type=_event_type,
            message_key=_message_key,
            message_url=_message_url
        )
