from datetime import datetime

import pytest
from GhlBaseMessage import GhlBaseMessage

outboundMessageBody = {
    "type": "OutboundMessage",
    "locationId": "dFUlfpB0VzwguRGR3IB3",
    "contactId": "yQt7wzy5pVDbds94pEpq",
    "conversationId": "jnHaVcGxKq6OEkIJDd6q",
    "userId": "8tMrecTfd0N6egSO3bYT",
    "messageType": "SMS",
    "direction": "outbound",
    "contentType": "text/plain",
    "body": "\"SMS\" Message Test",
    "attachments": [],
    "dateAdded": "2023-05-22T06:51:16.000Z"
}


class TestIsOutboundMessage():
    """
    Tests the is_outbound_message() method
    """

    def test_returns_proper_result(self):
        """
        Tests that the is_outbound_message() function returns True for OutboundMessage objects and false for others
        For brevity sake, many tests are joined into one
        """
        # Arrange
        # Act
        # Assert
        assert GhlBaseMessage.is_outbound_message(None) is False
        assert GhlBaseMessage.is_outbound_message(10) is False
        assert GhlBaseMessage.is_outbound_message({}) is False
        assert GhlBaseMessage.is_outbound_message({'typ': 'OutboundMessage'}) is False
        assert GhlBaseMessage.is_outbound_message(outboundMessageBody) is True
        assert GhlBaseMessage.is_outbound_message({'type': 'OutboundMessage'}) is True
        assert GhlBaseMessage.is_outbound_message({'firstKey': 'SomeValue', 'type': 'OutboundMessage'}) is True


class TestFromDict():
    """
    Tests the from_dict() method
    """

    def test_returns_object(self):
        """
        Tests that the from_dict() method returns a proper object with all fields
        """
        # Arrange
        
        # Act
        ghl_outbound_message = GhlBaseMessage.from_dict(outboundMessageBody)
        
        # Assert
        assert ghl_outbound_message.type == 'OutboundMessage'
        assert ghl_outbound_message.location_id == outboundMessageBody['locationId']
        assert ghl_outbound_message.contact_id == outboundMessageBody['contactId']
        assert ghl_outbound_message.content_type == outboundMessageBody['contentType']
        assert ghl_outbound_message.conversation_id == outboundMessageBody['conversationId']
        assert ghl_outbound_message.user_id == outboundMessageBody['userId']
        assert ghl_outbound_message.direction == outboundMessageBody['direction']
        assert ghl_outbound_message.message_type == outboundMessageBody['messageType']
        assert ghl_outbound_message.body == outboundMessageBody['body']
        date_added_str = outboundMessageBody['dateAdded'].replace('Z', '+00:00')
        date_added = datetime.fromisoformat(date_added_str)
        assert ghl_outbound_message.date_added == date_added


    def test_wrong_datetime(self):
        """
        Tests that the from_dict() method returns a proper object with all fields
        """
        # Arrange
        body_with_wrong_date = outboundMessageBody.copy()
        
        # Act
        # Assert
        body_with_wrong_date['dateAdded'] = 'abcdef'
        with pytest.raises(ValueError, match='Invalid isoformat string'):
            GhlBaseMessage.from_dict(body_with_wrong_date)

        body_with_wrong_date['dateAdded'] = '2023-15-02T06:51:16.000Z'
        with pytest.raises(ValueError, match='month must be in'):
            GhlBaseMessage.from_dict(body_with_wrong_date)
        
        body_with_wrong_date['dateAdded'] = '2023-05-00T06:51:16.000Z'
        with pytest.raises(ValueError, match='day is out of range for month'):
            GhlBaseMessage.from_dict(body_with_wrong_date)
