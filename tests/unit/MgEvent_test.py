from MgEvent import MgEvent

LOCATION_ID = 'SampleLocationID123'
MESSAGE_KEY_01 = 'Sample1Storage2Key3=='

ACCEPTED_EVENT_01 = {
    "timestamp": 1683700208.21084,
    "envelope": {
        "sender": "reply@send.senderdomain.com",
        "targets": "first.last+02@example.com",
        "transport": "smtp"
    },
    "flags": {
        "is-test-mode": False,
        "is-authenticated": True
    },
    "event": "accepted",
    "method": "HTTP",
    "id": "t0t_VgpZRz1234567-z77Q",
    "originating-ip": "1.2.3.4",
    "recipient": "first.last+02@example.com",
    "recipient-domain": "example.com",
    "storage": {
        "region": "us-west1",
        "env": "production",
        "key": MESSAGE_KEY_01,
        "url": f"https://storage-us-west1.api.mailgun.net/v3/domains/send.senderdomain.com/messages/{MESSAGE_KEY_01}"
    },
    "tags": None,
    "user-variables": {
        "c_id": "CId012345",
        "email_type": "campaign",
        "email_type_id": "645a1207cf49950c85eb44aa",
        "loc_id": "LOCATION_ID"
    },
    "log-level": "info",
    "message": {
        "size": 16002,
        "headers": {
            "message-id": "20230510063008.ac319c4df31914db@send.senderdomain.com",
            "to": "first.last+02@example.com",
            "subject": "Test Subject 01",
            "from": "TestSender <reply@send.senderdomain.com>"
        }
    }
}


class TestMgEvent():

    def test_from_dict(self):
        # Arrange
        event = ACCEPTED_EVENT_01
        # Act
        mg_event = MgEvent.from_dict(event)
        #Assert
        assert mg_event.id == event['id']
        assert mg_event.timestamp == event['timestamp']
        assert mg_event.sender == event['envelope']['sender']
        assert mg_event.recipient == event['recipient']
        assert mg_event.subject == event['message']['headers']['subject']
        assert mg_event.message_size == event['message']['size']
        assert mg_event.sender_message_id == event['message']['headers']['message-id']
        assert mg_event.event_type == event['event']
        assert mg_event.message_key == event['storage']['key']
        assert mg_event.message_url == event['storage']['url']

    def test_from_dict_with_wrong_values(self):
        # Arrange
        event = ACCEPTED_EVENT_01
        event['timestamp'] = '123a'
        event['message']['size'] = '123.45'
        # Act
        mg_event = MgEvent.from_dict(event)
        #Assert
        assert mg_event.id == event['id']
        assert mg_event.timestamp is None
        assert mg_event.message_size is None
