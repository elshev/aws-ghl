from dataclasses import dataclass
from datetime import (
    datetime
)
from typing import (
    Any, 
    Mapping
)

from GhlContact import GhlContact

class GhlEventType:
    INBOUND = 'InboundMessage'
    OUTBOUND = 'OutboundMessage'
    CONVERSATION_UNREAD_UPDATE = 'ConversationUnreadUpdate'
    
class GhlMessageType:
    EMAIL = 'EMAIL'
    SMS = 'SMS'
    

@dataclass
class GhlBaseMessage:
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
    def from_dict(event: Any) -> 'GhlBaseMessage':
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
        return GhlBaseMessage(
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
    def is_event_of_type(event, event_type: GhlEventType):
        if not isinstance(event, Mapping):
            return False
        event_message_type = str(event.get('type'))
        return event_message_type == event_type

    @staticmethod
    def is_outbound_message(event: Any):
        return GhlBaseMessage.is_event_of_type(event, GhlEventType.OUTBOUND)

    @staticmethod
    def is_inbound_message(event: Any):
        return GhlBaseMessage.is_event_of_type(event, GhlEventType.INBOUND)

    @staticmethod
    def is_sms(event):
        event_type = str(event.get('messageType'))
        return event_type == GhlMessageType.SMS

    @staticmethod
    def is_outbound_sms(event: Any):
        return GhlBaseMessage.is_outbound_message(event) and GhlBaseMessage.is_sms(event)

    @staticmethod
    def is_inbound_sms(event: Any):
        return GhlBaseMessage.is_inbound_message(event) and GhlBaseMessage.is_sms(event)


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
            'locationId': self.location_id,
            'contactId': self.contact_id,
            'conversationId': self.conversation_id,
            'userId': self.user_id,
            'fullName': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'messageType': self.message_type,
            'direction': self.direction,
            'contentType': self.content_type,
            'body': self.body,
            'dateAdded': self.date_added.isoformat()
        }
        return result