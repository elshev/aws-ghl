import os

class AppConfig:

    def get_aws_bucket_region():
        return os.environ.get('AWS_BUCKET_REGION', 'us-east-1')

    def get_mailgun_api_url():
        return os.environ.get('MAILGUN_API_URL', 'https://api.mailgun.net/v3')
    
    def get_mailgun_domain():
        return os.environ['MAILGUN_DOMAIN']

    def get_mailgun_api_key():
        return os.environ['MAILGUN_API_KEY']

    def get_temp_folder_path():
        return os.environ.get('TEMP_FOLDER', '/tmp/ghl')

    @staticmethod
    def get_temp_file_path(relative_file_path):
        tmp_folder_path = AppConfig.get_temp_folder_path()
        if not relative_file_path.startswith(f'{tmp_folder_path}/'):
            return f'{tmp_folder_path}/{relative_file_path}'
        return relative_file_path
