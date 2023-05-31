import json
import logging
from typing import Iterable
from AwsS3Client import AwsS3Client
from AwsSqsClient import AwsSqsClient
from MgClient import MgClient
from MgEvent import MgEvent
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
        # In case of direct request to SQS it uses 'Body', 'ReceiptHandle', etc.
        # In case of calling Lambda via SQS trigger, 'body', 'receiptHandle', etc. is used
        receipt_handle = Util.get_dict_value_with_either_key(record, ['ReceiptHandle', 'receiptHandle'], raise_if_not_found=True)
        raw_events = Util.get_dict_value_with_either_key(record, ['Body', 'body'], raise_if_not_found=True)
            
        # Convert raw events dict to a list of MgEvent
        logging.info('Processing events...')
        mg_client = MgClient()
        mg_events = mg_client.raw_events_to_mg_events(raw_events)
        
        # Store MgMessage as MIME to S3
        logging.info('Storing to S3 Bucket...')
        s3_client = AwsS3Client()
        for mg_event in mg_events:
            object_key = AwsS3Client.get_object_key_from_mg_event(mg_event)
            if s3_client.is_object_exits(object_key):
                bucket_name = s3_client.check_bucket()
                logging.info('MailGun message object "%s" already exists in S3 bucket "%s". Skip saving it.', object_key, bucket_name)
                continue
            mg_message = mg_client.get_mime_message(mg_event)
            s3_client.upload_mgmessage_to_s3(mg_message)
        
        # Remove message from SQS
        if receipt_handle:
            logging.info('Removing a message from the queue (ReceiptHandle = "%s")...', receipt_handle)
            sqs_client.delete_from_mailgun_events_queue(receipt_handle)
        else:
            logging.info('ReceiptHandle is empty. Nothing to remove.', receipt_handle)

    logging.info('Successfully completed!')
