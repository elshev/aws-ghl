import logging
import json
from AwsS3Client import AwsS3Client
from ConversationRepository import ConversationRepository
from ConversationUnreadUpdate import ConversationUnreadUpdate


logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_body_from_event(event):
    value = event.get('body', None)
    if value is None:
        value = event
    body = json.loads(value) if isinstance(value, str) else value
    return body

def lambda_handler(event, context):
    logger.info('Event: %s', event)
    if not context is None:
        logger.info('Context: %s', context)
    body = get_body_from_event(event)
    if body != event:
        logger.info('Content: %s', body)

    conversation_unread_update = ConversationUnreadUpdate.from_dict(body)
    logger.info(conversation_unread_update)

    location_id = conversation_unread_update.location_id

    conversation_repository = ConversationRepository(location_id)
    conversation = conversation_repository.search(conversation_unread_update.id)
    logger.info('Search Conversation by ID result: \n%s', conversation)

    s3_client = AwsS3Client()
    # s3_client.write_to_s3(conversation)
