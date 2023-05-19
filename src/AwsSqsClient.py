import os
import boto3

from AppConfig import AppConfig

class AwsSqsClient:
    
    def __init__(self) -> None:
        self._sqs_client = boto3.client('sqs')

    def get_queue_url(self, queue_name):
        queue_prefix = AppConfig.get_sqs_queue_prefix()
        queue_full_name = f'{queue_prefix}-{queue_name}'
        queue_url = self._sqs_client.get_queue_url(QueueName=queue_full_name)
        return queue_url
        
    def get_message(self, queue_name):
        queue_url = self.get_queue_url(queue_name)
        self._sqs_client.get_message(
            QueueUrl=queue_url
        )
        
    def send_message(self, queue_name, message_body):
        queue_url = self.get_queue_url(queue_name)
        self._sqs_client.send_message(
            QueueUrl=queue_url,
            MessageBody=message_body
        )

    def delete_message(self, queue_name):
        queue_url = self.get_queue_url(queue_name)
        self._sqs_client.delete_message(
            QueueUrl=queue_url
        )
        
        

    # 'mailgun-events' queue methods
    def get_maigun_events_queue_url(self):
        return self.get_queue_url('mailgun-events')

    def get_from_mailgun_events_queue(self):
        queue_url = self.get_maigun_events_queue_url()
        result = self.get_message(queue_url)
        return result

    def send_to_mailgun_events_queue(self, message_body):
        queue_url = self.get_maigun_events_queue_url()
        self.send_message(queue_url, message_body)

    def delete_from_mailgun_events_queue(self):
        queue_url = self.get_maigun_events_queue_url()
        result = self.delete_message(queue_url)
        return result
