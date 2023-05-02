import datetime
import json
import logging
import os
import boto3
from botocore.exceptions import ClientError


class AwsS3Client:

    bucket_name = 'test-489440259680'
    logger = logging.getLogger()

    def __init__(self) -> None:
        self._s3_client = boto3.client('s3')

    @staticmethod
    def time_to_str(date_time = None):
        if not isinstance(date_time, datetime.date):
            date_time = datetime.datetime.now()
        return date_time.strftime('%Y%m%d-%H%M%S')


    @staticmethod
    def get_tmp_file_path(file_name):
        tmp_folder_path = '/tmp'
        if not file_name.startswith(f'{tmp_folder_path}/'):
            return f'/tmp/{file_name}'
        return file_name


    @staticmethod
    def remove_tmp_file(file_name):
        lambda_path = AwsS3Client.get_tmp_file_path(file_name)
        try:
            if os.path.isfile(lambda_path):
                os.remove(lambda_path)
            else:
                AwsS3Client.logger.error('Error: %s file not found', lambda_path)
        except OSError as e:
            AwsS3Client.logger.error('Error while removing file: %s - %s', e.filename, e.strerror)


    @staticmethod
    def data_to_tmp_file(data, file_name):
        lambda_path = AwsS3Client.get_tmp_file_path(file_name)
        with open(lambda_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return lambda_path


    @staticmethod
    def get_s3_key_name():
        return f'{AwsS3Client.time_to_str()}.txt'


    def write_to_s3(self, data):
        key_name = AwsS3Client.get_s3_key_name()
        s3_path = f'{AwsS3Client.bucket_name}/{key_name}'
        tmp_file_path = AwsS3Client.data_to_tmp_file(data, key_name)

        AwsS3Client.logger.info('Starting S3.putObject to %s ...', s3_path)
        try:
            response = self._s3_client.upload_file(tmp_file_path, AwsS3Client.bucket_name, key_name)
        except ClientError as e:
            AwsS3Client.logger.error(e)
            return False
        finally:
            AwsS3Client.remove_tmp_file(tmp_file_path)
        AwsS3Client.logger.info('Successfully saved object to %s', s3_path)
        AwsS3Client.logger.info('Response: %s', response)
        return True
