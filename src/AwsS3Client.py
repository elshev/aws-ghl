import datetime
import json
import logging
import os
import boto3
from botocore.exceptions import ClientError
from AppConfig import AppConfig
from AwsStsClient import AwsStsClient


class AwsS3Client:

    logger = logging.getLogger()
    _aws_sts_client = AwsStsClient()
    _aws_account_id = ''
    
    # "location_id: bucket_name" pairs
    _bucket_cache = {}    

    @property
    def aws_account_id(self):
        if not AwsS3Client._aws_account_id:
            AwsS3Client._aws_account_id = self._aws_sts_client.get_aws_account_id()
        return AwsS3Client._aws_account_id

    def __init__(self) -> None:
        self._s3_client = boto3.client('s3')

    @staticmethod
    def time_to_str(date_time = None):
        if not isinstance(date_time, datetime.date):
            date_time = datetime.datetime.now()
        return date_time.strftime('%Y%m%d-%H%M%S')


    @staticmethod
    def remove_tmp_file(file_name):
        lambda_path = AppConfig.get_tmp_file_path(file_name)
        try:
            if os.path.isfile(lambda_path):
                os.remove(lambda_path)
            else:
                AwsS3Client.logger.error('Error: %s file not found', lambda_path)
        except OSError as e:
            AwsS3Client.logger.error('Error while removing file: %s - %s', e.filename, e.strerror)


    @staticmethod
    def data_to_tmp_file(data, relative_file_path):
        file_path = AppConfig.get_tmp_file_path(relative_file_path)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return file_path

    def get_bucket_name_by_location(self, location_id: str):
        return f'ghl-{self.aws_account_id}-{location_id.lower()}'

    def check_bucket(self, location_id: str):
        """Checks if a bucket for location_id exists. If not creates it

        Args:
            location_id (str): GoHighLevel Location ID

        Returns:
            str: Bucket Name.
        """
        # try to get a bucket name from cache first
        bucket_name = None
        if location_id in AwsS3Client._bucket_cache:
            bucket_name = AwsS3Client._bucket_cache[location_id]
        #         
        if not bucket_name:
            bucket_name = self.get_bucket_name_by_location(location_id)
            s3_resource = boto3.resource("s3")
            bucket_resource = s3_resource.Bucket(bucket_name)
            # Create bucket in S3 if doesn't exist
            if bucket_resource.creation_date is None:
                AwsS3Client.logger.info("Bucket '%s' doesn't exist. Creating...", bucket_name)
                create_bucket_configuration = {}
                aws_bucket_region = AppConfig.get_aws_bucket_region()
                if aws_bucket_region != 'us-east-1':
                    create_bucket_configuration['LocationConstraint'] = aws_bucket_region
                if create_bucket_configuration:
                    self._s3_client.create_bucket(
                        Bucket=bucket_name,
                        CreateBucketConfiguration=create_bucket_configuration
                    )
                else:
                    self._s3_client.create_bucket(Bucket=bucket_name)
                AwsS3Client.logger.info("Bucket '%s' was created.", bucket_name)
            
            AwsS3Client._bucket_cache[location_id] = bucket_name
            return bucket_name
    
    @staticmethod
    def get_object_key(contact_id: str):
        dt = datetime.datetime.now()
        return f'{contact_id}/{dt:%Y-%m}/{dt:%Y%m%d-%H%M%S-%f}.json'

    def write_to_s3(self, location_id, contact_id, data):
        bucket_name = self.check_bucket(location_id)
        key_name = AwsS3Client.get_object_key(contact_id)
        s3_path = f'{bucket_name}/{key_name}'
        tmp_file_path = AwsS3Client.data_to_tmp_file(data, key_name)

        AwsS3Client.logger.info('Starting S3.putObject to %s ...', s3_path)
        try:
            response = self._s3_client.upload_file(tmp_file_path, bucket_name, key_name)
        except ClientError as e:
            AwsS3Client.logger.error(e)
            return False
        finally:
            AwsS3Client.remove_tmp_file(tmp_file_path)
        AwsS3Client.logger.info('Successfully saved object to %s', s3_path)
        AwsS3Client.logger.info('Response: %s', response)
        return True
