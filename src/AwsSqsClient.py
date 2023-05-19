import json
import os
import boto3

from AppConfig import AppConfig

class AwsSqsClient:

    _queue_url_cache = {}    

    def __init__(self) -> None:
        self._sqs_client = boto3.client('sqs')
        self._mailgun_events_queue_name = AppConfig.get_mailgun_events_queue_name()

    def get_queue_url(self, queue_name):
        queue_url = AwsSqsClient._queue_url_cache.get(queue_name)
        if not queue_url:
            queue_prefix = AppConfig.get_sqs_queue_prefix()
            queue_full_name = f'{queue_prefix}-{queue_name}'
            response = self._sqs_client.get_queue_url(QueueName=queue_full_name)
            queue_url = response['QueueUrl']
            AwsSqsClient._queue_url_cache[queue_name] = queue_url
        return queue_url
        
    def get_message(self, queue_name):
        queue_url = self.get_queue_url(queue_name)
        response = self._sqs_client.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=1
        )
        return response
        
    def send_message(self, queue_name, message_body):
        queue_url = self.get_queue_url(queue_name)
        message_str = message_body
        if isinstance(message_body, dict) or isinstance(message_body, list):
            message_str = json.dumps(message_body)
        self._sqs_client.send_message(
            QueueUrl=queue_url,
            MessageBody=message_str
        )

    def delete_message(self, queue_name, receipt_handle):
        queue_url = self.get_queue_url(queue_name)
        self._sqs_client.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle
        )


    # 'mailgun-events' queue methods
    def send_to_mailgun_events_queue(self, message_body):
        self.send_message(self._mailgun_events_queue_name, message_body)

    def get_from_mailgun_events_queue(self):
        response = self.get_message(self._mailgun_events_queue_name)
        return response

    def delete_from_mailgun_events_queue(self, receipt_handle):
        self.delete_message(self._mailgun_events_queue_name, receipt_handle)
