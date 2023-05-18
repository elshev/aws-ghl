import os
import boto3

from AppConfig import AppConfig

class AwsSqsClient:
    
    MAILGUN_EVENTS_QUEUE_NAME = 'mailgun-events'

    def __init__(self) -> None:
        self._sqs_client = boto3.client('sqs')


    def send_message(self, queue_url, message_body):
        self._sqs_client.send_message(
            QueueUrl=queue_url,
            MessageBody=message_body
        )
        
    def send_message_to_mailgun_events_queue(self, message_body):
        queue_prefix = AppConfig.get_sqs_queue_prefix()
        queue_url = f'{queue_prefix}-{AwsSqsClient.MAILGUN_EVENTS_QUEUE_NAME}'
        self.send_message(queue_url, message_body)
