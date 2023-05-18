from datetime import date, datetime
import json
import logging
import os
import boto3
from botocore.exceptions import ClientError
from AppConfig import AppConfig
from AwsStsClient import AwsStsClient
from MgMessage import MgMessage
from Util import Util


class AwsS3Client:

    logger = logging.getLogger()
    _aws_sts_client = AwsStsClient()
    _aws_account_id = ''
    
    # Optimization variable to avoid redundant calls to AWS to check if the bucket exists
    _bucket_exists = None

    
    @property
    def aws_account_id(self):
        if not AwsS3Client._aws_account_id:
            AwsS3Client._aws_account_id = self._aws_sts_client.get_aws_account_id()
        return AwsS3Client._aws_account_id

    
    def __init__(self) -> None:
        self._s3_client = boto3.client('s3')

    
    @staticmethod
    def time_to_str(date_time = None):
        if not isinstance(date_time, date):
            date_time = datetime.now()
        return date_time.strftime('%Y%m%d-%H%M%S')


    @staticmethod
    def remove_tmp_file(file_path):
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
            else:
                AwsS3Client.logger.error('Error: %s file not found', file_path)
        except OSError as e:
            AwsS3Client.logger.error('Error while removing file: %s - %s', e.filename, e.strerror)


    @staticmethod
    def data_to_tmp_file(data, relative_file_path):
        file_path = AppConfig.get_tmp_file_path(relative_file_path)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return file_path

    
    def check_bucket(self):
        """Checks if a bucket exists. If not creates it

        Returns:
            str: Bucket Name.
        """
        # try to get a bucket name from cache first
        bucket_name = AppConfig.get_aws_bucket_name()
        #         
        if not AwsS3Client._bucket_exists:
            bucket_name = AppConfig.get_aws_bucket_name()
            s3_resource = boto3.resource("s3")
            bucket_resource = s3_resource.Bucket(bucket_name)
            # Create a bucket in S3 if it doesn't exist
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
            
            AwsS3Client._bucket_exists = True
        return bucket_name
    
    
    @staticmethod
    def get_object_key_from_contact(contact_id: str):
        dt = datetime.now()
        return f'{contact_id}/{dt:%Y-%m}/{dt:%Y%m%d-%H%M%S-%f}.json'

    
    @staticmethod
    def get_object_key_from_mg_message(mg_message: MgMessage):
        dt = datetime.fromtimestamp(mg_message.timestamp)
        folder_name = mg_message.sender if mg_message.is_reply_from_user else mg_message.recipient
        return f'{folder_name}/{dt:%Y-%m}/{dt:%Y%m%d-%H%M%S-%f}.eml'
    
    
    def upload_conversation_to_s3(self, contact_id, data):
        bucket_name = self.check_bucket()
        key_name = AwsS3Client.get_object_key_from_contact(contact_id)
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

    
    def save_message_as_mime(message: MgMessage):
        message_key = message.key.strip('=').lower()
        output_file_name = f'{datetime.now().strftime("%Y%m%d-%H%M%S-%f")}-{message_key}.eml'
        output_file_path = AppConfig.get_temp_file_path(output_file_name)
        logging.info(f'Dumpping MIME to the file: "{output_file_path}"')
        Util.write_file(output_file_path, message.body_mime, newline='\n')

        return output_file_path
        

    def upload_message_to_s3(self, mg_message: MgMessage):
        bucket_name = self.check_bucket()
        key_name = AwsS3Client.get_object_key_from_mg_message(mg_message=mg_message)
        s3_path = f'{bucket_name}/{key_name}'
        tmp_file_path = AwsS3Client.save_message_as_mime(message=mg_message)

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
