import json
from ghl_hook import (
    get_body_from_event
)

BODY_KEY = 'body'


contactCreateBody = {
        'type': 'ContactCreate',
        'locationId': 'locacion123',
        'id': 'id12345',
        'email': 'mail@example.com',
        'country': 'US',
        'firstName': 'John',
        'lastName': 'Testoff'
    }

apiEvent = {
        'resource': '/gohighlevel',
        'path': '/gohighlevel',
        'httpMethod': 'POST',
        'headers': {
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json;charset=utf-8',
            'Host': 'sxmz4whd3h.execute-api.us-east-1.amazonaws.com',
            'User-Agent': 'axios/0.21.1'
        },
        'queryStringParameters': '',
        'requestContext': {
            'resourceId': '5lllcr',
            'resourcePath': '/gohighlevel',
            'httpMethod': 'POST'
        },
        BODY_KEY: contactCreateBody,
        'isBase64Encoded': False
    }


class TestGetBodyFromEvent():
    """
    Test the get_body_from_event() function
    """

    def test_event_doesnt_contain_body(self):
        """
        Test that the get_body_from_event() function returns the whole 'event' object if 'event' doesn't contain 'body'
        """
        # Arrange
        event = contactCreateBody

        # Act
        body = get_body_from_event(event)

        #Assert
        assert body == event


    def test_event_contains_body_as_dict(self):
        """
        Test that the get_body_from_event() function returns 'event.body' when event.body is 'dict'
        """
        # Arrange
        event = apiEvent
        event[BODY_KEY] = contactCreateBody

        # Act
        body = get_body_from_event(event)

        #Assert
        assert body == contactCreateBody


    def test_event_contains_body_as_string(self):
        """
        Test that the get_body_from_event() function returns 'event.body' when event.body is 'string'
        """
        # Arrange
        event = apiEvent
        event[BODY_KEY] = json.dumps(contactCreateBody)

        # Act
        body = get_body_from_event(event)

        #Assert
        assert body == contactCreateBody

