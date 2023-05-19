import logging
from AwsS3Client import AwsS3Client
from AwsSqsClient import AwsSqsClient
from MgClient import MgClient
from Util import Util

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    Util.log_lambda_event(event, context)

    # Get events from queue
    logging.info('Getting a message from the Queue...')
    sqs_client = AwsSqsClient()
    sqs_response = sqs_client.get_from_mailgun_events_queue()
    message = sqs_response['Messages'][0]
    receipt_handle = message['ReceiptHandle']
    raw_events = message['data']

    # Convert raw events dict to a list of MgEvent
    logging.info('Processing events...')
    mg_client = MgClient()
    mg_events = mg_client.raw_events_to_mg_events(raw_events)
    
    # Store MgMessage as MIME to S3
    logging.info('Storing to S3 Bucket...')
    s3_client = AwsS3Client()
    for mg_event in mg_events:
        mg_message = MgClient.get_mime_message(mg_event=mg_event)
        s3_client.upload_message_to_s3(mg_message)
    
    # Remove message from SQS
    logging.info('Removing a message from the queue (ReceiptHandle = "%s")...', receipt_handle)
    sqs_client.delete_from_mailgun_events_queue(receipt_handle)

    logging.info('Successfully completed!')
