from dataclasses import dataclass
from typing import Any
    
contactBody = {
    'id': 'yQt7wzy5pVDbds94pEpq',
    'locationId': 'dFUlfpB0VzwguRGR3IB3',
    'type': 'lead',
    'firstName': 'Alex01',
    'lastName': 'Test01',
    'country': 'US',
    'email': 'alexander.shevchenko+01@toptal.com',
    'phone': '+79263900456',
    'dnd': False,
    'dateAdded': '2023-04-26T06:10:06.248Z'
}

@dataclass
class GhlContact:
    id: str
    location_id: str
    type: str
    first_name: str
    last_name: str
    country: str
    email: str
    phone: str
    dnd: str
    date_added: str

    @staticmethod
    def from_dict(event: Any) -> 'GhlContact':
        _id = str(event.get('id'))
        _location_id = str(event.get('locationId'))
        _type = str(event.get('type'))
        _first_name = str(event.get('firstName'))
        _last_name = str(event.get('lastName'))
        _country = str(event.get('country'))
        _email = str(event.get('email'))
        _phone = str(event.get('phone'))
        _dnd = bool(event.get('dnd'))
        _date_added = str(event.get('dateAdded'))
        return GhlContact(
            id=_id,
            location_id=_location_id,
            type=_type,
            first_name =_first_name,
            last_name =_last_name,
            country=_country,
            email=_email,
            phone = _phone,
            dnd=_dnd,
            date_added=_date_added
        )
