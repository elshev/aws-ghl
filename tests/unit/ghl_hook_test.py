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

outboundSmsBody = {
    "type": "OutboundMessage",
    "locationId": "testLocation01",
    "contactId": "testContact01",
    "conversationId": "testConversation01",
    "userId": "testUser01",
    "messageType": "SMS",
    "direction": "outbound",
    "contentType": "text/plain",
    "body": "\"SMS\" Message Test",
    "attachments": [],
    "dateAdded": "2023-05-22T06:51:16.000Z"
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


    def test_event_contains_nested_body(self):
        """
        Test that the get_body_from_event() function returns 'event.body' when event.body also contains 'body' key
        """
        # Arrange
        event = apiEvent
        event[BODY_KEY] = json.dumps(outboundSmsBody)

        # Act
        body = get_body_from_event(event)

        #Assert
        assert body == outboundSmsBody


    def test_body_contains_nested_body(self):
        """
        Test that the get_body_from_event() function returns 'body' when body also contains 'body' key
        """
        # Arrange

        # Act
        body = get_body_from_event(outboundSmsBody)

        #Assert
        assert body == outboundSmsBody

