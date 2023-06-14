import os
import pytest
from src.AppConfig import AppConfig
from TestUtil import *

class TestGetTempFolderPath:

    def test_when_env_is_set(self):
        # Arrange
        TestUtil.set_envs()
        
        # Act
        value = AppConfig.get_temp_folder_path()
        
        #Assert
        assert value == TEST_TEMP_FOLDER


    def test_when_env_is_not_set(self):
        # Arrange
        TestUtil.set_envs()
        os.environ.pop(AppConfig.ENV_TEMP_FOLDER, None)
        
        # Act
        value = AppConfig.get_temp_folder_path()
        
        #Assert
        assert value == AppConfig.DEFAULT_TEMP_FOLDER


class TestGetTempFilePath:

    def test_when_env_is_set(self):
        # Arrange
        file_path = 'testEnvSet.txt'
        TestUtil.set_envs()
        
        # Act
        value = AppConfig.get_temp_file_path(file_path)
        
        #Assert
        assert value == f'{TEST_TEMP_FOLDER}/{file_path}'


    def test_when_env_is_not_set(self):
        # Arrange
        file_path = 'testEnvNotSet.txt'
        TestUtil.set_envs()
        os.environ.pop(AppConfig.ENV_TEMP_FOLDER, None)
        
        # Act
        value = AppConfig.get_temp_file_path(file_path)
        
        #Assert
        assert value == f'{AppConfig.DEFAULT_TEMP_FOLDER}/{file_path}'


class TestGetStatics:

    def test_get_aws_region(self):
        # Arrange
        TestUtil.set_envs()
        
        # Act
        value = AppConfig.get_aws_region()
        
        #Assert
        assert value == TEST_AWS_REGION

    def test_get_aws_region_default(self):
        # Arrange
        TestUtil.set_envs()
        os.environ.pop(AppConfig.ENV_AWS_REGION, None)
        
        # Act
        value = AppConfig.get_aws_region()
        
        #Assert
        assert value == AppConfig.DEFAULT_AWS_REGION

