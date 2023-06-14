import os
import pytest
from AppConfig import AppConfig

TEMP_FOLDER = '/tmp/TestAppConfig'
AWS_LAMBDA_FUNCTION_NAME = 'testAppConfigFunction'

class TestUtil:
    
    def set_envs():
        os.environ[AppConfig.ENV_TEMP_FOLDER] = TEMP_FOLDER
        os.environ[AppConfig.ENV_AWS_LAMBDA_FUNCTION_NAME] = AWS_LAMBDA_FUNCTION_NAME

