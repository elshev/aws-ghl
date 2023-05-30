from datetime import datetime

from GhlInboundMessage import GhlInboundMessage

inboundSmsBody = {
  "type": "InboundMessage",
  "locationId": "Location1234",
  "contactId": "Contact1234",
  "conversationId": "Conversation1234",
  "attachments": [],
  "body": "Test Inbound SMS from local",
  "contentType": "text/plain",
  "dateAdded": "2021-04-21T11:31:45.750Z",
  "direction": "inbound",
  "messageType": "SMS"
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
        ghl_inbound_message = GhlInboundMessage.from_dict(inboundSmsBody)
        
        # Assert
        assert ghl_inbound_message.type == 'InboundMessage'
        assert ghl_inbound_message.location_id == inboundSmsBody['locationId']
        assert ghl_inbound_message.contact_id == inboundSmsBody['contactId']
        assert ghl_inbound_message.content_type == inboundSmsBody['contentType']
        assert ghl_inbound_message.conversation_id == inboundSmsBody['conversationId']
        assert ghl_inbound_message.direction == inboundSmsBody['direction']
        assert ghl_inbound_message.message_type == inboundSmsBody['messageType']
        assert ghl_inbound_message.body == inboundSmsBody['body']
        date_added_str = inboundSmsBody['dateAdded'].replace('Z', '+00:00')
        date_added = datetime.fromisoformat(date_added_str)
        assert ghl_inbound_message.date_added == date_added


class TestToDict():
    """
    Tests the to_dict() method
    """

    def test_returns_object(self):
        """
        Tests that the from_dict() method returns a proper object with all fields
        """
        # Arrange
        ghl_inbound_message = GhlInboundMessage.from_dict(inboundSmsBody)
        
        # Act
        dic = ghl_inbound_message.to_dict()
        
        # Assert
        assert ghl_inbound_message.type == dic['type']
        assert ghl_inbound_message.location_id == dic['locationId']
        assert ghl_inbound_message.contact_id == dic['contactId']
        assert ghl_inbound_message.content_type == dic['contentType']
        assert ghl_inbound_message.conversation_id == dic['conversationId']
        assert ghl_inbound_message.user_id == dic['userId']
        assert ghl_inbound_message.direction == dic['direction']
        assert ghl_inbound_message.message_type == dic['messageType']
        assert ghl_inbound_message.body == dic['body']
        assert ghl_inbound_message.date_added == datetime.fromisoformat(dic['dateAdded'])
