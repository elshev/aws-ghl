import logging
import json
from AwsS3Client import AwsS3Client
from GhlConversationRepository import GhlConversationRepository
from GhlConversationUnreadUpdate import GhlConversationUnreadUpdate
from GhlOutboundMessage import (
    GhlMessageType, 
    GhlOutboundMessage
)
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


def process_outbound_sms(outbound_sms: GhlOutboundMessage):
    if outbound_sms.message_type != GhlMessageType.SMS:
        raise ValueError('The current message type "%s" does not equal to "%s".', outbound_sms.message_type, GhlMessageType.SMS)

    return outbound_sms


def process_outbound_message(body):
    outbound_message = GhlOutboundMessage.from_dict(body)
    if not outbound_message:
        return None
    if outbound_message.message_type != GhlMessageType.SMS:
        logger.info('The current message type ("%s") is not currently processed by this function. Exiting...', outbound_message.message_type)
        return None
    
    result = process_outbound_sms(outbound_message)
    return result


def handler(event, context):
    Util.log_lambda_event(event, context)
        
    body = get_body_from_event(event)
    if body != event:
        logger.info('Content: %s', body)

    event_type = body.get('type')
    if not event_type:
        logger.info('"type" key was not found in event. Exiting...')
 
    
    outbound_sms = None
    if GhlOutboundMessage.is_outbound_message(body):
        outbound_sms = process_outbound_message(body)
    else:
        logger.info('Event type = "%s" is not processed by this function. Exiting...', event_type)
        return

    s3_client = AwsS3Client()
    s3_client.upload_outbound_sms(outbound_sms)
    
    
    # conversation_unread_update = ConversationUnreadUpdate.from_dict(body)
    # logger.info(conversation_unread_update)

    # location_id = conversation_unread_update.location_id
    # contact_id = conversation_unread_update.contact_id

    # conversation_repository = ConversationRepository(location_id)
    # conversation = conversation_repository.search(conversation_unread_update.id)
    # logger.info('Search Conversation by ID result: \n%s', conversation)

    # s3_client = AwsS3Client()
    # s3_client.upload_conversation_to_s3(contact_id, conversation)

