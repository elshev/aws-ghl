import os
import pytest
from AppConfig import AppConfig

TEMP_FOLDER = '/tmp/TestAppConfig'
AWS_LAMBDA_FUNCTION_NAME = 'testAppConfigFunction'

def set_envs():
    os.environ[AppConfig.ENV_TEMP_FOLDER] = TEMP_FOLDER
    os.environ[AppConfig.ENV_AWS_LAMBDA_FUNCTION_NAME] = AWS_LAMBDA_FUNCTION_NAME

class TestGetTempFolderPath():

    def test_get_temp_folder_path_when_env_is_set(self):
        # Arrange
        set_envs()
        
        # Act
        value = AppConfig.get_temp_folder_path()
        
        #Assert
        assert value == TEMP_FOLDER


    def test_get_temp_folder_path_when_env_is_not_set(self):
        # Arrange
        
        # Act
        value = AppConfig.get_temp_folder_path()
        
        #Assert
        assert value == AppConfig.TEMP_FOLDER_DEFAULT
