from dataclasses import dataclass
from datetime import (
    datetime
)
from typing import (
    Any
)
from GhlBaseMessage import GhlBaseMessage


@dataclass
class GhlOutboundMessage(GhlBaseMessage):

    @staticmethod
    def from_dict(event: Any) -> 'GhlOutboundMessage':
        if not GhlBaseMessage.is_outbound_message(event):
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
    

    def to_dict(self):
        result = super().to_dict()
        return result