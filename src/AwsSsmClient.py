import os
import boto3

GHL_ACCESS_TOKEN_SSM_PARAMETER_NAME = '/GHL/Dev/CurlWisdom/AccessToken'
GHL_REFRESH_TOKEN_SSM_PARAMETER_NAME = '/GHL/Dev/CurlWisdom/RefreshToken'

class AwsSsmClient:

    def __init__(self) -> None:
        self._ssm_client = boto3.client('ssm')


    def get_ssm_parameter(self, name):
        parameter = self._ssm_client.get_parameter(Name=name)
        return parameter['Parameter']['Value']


    def update_ssm_parameter(self, name, value):
        self._ssm_client.put_parameter(
            Name=name,
            Overwrite=True,
            Value=value,
        )


    def get_parameter(self, env_name, env_ssm_parameter_name):
        '''
        If 'env_name' exists in environment variables, returns its value
        Otherwise, goes to SSM Parameter Store and returns value for parameter with name = env_ssm_parameter_name
        '''
        result = ''
        if env_name in os.environ:
            result = os.environ[env_name]
        if result is None or result == '':
            result = self.get_ssm_parameter(env_ssm_parameter_name)
        return result
    
    def get_access_token(self):
        return self.get_parameter('GHL_ACCESS_TOKEN', GHL_ACCESS_TOKEN_SSM_PARAMETER_NAME)

