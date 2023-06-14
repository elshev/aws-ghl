import os

class AppConfig:
    # Environment variable names
    ENV_AWS_LAMBDA_FUNCTION_NAME = 'AWS_LAMBDA_FUNCTION_NAME'
    ENV_TEMP_FOLDER = 'TEMP_FOLDER'
    ENV_AWS_REGION = 'AWS_REGION'
    ENV_SQS_MAILGUN_EVENTS_QUEUE_NAME = 'SQS_MAILGUN_EVENTS_QUEUE_NAME'
    ENV_MAILGUN_API_URL = 'MAILGUN_API_URL'
    
    # Default values
    DEFAULT_TEMP_FOLDER = '/tmp/ghl'
    DEFAULT_AWS_REGION = 'us-east-1'
    DEFAULT_SQS_MAILGUN_EVENTS_QUEUE_NAME = 'mailgun-events'
    DEFAULT_MAILGUN_API_URL = 'https://api.mailgun.net/v3'

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
        return os.environ.get(AppConfig.ENV_SQS_MAILGUN_EVENTS_QUEUE_NAME, AppConfig.DEFAULT_SQS_MAILGUN_EVENTS_QUEUE_NAME)

    @staticmethod
    def get_ghl_base_url():
        return 'https://services.leadconnectorhq.com'

    @staticmethod
    def get_aws_bucket_name():
        return os.environ['GHL_BUCKET_NAME']

    @staticmethod
    def get_aws_region():
        return os.environ.get(AppConfig.ENV_AWS_REGION, AppConfig.DEFAULT_AWS_REGION)

    @staticmethod
    def get_mailgun_api_url():
        return os.environ.get(AppConfig.ENV_MAILGUN_API_URL, AppConfig.DEFAULT_MAILGUN_API_URL)

    @staticmethod
    def get_mailgun_domain():
        return os.environ['MAILGUN_DOMAIN']


    @staticmethod
    def get_temp_folder_path():
        return os.environ.get(AppConfig.ENV_TEMP_FOLDER, AppConfig.DEFAULT_TEMP_FOLDER)


    @staticmethod
    def get_temp_file_path(relative_file_path):
        if not relative_file_path:
            raise ValueError('"relative_file_path" is empty')
        tmp_folder_path = AppConfig.get_temp_folder_path()
        if not relative_file_path.startswith(f'{tmp_folder_path}/'):
            return f'{tmp_folder_path}/{relative_file_path}'
        return relative_file_path
