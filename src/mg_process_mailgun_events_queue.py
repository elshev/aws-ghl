import json
import logging
from AwsS3Client import AwsS3Client
from AwsSqsClient import AwsSqsClient
from MgClient import MgClient
from Util import Util

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    """Processes messages from SQS 'mailgun-events' queue

    Args:
        event (dict): Should contain event from SQS like { "Records": [message1, message2]}
        Where 'messageX' is a dict representing SQS message
    """
    Util.log_lambda_event(event, context)

    event_dict = event
    if not isinstance(event_dict, dict):
        event_dict = json.loads(event)
    records = event_dict['Records']
    if not records:
        raise ValueError('"Records" entry is empty or not found in "event"')

    sqs_client = AwsSqsClient()
    
    for record in records:
        receipt_handle = record['ReceiptHandle']
        # In case of direct request to SQS it uses 'Body'
        # In case of calling Lambda via SQS trigger, 'body' is used
        raw_events = record.get('Body')
        if not raw_events:
            raw_events = record.get('body')
        if not raw_events:
            raise ValueError('Record does not contain "Body" entry')
            
        # Convert raw events dict to a list of MgEvent
        logging.info('Processing events...')
        mg_client = MgClient()
        mg_events = mg_client.raw_events_to_mg_events(raw_events)
        
        # Store MgMessage as MIME to S3
        logging.info('Storing to S3 Bucket...')
        s3_client = AwsS3Client()
        for mg_event in mg_events:
            mg_message = mg_client.get_mime_message(mg_event)
            s3_client.upload_mgmessage_to_s3(mg_message)
        
        # Remove message from SQS
        if receipt_handle:
            logging.info('Removing a message from the queue (ReceiptHandle = "%s")...', receipt_handle)
            sqs_client.delete_from_mailgun_events_queue(receipt_handle)
        else:
            logging.info('ReceiptHandle is empty. Nothing to remove.', receipt_handle)

    logging.info('Successfully completed!')
