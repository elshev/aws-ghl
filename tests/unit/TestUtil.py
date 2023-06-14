import os
from typing import Iterable
import pytest
from AppConfig import AppConfig

TEST_TEMP_FOLDER = '/tmp/TestAppConfig'
TEST_AWS_LAMBDA_FUNCTION_NAME = 'testAppConfigFunction'
TEST_AWS_REGION = 'us-test-2'
TEST_SQS_MAILGUN_EVENTS_QUEUE_NAME = 'test-mgevents-queue'
TEST_MAILGUN_API_URL = 'https://api.test-mailgun.net/v3/test'

class TestUtil:
    
    @staticmethod
    def init_envs(remove_envs: Iterable = None):
        os.environ[AppConfig.ENV_TEMP_FOLDER] = TEST_TEMP_FOLDER
        os.environ[AppConfig.ENV_AWS_LAMBDA_FUNCTION_NAME] = TEST_AWS_LAMBDA_FUNCTION_NAME
        os.environ[AppConfig.ENV_AWS_REGION] = TEST_AWS_REGION
        os.environ[AppConfig.ENV_SQS_MAILGUN_EVENTS_QUEUE_NAME] = TEST_SQS_MAILGUN_EVENTS_QUEUE_NAME
        os.environ[AppConfig.ENV_MAILGUN_API_URL] = TEST_MAILGUN_API_URL

        if not remove_envs:
            return
        for env in remove_envs:
            TestUtil.del_env(env)

    @staticmethod
    def del_env(env_name):
        os.environ.pop(env_name, None)
        
