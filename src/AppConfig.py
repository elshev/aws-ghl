import os

class AppConfig:
    # Environment variable names
    ENV_AWS_LAMBDA_FUNCTION_NAME = 'AWS_LAMBDA_FUNCTION_NAME'
    ENV_TEMP_FOLDER = 'TEMP_FOLDER'
    
    # Default values
    TEMP_FOLDER_DEFAULT = '/tmp/ghl'


    @staticmethod
    def is_local_execution():
        return os.environ.get(AppConfig.ENV_AWS_LAMBDA_FUNCTION_NAME) is None
    
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
    def get_temp_folder_path():
        return os.environ.get(AppConfig.ENV_TEMP_FOLDER, AppConfig.TEMP_FOLDER_DEFAULT)


    @staticmethod
    def get_temp_file_path(relative_file_path):
        tmp_folder_path = AppConfig.get_temp_folder_path()
        if not relative_file_path.startswith(f'{tmp_folder_path}/'):
            return f'{tmp_folder_path}/{relative_file_path}'
        return relative_file_path
