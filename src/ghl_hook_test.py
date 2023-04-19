import json

from ghl_hook import get_body_from_event

BODY_KEY = 'body'


def get_body():
    return {
        'type': 'ContactCreate',
        'locationId': 'locacion123',
        'id': 'id12345',
        'email': 'mail@example.com',
        'country': 'US',
        'firstName': 'John',
        'lastName': 'Testoff'
    }

def get_event():
    return {
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
        BODY_KEY: get_body(),
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
        event = get_body()

        # Act
        body = get_body_from_event(event)

        #Assert
        assert body == event


    def test_event_contains_body_as_dict(self):
        """
        Test that the get_body_from_event() function returns 'event.body' when event.body is 'dict'
        """
        # Arrange
        event = get_event()
        event[BODY_KEY] = get_body()

        # Act
        body = get_body_from_event(event)

        #Assert
        assert body == get_body()


    def test_event_contains_body_as_string(self):
        """
        Test that the get_body_from_event() function returns 'event.body' when event.body is 'string'
        """
        # Arrange
        event = get_event()
        event[BODY_KEY] = json.dumps(get_body())

        # Act
        body = get_body_from_event(event)

        #Assert
        assert body == get_body()
