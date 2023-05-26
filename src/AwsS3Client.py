from datetime import date, datetime
import json
import logging
import os
import boto3
from botocore.exceptions import ClientError
from AppConfig import AppConfig
from AwsStsClient import AwsStsClient
from GhlOutboundMessage import GhlOutboundMessage
from MgMessage import MgMessage
from Util import Util


class AwsS3Client:

    logger = logging.getLogger()
    _aws_sts_client = AwsStsClient()
    _aws_account_id = ''
    
    # Optimization variable to avoid redundant calls to AWS to check if the bucket exists
    _bucket_name_cache = None

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

    
    def is_bucket_exists(self, bucket_name):
        s3_resource = boto3.resource("s3")
        bucket_resource = s3_resource.Bucket(bucket_name)
        if bucket_resource.creation_date:
            return True
        try:
            s3_resource.meta.client.head_bucket(Bucket=bucket_name)
        except ClientError:
            return False
        
        return True
        
    
    def check_bucket(self):
        """Checks if a bucket exists. If not creates it

        Returns:
            str: Bucket Name.
        """
        # try to get a bucket name from cache first
        bucket_name = AwsS3Client._bucket_name_cache
        #         
        if not bucket_name:
            # Create a bucket in S3 if it doesn't exist
            bucket_name = AppConfig.get_aws_bucket_name()
            if not self.is_bucket_exists(bucket_name):
                create_bucket_configuration = {}
                aws_region = AppConfig.get_aws_region()
                AwsS3Client.logger.info("Bucket '%s' doesn't exist. Creating a bucket in '%s' regon...", bucket_name, aws_region)
                if aws_region != 'us-east-1':
                    create_bucket_configuration['LocationConstraint'] = aws_region
                if create_bucket_configuration:
                    self._s3_client.create_bucket(
                        Bucket=bucket_name,
                        CreateBucketConfiguration=create_bucket_configuration
                    )
                else:
                    self._s3_client.create_bucket(Bucket=bucket_name)
                AwsS3Client.logger.info("Bucket '%s' was created.", bucket_name)
            
            AwsS3Client._bucket_name_cache = bucket_name

        return bucket_name

    
    def is_object_exits(self, object_key):
        bucket_name = self.check_bucket()
        response = self._s3_client.list_objects_v2(
            Bucket=bucket_name,
            Prefix=object_key,
            MaxKeys=1
        )
        if not 'Contents' in response:
            return False
        if not len(response['Contents']) > 0:
            return False
        if not 'Key' in response['Contents'][0]:
            return False
        return response['Contents'][0]['Key'] == object_key

    
    @staticmethod
    def get_object_key_from_contact(contact_id: str):
        dt = datetime.now()
        return f'{contact_id}/{dt:%Y-%m}/{dt:%Y%m%d-%H%M%S-%f}.json'

    
    @staticmethod
    def get_object_key_from_mg_message(mg_message: MgMessage):
        dt = datetime.fromtimestamp(mg_message.timestamp)
        folder_name = mg_message.sender if mg_message.is_reply_from_user else mg_message.recipient
        return f'{folder_name}/{dt:%Y-%m}/{dt:%Y%m%d-%H%M%S-%f}.eml'
    
    
    def upload_file_to_s3(self, object_key, tmp_file_path, remove_file_after_upload=True):
        try:
            bucket_name = self.check_bucket()
            if self.is_object_exits(object_key):
                AwsS3Client.logger.info('Object "%s" already exists in S3 bucket "%s". Skip saving it.', object_key, bucket_name)
                return True
            s3_path = f'{bucket_name}/{object_key}'
            AwsS3Client.logger.info('Starting S3.putObject to %s ...', s3_path)
            response = self._s3_client.upload_file(tmp_file_path, bucket_name, object_key)
        except ClientError as e:
            AwsS3Client.logger.error(e)
            return False
        finally:
            if remove_file_after_upload:
                AwsS3Client.remove_tmp_file(tmp_file_path)
        AwsS3Client.logger.info('Successfully saved object to %s', s3_path)
        AwsS3Client.logger.info('Response: %s', response)
        return False

    
    def upload_conversation_to_s3(self, contact_id, data):
        object_key = AwsS3Client.get_object_key_from_contact(contact_id)
        tmp_file_path = AwsS3Client.data_to_tmp_file(data, object_key)
        return self.upload_file_to_s3(object_key, tmp_file_path)

    
    def save_message_as_mime(message: MgMessage):
        message_key = message.key.strip('=').lower()
        output_file_name = f'{datetime.now().strftime("%Y%m%d-%H%M%S-%f")}-{message_key}.eml'
        output_file_path = AppConfig.get_temp_file_path(output_file_name)
        logging.info(f'Dumpping MIME to the file: "{output_file_path}"')
        Util.write_file(output_file_path, message.body_mime, newline='\n')

        return output_file_path
        

    def upload_mgmessage_to_s3(self, mg_message: MgMessage):
        object_key = AwsS3Client.get_object_key_from_mg_message(mg_message)
        tmp_file_path = AwsS3Client.save_message_as_mime(mg_message)
        return self.upload_file_to_s3(object_key, tmp_file_path)

    
    @staticmethod
    def get_object_key_from_outbound_message(ghl_message: GhlOutboundMessage):
        dt = ghl_message.date_added
        folder_name = ghl_message.email.lower()
        return f'{folder_name}/{dt:%Y-%m}/{dt:%Y%m%d-%H%M%S-%f}-sms.json'


    def save_ghlmessage_as_sms(ghl_message: GhlOutboundMessage):
        output_file_name = f'{datetime.now().strftime("%Y%m%d-%H%M%S-%f")}-{ghl_message.conversation_id}.json'
        output_file_path = AppConfig.get_temp_file_path(output_file_name)
        logging.info(f'Dumpping SMS to the file: "{output_file_path}"')
        content = json.dumps(ghl_message.to_dict(), indent=2)
        Util.write_file(output_file_path, content, newline='\n')

        return output_file_path
        

    def upload_outbound_sms(self, ghl_message: GhlOutboundMessage):
        object_key = AwsS3Client.get_object_key_from_outbound_message(ghl_message)
        tmp_file_path = AwsS3Client.save_ghlmessage_as_sms(ghl_message)
        return self.upload_file_to_s3(object_key, tmp_file_path)
