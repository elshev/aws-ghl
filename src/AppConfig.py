import os
from datetime import (
    datetime,
    timedelta
)

from AwsSsmClient import AwsSsmClient

class AppConfig:

    @staticmethod
    def is_local_execution():
        return os.environ.get('AWS_LAMBDA_FUNCTION_NAME') is None
    
    @staticmethod
    def is_aws_execution():
        return not AppConfig.is_local_execution()
    
    @staticmethod
    def get_ssm_base_path():
        return os.environ['SSM_BASE_PATH']

    @staticmethod
    def get_sqs_queue_prefix():
        return os.environ['SQS_QUEUE_PREFIX']

    @staticmethod
    def get_mailgun_events_queue_name():
        return os.environ.get('SQS_MAILGUN_EVENTS_QUEUE_NAME', 'mailgun-events')

    @staticmethod
    def get_ghl_base_url():
        return 'https://services.leadconnectorhq.com'

    @staticmethod
    def get_ghl_access_token_ssm_path():
        return f'{AppConfig.get_ssm_base_path()}/AccessToken'

    @staticmethod
    def get_ghl_access_token():
        access_token_param_name = AppConfig.get_ghl_access_token_ssm_path()
        return AwsSsmClient.get_parameter('GHL_ACCESS_TOKEN', access_token_param_name)
   
    
    @staticmethod
    def get_aws_bucket_name():
        return os.environ['GHL_BUCKET_NAME']

    @staticmethod
    def get_aws_region():
        return os.environ.get('AWS_REGION', 'us-east-1')

    @staticmethod
    def get_mailgun_api_url():
        return os.environ.get('MAILGUN_API_URL', 'https://api.mailgun.net/v3')

    @staticmethod
    def get_mailgun_domain():
        return os.environ['MAILGUN_DOMAIN']

    @staticmethod
    def get_mailgun_api_key():
        mailgun_api_key_param_name = f'{AppConfig.get_ssm_base_path()}/MailGunApiKey'
        return AwsSsmClient.get_parameter('MAILGUN_API_KEY', mailgun_api_key_param_name)

    @staticmethod
    def get_mailgun_processed_datetime():
        mailgun_processed_timestamp_param_name = f'{AppConfig.get_ssm_base_path()}/MailGunProcessedTimestamp'
        result = None
        isotime = os.environ.get('MAILGUN_PROCESSED_ISOTIME')
        if (isotime):
            return datetime.fromisoformat(isotime)
        ts = AwsSsmClient.get_parameter('MAILGUN_PROCESSED_TIMESTAMP', mailgun_processed_timestamp_param_name)
        if ts:
            return datetime.fromtimestamp(ts)
        # if there is no starting date to process MailGun events, return one day before
        return datetime.utcnow().date() + timedelta(days=-1)


    @staticmethod
    def get_temp_folder_path():
        return os.environ.get('TEMP_FOLDER', '/tmp/ghl')


    @staticmethod
    def get_temp_file_path(relative_file_path):
        tmp_folder_path = AppConfig.get_temp_folder_path()
        if not relative_file_path.startswith(f'{tmp_folder_path}/'):
            return f'{tmp_folder_path}/{relative_file_path}'
        return relative_file_path
