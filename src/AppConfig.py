import os

class AppConfig:

    @property
    def aws_bucket_region():
        return os.environ.get('AWS_BUCKET_REGION', 'us-east-1')
    