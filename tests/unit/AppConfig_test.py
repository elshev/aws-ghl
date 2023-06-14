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
        assert value == TEMP_FOLDER


    def test_when_env_is_not_set(self):
        # Arrange
        TestUtil.set_envs()
        os.environ.pop(AppConfig.ENV_TEMP_FOLDER, None)
        
        # Act
        value = AppConfig.get_temp_folder_path()
        
        #Assert
        assert value == AppConfig.TEMP_FOLDER_DEFAULT


class TestGetTempFilePath:

    def test_when_env_is_set(self):
        # Arrange
        file_path = 'testEnvSet.txt'
        TestUtil.set_envs()
        
        # Act
        value = AppConfig.get_temp_file_path(file_path)
        
        #Assert
        assert value == f'{TEMP_FOLDER}/{file_path}'


    def test_when_env_is_not_set(self):
        # Arrange
        file_path = 'testEnvNotSet.txt'
        TestUtil.set_envs()
        os.environ.pop(AppConfig.ENV_TEMP_FOLDER, None)
        
        # Act
        value = AppConfig.get_temp_file_path(file_path)
        
        #Assert
        assert value == f'{AppConfig.TEMP_FOLDER_DEFAULT}/{file_path}'
