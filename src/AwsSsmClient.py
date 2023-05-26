from datetime import (
    datetime,
    timedelta
)
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

    def _get_param_path(self, name):
        return f'{self._base_path}/{name}'

    def _get_ssm_parameter(self, name, use_cache=False):
        param_path = self._get_param_path(name)
        result = None
        if (use_cache):
            result = AwsSsmClient._param_cache.get(param_path)
        if result is None or result == '':
            parameters = self._ssm_client.get_parameters(Names=[param_path], WithDecryption=True)
            invalid_parameters = parameters.get('InvalidParameters')
            if invalid_parameters and param_path in invalid_parameters:
                return None
            result = parameters['Parameters'][0]['Value']
            AwsSsmClient._param_cache[param_path] = result
        return result

    def _update_ssm_parameter(self, name, value, value_type):
        param_path = self._get_param_path(name)
        if value_type is None or value_type == '':
            value_type = 'SecureString'
        self._ssm_client.put_parameter(
            Name=param_path,
            Value=value,
            Type=value_type,
            Overwrite=True
        )
        AwsSsmClient._param_cache[param_path] = value

    def _update_ssm_string_parameter(self, name, value):
        self._update_ssm_parameter(name, value, 'String')

    def _update_ssm_secure_string_parameter(self, name, value):
        self._update_ssm_parameter(name, value, 'SecureString')

    def _get_parameter(self, env_name, ssm_parameter_name, use_cache=True):
        '''
        If 'env_name' exists in environment variables, returns its value
        Otherwise, goes to SSM Parameter Store and returns value for parameter with name = env_ssm_parameter_name
        '''
        result = ''
        if env_name in os.environ:
            result = os.environ[env_name]
        if result is None or result == '':
            result = self._get_ssm_parameter(ssm_parameter_name, use_cache=use_cache)
        return result


    REFRESH_TOKEN_PARAM_NAME = 'RefreshToken'
    ACCESS_TOKEN_PARAM_NAME = 'AccessToken'
    ACCESS_TOKEN_EXPIRE_PARAM_NAME = 'AccessTokenExpire'
    MAILGUN_PROCESSED_ISOTIME_PARAM_NAME = 'MailGunProcessedIsoTime'

    def get_ghl_client_id(self):
        return self._get_parameter('GHL_CLIENT_ID', 'ClientId')

    def get_ghl_client_secret(self):
        return self._get_parameter('GHL_CLIENT_SECRET', 'ClientSecret')

    def get_ghl_refresh_token(self):
        return self._get_parameter('GHL_REFRESH_TOKEN', AwsSsmClient.REFRESH_TOKEN_PARAM_NAME, use_cache=False)

    def set_ghl_refresh_token(self, value):
        return self._update_ssm_secure_string_parameter(AwsSsmClient.REFRESH_TOKEN_PARAM_NAME, value)

    def get_ghl_access_token(self):
        return self._get_parameter('GHL_ACCESS_TOKEN', AwsSsmClient.ACCESS_TOKEN_PARAM_NAME)

    def set_ghl_access_token(self, value):
        return self._update_ssm_secure_string_parameter(AwsSsmClient.ACCESS_TOKEN_PARAM_NAME, value)

    def get_ghl_access_token_expire(self):
        return self._get_parameter('GHL_ACCESS_TOKEN_EXXPIRE', AwsSsmClient.ACCESS_TOKEN_EXPIRE_PARAM_NAME)

    def set_ghl_access_token_expire(self, value):
        return self._update_ssm_secure_string_parameter(AwsSsmClient.ACCESS_TOKEN_EXPIRE_PARAM_NAME, value)

    def get_mailgun_api_key(self):
        return self._get_parameter('MAILGUN_API_KEY', 'MailGunApiKey')
    
    def get_mailgun_processed_datetime(self):
        isotime = self._get_parameter('MAILGUN_PROCESSED_ISOTIME', AwsSsmClient.MAILGUN_PROCESSED_ISOTIME_PARAM_NAME, use_cache=False)
        if isotime:
            return datetime.fromisoformat(isotime)
        # if there is no starting date to process MailGun events, return yesterday
        return datetime.utcnow().date() + timedelta(days=-1)

    def set_mailgun_processed_datetime(self, value: datetime):
        if value > datetime.utcnow():
            raise ValueError('MailGun Processed datetime cant be greater than current time')
        self._update_ssm_string_parameter(AwsSsmClient.MAILGUN_PROCESSED_ISOTIME_PARAM_NAME, value.isoformat())
