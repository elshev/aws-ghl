from dataclasses import dataclass
from datetime import (
    datetime
)
from typing import (
    Any, 
    Mapping
)

from GhlContact import GhlContact

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
    date_added: datetime
    contact: GhlContact = None

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
        _date_added_str = str(event.get("dateAdded")).replace('Z', '+00:00')
        _date_added = datetime.fromisoformat(_date_added_str)
        _contact = None
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
            date_added=_date_added,
            contact=_contact
        )
    
    @staticmethod
    def is_outbound_message(event: Any):
        if not isinstance(event, Mapping):
            return False
        event_type = str(event.get('type'))
        return event_type == 'OutboundMessage'

    @property
    def first_name(self):
        return self.contact.first_name if self.contact else None

    @property
    def last_name(self):
        return self.contact.last_name if self.contact else None

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def email(self):
        return self.contact.email if self.contact else None

    @property
    def phone(self):
        return self.contact.phone if self.contact else None

    def to_dict(self):
        result = {
            'type': self.type,
            'location_id': self.location_id,
            'contact_id': self.contact_id,
            'conversation_id': self.conversation_id,
            'user_id': self.user_id,
            'full_name': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'message_type': self.message_type,
            'direction': self.direction,
            'content_type': self.content_type,
            'body': self.body,
            'date_added': self.date_added.isoformat()
        }
        return result