import os
import pytest
from src.AppConfig import AppConfig
from TestUtil import *

class TestTempFolderAndPath:

    def test_get_temp_folder(self):
        # Arrange
        TestUtil.init_envs()
        
        # Act
        value = AppConfig.get_temp_folder_path()
        
        #Assert
        assert value == TEST_TEMP_FOLDER


    def test_get_temp_folder_default(self):
        # Arrange
        TestUtil.init_envs(remove_envs=[AppConfig.ENV_TEMP_FOLDER])
        
        # Act
        value = AppConfig.get_temp_folder_path()
        
        #Assert
        assert value == AppConfig.DEFAULT_TEMP_FOLDER


    def test_get_temp_file(self):
        # Arrange
        file_path = 'testEnvSet.txt'
        TestUtil.init_envs()
        
        # Act
        value = AppConfig.get_temp_file_path(file_path)
        
        #Assert
        assert value == f'{TEST_TEMP_FOLDER}/{file_path}'


    def test_get_temp_file_default(self):
        # Arrange
        file_path = 'testEnvNotSet.txt'
        TestUtil.init_envs(remove_envs=[AppConfig.ENV_TEMP_FOLDER])
        
        # Act
        value = AppConfig.get_temp_file_path(file_path)
        
        #Assert
        assert value == f'{AppConfig.DEFAULT_TEMP_FOLDER}/{file_path}'


    def test_when_started_with_path(self):
        # Arrange
        TestUtil.init_envs()
        file_path = f'TestFolder/testWithPath.txt'
        
        # Act
        value = AppConfig.get_temp_file_path(file_path)
        
        #Assert
        assert value == f'{TEST_TEMP_FOLDER}/{file_path}'


    def test_when_started_with_temp_folder_path(self):
        # Arrange
        TestUtil.init_envs()
        file_path = f'{os.environ[AppConfig.ENV_TEMP_FOLDER]}/testWithPath.txt'
        
        # Act
        value = AppConfig.get_temp_file_path(file_path)
        
        #Assert
        assert value == file_path


class TestAppConfig:

    def test_get_aws_region(self):
        # Arrange
        TestUtil.init_envs()
        
        # Act
        value = AppConfig.get_aws_region()
        
        #Assert
        assert value == TEST_AWS_REGION

    def test_get_aws_region_default(self):
        # Arrange
        TestUtil.init_envs(remove_envs=[AppConfig.ENV_AWS_REGION])
        
        # Act
        value = AppConfig.get_aws_region()
        
        #Assert
        assert value == AppConfig.DEFAULT_AWS_REGION

