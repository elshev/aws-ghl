from dataclasses import dataclass
from typing import (
    Any, 
    Mapping
)

class GhlMessageType:
    EMAIL = 'EMAIL'
    SMS = 'SMS'
    

@dataclass
class GhlOutboundMessage:
    type: str
    location_id: str
    contact_id: str
    conversation_id: str
    user_id: str
    message_type: str
    direction: str
    content_type: str
    body: str
    date_added: str

    @staticmethod
    def from_dict(event: Any) -> 'GhlOutboundMessage':
        if not GhlOutboundMessage.is_outbound_message(event):
            return None
        _type = str(event.get("type"))
        _location_id = str(event.get("locationId"))
        _contact_id = str(event.get("contactId"))
        _conversation_id = str(event.get("conversationId"))
        _user_id = str(event.get("userId"))
        _message_type = str(event.get("messageType"))
        _direction = str(event.get("direction"))
        _content_type = str(event.get("contentType"))
        _body = str(event.get("body"))
        _date_added = str(event.get("dateAdded"))
        return GhlOutboundMessage(
            type=_type,
            location_id=_location_id,
            contact_id=_contact_id,
            conversation_id=_conversation_id,
            user_id=_user_id,
            message_type=_message_type,
            direction=_direction,
            content_type=_content_type,
            body=_body,
            date_added=_date_added
        )
    
    @staticmethod
    def is_outbound_message(event: Any):
        if not isinstance(event, Mapping):
            return False
        event_type = str(event.get('type'))
        return event_type == 'OutboundMessage'
