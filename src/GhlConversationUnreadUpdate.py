from dataclasses import dataclass
from typing import (
    Any, 
    Mapping
)


@dataclass
class GhlConversationUnreadUpdate:
    type: str
    location_id: str
    id: str
    contact_id: str
    deleted: str
    inbox: str
    unread_count: str

    @staticmethod
    def from_dict(event: Any) -> 'GhlConversationUnreadUpdate':
        if not GhlConversationUnreadUpdate.is_conversation_unread_update(event):
            return None
        _type = str(event.get("type"))
        _location_id = str(event.get("locationId"))
        _id = str(event.get("id"))
        _contact_id = str(event.get("contactId"))
        _deleted = bool(event.get("deleted"))
        _inbox = bool(event.get("inbox"))
        _unread_count = int(event.get("unreadCount"))
        return GhlConversationUnreadUpdate(
            type=_type,
            location_id=_location_id,
            id=_id,
            contact_id=_contact_id,
            deleted=_deleted,
            inbox=_inbox,
            unread_count=_unread_count
        )
    
    @staticmethod
    def is_conversation_unread_update(event: Any):
        if not isinstance(event, Mapping):
            return False
        event_type = str(event.get('type'))
        return event_type == 'ConversationUnreadUpdate'
