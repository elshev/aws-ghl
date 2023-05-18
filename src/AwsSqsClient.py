import os
import boto3

from AppConfig import AppConfig

class AwsSqsClient:
    
    def __init__(self) -> None:
        self._sqs_client = boto3.client('sqs')

    @staticmethod
    def get_queue_url(queue_name):
        queue_base_url = AppConfig.get_sqs_base_url()
        queue_prefix = AppConfig.get_sqs_queue_prefix()
        queue_url = f'{queue_base_url}/{queue_prefix}-{queue_name}'
        return queue_url
        
    @staticmethod
    def get_maigun_events_queue_url():
        return AwsSqsClient.get_queue_url('mailgun-events')

    def get_message(self, queue_url):
        self._sqs_client.get_message(
            QueueUrl=queue_url
        )
        
    def send_message(self, queue_url, message_body):
        self._sqs_client.send_message(
            QueueUrl=queue_url,
            MessageBody=message_body
        )
        

    def get_from_mailgun_events_queue(self):
        queue_url = AwsSqsClient.get_maigun_events_queue_url()
        result = self.get_message(queue_url)
        return result

    def send_to_mailgun_events_queue(self, message_body):
        queue_url = AwsSqsClient.get_maigun_events_queue_url()
        self.send_message(queue_url, message_body)
