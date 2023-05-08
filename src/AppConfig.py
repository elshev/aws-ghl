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
