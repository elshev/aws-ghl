import os
import boto3

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

    _param_cache = {}

    @staticmethod
    def get_parameter(env_name, env_ssm_parameter_name):
        '''
        If 'env_name' exists in environment variables, returns its value
        Otherwise, goes to SSM Parameter Store and returns value for parameter with name = env_ssm_parameter_name
        '''
        result = ''
        if env_name in os.environ:
            result = os.environ[env_name]
        if result is None or result == '':
            result = AwsSsmClient._param_cache.get(env_ssm_parameter_name)
            if result is None or result == '':
                aws_ssm_client = AwsSsmClient()
                result = aws_ssm_client.get_ssm_parameter(env_ssm_parameter_name)
                AwsSsmClient._param_cache[env_ssm_parameter_name] = result
        return result
    