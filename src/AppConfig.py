import os

from AwsSsmClient import AwsSsmClient

class AppConfig:

    GHL_ACCESS_TOKEN_SSM_PARAMETER_NAME = '/GHL/Dev/CurlWisdom/AccessToken'
    MAILGUN_API_KEY_SSM_PARAMETER_NAME = '/GHL/Dev/CurlWisdom/MailGunApiKey'

    def is_local_execution():
        return os.environ.get['AWS_LAMBDA_FUNCTION_NAME'] is None
    
    def is_aws_execution():
        return not AppConfig.is_local_execution()
    
    def get_ghl_access_token(self):
        return AwsSsmClient.get_parameter('GHL_ACCESS_TOKEN', AppConfig.GHL_ACCESS_TOKEN_SSM_PARAMETER_NAME)
    
    def get_aws_bucket_name():
        return os.environ['GHL_BUCKET_NAME']

    def get_aws_bucket_region():
        return os.environ.get('AWS_BUCKET_REGION', 'us-east-1')

    def get_mailgun_api_url():
        return os.environ.get('MAILGUN_API_URL', 'https://api.mailgun.net/v3')
    
    def get_mailgun_domain():
        return os.environ['MAILGUN_DOMAIN']

    def get_mailgun_api_key():
        aws_ssm_client = AwsSsmClient()
        return aws_ssm_client.get_parameter(env_name='MAILGUN_API_KEY', env_ssm_parameter_name=AppConfig.MAILGUN_API_KEY_SSM_PARAMETER_NAME)

    def get_temp_folder_path():
        return os.environ.get('TEMP_FOLDER', '/tmp/ghl')


    @staticmethod
    def get_temp_file_path(relative_file_path):
        tmp_folder_path = AppConfig.get_temp_folder_path()
        if not relative_file_path.startswith(f'{tmp_folder_path}/'):
            return f'{tmp_folder_path}/{relative_file_path}'
        return relative_file_path
