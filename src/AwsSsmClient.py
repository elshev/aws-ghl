from datetime import datetime
import os
import boto3

from AppConfig import AppConfig

class AwsSsmClient:

    _param_cache = {}

    @property
    def base_path(self):
        return self._base_path
    
    def __init__(self) -> None:
        self._base_path = AppConfig.get_ssm_base_path()
        self._ssm_client = boto3.client('ssm')

    def get_param_path(self, name):
        return f'{self._base_path}/{name}'

    def get_ssm_parameter(self, name):
        param_path = self.get_param_path(name)
        result = AwsSsmClient._param_cache.get(param_path)
        if result is None or result == '':
            parameter = self._ssm_client.get_parameter(Name=param_path, WithDecryption=True)
            result = parameter['Parameter']['Value']
            AwsSsmClient._param_cache[param_path] = result
        return result

    def _update_ssm_parameter(self, name, value, value_type):
        param_path = self.get_param_path(name)
        if value_type is None or value_type == '':
            value_type = 'SecureString'
        self._ssm_client.put_parameter(
            Name=param_path,
            Value=value,
            Type=value_type,
            Overwrite=True
        )
        AwsSsmClient._param_cache[param_path] = value

    def update_ssm_string_parameter(self, name, value):
        self._update_ssm_parameter(name, value, 'String')

    def update_ssm_secure_string_parameter(self, name, value):
        self._update_ssm_parameter(name, value, 'SecureString')

    def get_parameter(self, env_name, ssm_parameter_name):
        '''
        If 'env_name' exists in environment variables, returns its value
        Otherwise, goes to SSM Parameter Store and returns value for parameter with name = env_ssm_parameter_name
        '''
        result = ''
        if env_name in os.environ:
            result = os.environ[env_name]
        if result is None or result == '':
            result = self.get_ssm_parameter(ssm_parameter_name)
        return result


    REFRESH_TOKEN_PARAM_NAME = 'RefreshToken'
    ACCESS_TOKEN_PARAM_NAME = 'AccessToken'
    ACCESS_TOKEN_EXPIRE_PARAM_NAME = 'AccessTokenExpire'
    MAILGUN_PROCESSED_ISOTIME_PARAM_NAME = 'MailGunProcessedIsoTime'

    def get_ghl_refresh_token(self):
        return self.get_parameter('GHL_REFRESH_TOKEN', AwsSsmClient.REFRESH_TOKEN_PARAM_NAME)

    def set_ghl_refresh_token(self, value):
        return self.update_ssm_secure_string_parameter(AwsSsmClient.REFRESH_TOKEN_PARAM_NAME, value)

    def get_ghl_access_token(self):
        return self.get_parameter('GHL_ACCESS_TOKEN', AwsSsmClient.ACCESS_TOKEN_PARAM_NAME)

    def set_ghl_access_token(self, value):
        return self.update_ssm_secure_string_parameter(AwsSsmClient.ACCESS_TOKEN_PARAM_NAME, value)

    def get_ghl_access_token_expire(self):
        return self.get_parameter('GHL_ACCESS_TOKEN_EXXPIRE', AwsSsmClient.ACCESS_TOKEN_EXPIRE_PARAM_NAME)

    def set_ghl_access_token_expire(self, value):
        return self.update_ssm_secure_string_parameter(AwsSsmClient.ACCESS_TOKEN_EXPIRE_PARAM_NAME, value)

    def get_mailgun_api_key(self):
        return self.get_parameter('MAILGUN_API_KEY', 'MailGunApiKey')
    
    def get_mailgun_processed_datetime(self):
        isotime = self.get_parameter('MAILGUN_PROCESSED_ISOTIME', AwsSsmClient.MAILGUN_PROCESSED_ISOTIME_PARAM_NAME)
        if isotime:
            return datetime.fromisoformat(isotime)
        # if there is no starting date to process MailGun events, return yesterday
        return datetime.utcnow().date() + datetime.timedelta(days=-1)

    def set_mailgun_processed_datetime(self, value: datetime):
        if not AppConfig.is_local_execution():
            self.update_ssm_string_parameter(AwsSsmClient.MAILGUN_PROCESSED_ISOTIME_PARAM_NAME, value.isoformat())
