from GhlConversationUnreadUpdate import GhlConversationUnreadUpdate

conversationUnreadUpdateBody = {
    "type": "ConversationUnreadUpdate",
    "locationId": "dFUlfpB0VzwguRGR3IB3",
    "id": "VH12UQXitFFdkA7tC6wX",
    "contactId": "X1PraMGEWrprg9GoJAZp",
    "deleted": False,
    "inbox": True,
    "unreadCount": 0
}


class TestIsConversationUnreadUpdate():
    """
    Tests the is_conversation_unread_update() function
    """

    def test_returns_proper_result(self):
        """
        Tests that the is_conversation_unread_update() function returns True for ConversationUnreadUpdate objects and false for others
        For brevity sake, many tests are joined into one
        """
        # Arrange
        # Act
        #Assert
        assert GhlConversationUnreadUpdate.is_conversation_unread_update(None) is False
        assert GhlConversationUnreadUpdate.is_conversation_unread_update(10) is False
        assert GhlConversationUnreadUpdate.is_conversation_unread_update({}) is False
        assert GhlConversationUnreadUpdate.is_conversation_unread_update({'typ': 'ConversationUnreadUpdate'}) is False
        assert GhlConversationUnreadUpdate.is_conversation_unread_update(conversationUnreadUpdateBody) is True
        assert GhlConversationUnreadUpdate.is_conversation_unread_update({'type': 'ConversationUnreadUpdate'}) is True
        assert GhlConversationUnreadUpdate.is_conversation_unread_update({'firstKey': 'SomeValue', 'type': 'ConversationUnreadUpdate'}) is True