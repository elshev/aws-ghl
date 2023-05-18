import os

from AwsSsmClient import AwsSsmClient

class AppConfig:

    @staticmethod
    def is_local_execution():
        return os.environ.get['AWS_LAMBDA_FUNCTION_NAME'] is None
    
    @staticmethod
    def is_aws_execution():
        return not AppConfig.is_local_execution()
    
    @staticmethod
    def get_ssm_parameter_path():
        return os.environ['SSM_PARAMETER_STORE_PATH']

    @staticmethod
    def get_sqs_base_url():
        return os.environ['SQS_BASE_URL']

    @staticmethod
    def get_sqs_queue_prefix():
        return os.environ['SQS_QUEUE_PREFIX']

    @staticmethod
    def get_ghl_base_url():
        return 'https://services.leadconnectorhq.com'

    @staticmethod
    def get_ghl_access_token():
        access_token_param_name = f'{AppConfig.get_ssm_parameter_path()}/AccessToken'
        return AwsSsmClient.get_parameter('GHL_ACCESS_TOKEN', access_token_param_name)
   
    
    @staticmethod
    def get_aws_bucket_name():
        return os.environ['GHL_BUCKET_NAME']

    @staticmethod
    def get_aws_bucket_region():
        return os.environ.get('AWS_BUCKET_REGION', 'us-east-1')

    @staticmethod
    def get_mailgun_api_url():
        return os.environ.get('MAILGUN_API_URL', 'https://api.mailgun.net/v3')

    @staticmethod
    def get_mailgun_domain():
        return os.environ['MAILGUN_DOMAIN']

    @staticmethod
    def get_mailgun_api_key():
        mailgun_api_key_param_name = f'{AppConfig.get_ssm_parameter_path()}/MailGunApiKey'
        return AwsSsmClient.get_parameter('MAILGUN_API_KEY', mailgun_api_key_param_name)

    @staticmethod
    def get_temp_folder_path():
        return os.environ.get('TEMP_FOLDER', '/tmp/ghl')


    @staticmethod
    def get_temp_file_path(relative_file_path):
        tmp_folder_path = AppConfig.get_temp_folder_path()
        if not relative_file_path.startswith(f'{tmp_folder_path}/'):
            return f'{tmp_folder_path}/{relative_file_path}'
        return relative_file_path
