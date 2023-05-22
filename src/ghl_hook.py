import logging
import json
from AwsS3Client import AwsS3Client
from ConversationRepository import ConversationRepository
from ConversationUnreadUpdate import ConversationUnreadUpdate
from GhlOutboundMessage import GhlOutboundMessage
from Util import Util


logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_body_from_event(event):
    value = event.get('body', None)
    if value is None:
        value = event
    body = json.loads(value) if isinstance(value, str) else value
    return body


def process_outbound_message(body):
    outbound_message = GhlOutboundMessage.from_dict(body)
    if not outbound_message:
        return None



def handler(event, context):
    Util.log_lambda_event(event, context)
        
    body = get_body_from_event(event)
    if body != event:
        logger.info('Content: %s', body)

    event_type = body.get('type')
    if not event_type:
        logger.info('"type" entry was not found in event. Exiting...')
 
    
    
    if GhlOutboundMessage.is_outbound_message(body):
        process_outbound_message(body)
    else:
        logger.info('Event type = "%s" is not processed by this function. Exiting...', event_type)
        return

    # conversation_unread_update = ConversationUnreadUpdate.from_dict(body)
    # logger.info(conversation_unread_update)

    # location_id = conversation_unread_update.location_id
    # contact_id = conversation_unread_update.contact_id

    # conversation_repository = ConversationRepository(location_id)
    # conversation = conversation_repository.search(conversation_unread_update.id)
    # logger.info('Search Conversation by ID result: \n%s', conversation)

    # s3_client = AwsS3Client()
    # s3_client.upload_conversation_to_s3(contact_id, conversation)

