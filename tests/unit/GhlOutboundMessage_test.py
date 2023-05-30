from datetime import datetime

from GhlOutboundMessage import GhlOutboundMessage

outboundMessageBody = {
    "type": "OutboundMessage",
    "locationId": "Location123",
    "contactId": "Contact123",
    "conversationId": "Conversation123",
    "userId": "User123",
    "messageType": "SMS",
    "direction": "outbound",
    "contentType": "text/plain",
    "body": "\"SMS\" Message Test",
    "attachments": [],
    "dateAdded": "2023-05-22T06:51:16.000Z"
}


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
        ghl_outbound_message = GhlOutboundMessage.from_dict(outboundMessageBody)
        
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


class TestToDict():
    """
    Tests the to_dict() method
    """

    def test_returns_object(self):
        """
        Tests that the from_dict() method returns a proper object with all fields
        """
        # Arrange
        ghl_outbound_message = GhlOutboundMessage.from_dict(outboundMessageBody)
        
        # Act
        dic = ghl_outbound_message.to_dict()
        
        # Assert
        assert ghl_outbound_message.type == dic['type']
        assert ghl_outbound_message.location_id == dic['locationId']
        assert ghl_outbound_message.contact_id == dic['contactId']
        assert ghl_outbound_message.content_type == dic['contentType']
        assert ghl_outbound_message.conversation_id == dic['conversationId']
        assert ghl_outbound_message.user_id == dic['userId']
        assert ghl_outbound_message.direction == dic['direction']
        assert ghl_outbound_message.message_type == dic['messageType']
        assert ghl_outbound_message.body == dic['body']
        assert ghl_outbound_message.date_added == datetime.fromisoformat(dic['dateAdded'])
