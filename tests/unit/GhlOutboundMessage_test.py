from GhlOutboundMessage import GhlOutboundMessage

outboundMessageBody = {
    "type": "OutboundMessage",
    "locationId": "dFUlfpB0VzwguRGR3IB3",
    "attachments": [],
    "body": "\"SMS\" Message Test",
    "contactId": "yQt7wzy5pVDbds94pEpq",
    "contentType": "text/plain",
    "conversationId": "jnHaVcGxKq6OEkIJDd6q",
    "dateAdded": "2023-05-22T06:51:16.000Z",
    "direction": "outbound",
    "messageType": "SMS",
    "userId": "8tMrecTfd0N6egSO3bYT"
}


class TestIsOutboundMessage():
    """
    Tests the is_outbound_message() method
    """

    def test_is_outbound_message(self):
        """
        Tests that the is_outbound_message() function returns True for OutboundMessage objects and false for others
        For brevity sake, many tests are joined into one
        """
        # Arrange
        # Act
        #Assert
        assert GhlOutboundMessage.is_outbound_message(None) is False
        assert GhlOutboundMessage.is_outbound_message(10) is False
        assert GhlOutboundMessage.is_outbound_message({}) is False
        assert GhlOutboundMessage.is_outbound_message({'typ': 'OutboundMessage'}) is False
        assert GhlOutboundMessage.is_outbound_message(outboundMessageBody) is True
        assert GhlOutboundMessage.is_outbound_message({'type': 'OutboundMessage'}) is True
        assert GhlOutboundMessage.is_outbound_message({'firstKey': 'SomeValue', 'type': 'OutboundMessage'}) is True
