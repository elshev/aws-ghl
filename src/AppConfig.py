import os

class AppConfig:

    def get_aws_bucket_region():
        return os.environ.get('AWS_BUCKET_REGION', 'us-east-1')
    