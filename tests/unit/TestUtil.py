import os
import pytest
from AppConfig import AppConfig

TEST_TEMP_FOLDER = '/tmp/TestAppConfig'
TEST_AWS_LAMBDA_FUNCTION_NAME = 'testAppConfigFunction'
TEST_AWS_REGION = 'us-test-2'

class TestUtil:
    
    def set_envs():
        os.environ[AppConfig.ENV_TEMP_FOLDER] = TEST_TEMP_FOLDER
        os.environ[AppConfig.ENV_AWS_LAMBDA_FUNCTION_NAME] = TEST_AWS_LAMBDA_FUNCTION_NAME
        os.environ[AppConfig.ENV_AWS_REGION] = TEST_AWS_REGION

