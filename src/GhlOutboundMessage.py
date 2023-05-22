from dataclasses import dataclass
from typing import (
    Any, 
    Mapping
)

@dataclass
class GhlOutboundMessage:
    type: str
    location_id: str
    body: str
    contact_id: str
    content_type: str
    conversation_id: str
    date_added: str
    direction: str
    message_type: str
    user_id: str

    @staticmethod
    def from_dict(event: Any) -> 'GhlOutboundMessage':
        if not GhlOutboundMessage.is_outbound_message(event):
            return None
        _type = str(event.get("type"))
        _location_id = str(event.get("locationId"))
        _body = str(event.get("body"))
        _contact_id = str(event.get("contactId"))
        _content_type = str(event.get("contentType"))
        _conversation_id = str(event.get("conversationId"))
        _date_added = str(event.get("dateAdded"))
        _direction = str(event.get("direction"))
        _message_type = str(event.get("messageType"))
        _user_id = str(event.get("userId"))
        return GhlOutboundMessage(
            type=_type,
            location_id=_location_id,
            body=_body,
            contact_id=_contact_id,
            content_type=_content_type,
            conversation_id=_conversation_id,
            date_added=_date_added,
            direction=_direction,
            message_type=_message_type,
            user_id=_user_id
        )
    
    @staticmethod
    def is_outbound_message(event: Any):
        if not isinstance(event, Mapping):
            return False
        event_type = str(event.get('type'))
        return event_type == 'OutboundMessage'
