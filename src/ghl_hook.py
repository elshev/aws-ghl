import logging
import json
from AwsS3Client import AwsS3Client
from GhlContactRepository import GhlContactRepository
from GhlConversationRepository import GhlConversationRepository
from GhlConversationUnreadUpdate import GhlConversationUnreadUpdate
from GhlBaseMessage import (
    GhlBaseMessage,
    GhlEventType,
    GhlMessageType
)
from GhlInboundMessage import GhlInboundMessage
from GhlOutboundMessage import GhlOutboundMessage
from Util import Util


logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_body_from_event(event):
    is_api_event = 'httpMethod' in event and 'headers' in event and 'body' in event
    if is_api_event:
        value = event['body']
    else:
        value = event
    body = json.loads(value) if isinstance(value, str) else value
    return body


def handler(event, context):
    Util.log_lambda_event(event, context)
        
    body = get_body_from_event(event)
    if body != event:
        logger.info('Content: %s', body)

    event_type = body.get('type')
    if not event_type:
        logger.info('"type" key was not found in event. Exiting...')
        return
 
    if not GhlBaseMessage.is_sms(body):
        logger.info('Warning! The current message type does not equal to "%s".', GhlMessageType.SMS)
        return None

    sms: GhlBaseMessage
    if GhlBaseMessage.is_outbound_message(body):
        sms = GhlOutboundMessage.from_dict(body)
    else:
        sms = GhlInboundMessage.from_dict(body)
    if not sms:
        logger.info('Warning! The current message type is not "%s" or "%s".', GhlEventType.INBOUND, GhlEventType.OUTBOUND)
        return None

    ghl_contact_repository = GhlContactRepository()
    ghl_contact = ghl_contact_repository.get_by_id(sms.contact_id)
    sms.contact = ghl_contact
    
    s3_client = AwsS3Client()
    s3_client.upload_sms(sms)
    
    
    # conversation_unread_update = ConversationUnreadUpdate.from_dict(body)
    # logger.info(conversation_unread_update)

    # location_id = conversation_unread_update.location_id
    # contact_id = conversation_unread_update.contact_id

    # conversation_repository = ConversationRepository(location_id)
    # conversation = conversation_repository.search(conversation_unread_update.id)
    # logger.info('Search Conversation by ID result: \n%s', conversation)

    # s3_client = AwsS3Client()
    # s3_client.upload_conversation_to_s3(contact_id, conversation)

