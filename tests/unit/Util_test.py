import pytest
from Util import Util

class TestGetDictValueWithEitherKey():

    def test_empty_with_no_raise(self):
        # Arrange
        dic = {}
        
        # Act
        value = Util.get_dict_value_with_either_key(dic, ['body'], raise_if_not_found=False)
        
        #Assert
        assert value is None


    def test_empty_with_raise(self):
        # Arrange
        dic = {}
        
        # Act
        #Assert
        with pytest.raises(ValueError, match='Dictionary does not contain either of the next keys'):
            value = Util.get_dict_value_with_either_key(dic, ['body'], raise_if_not_found=True)


    def test_key_exists(self):
        # Arrange
        expected_value = 'body123'
        dic = {
            'body': expected_value,
            'Key1': 'bbbb789'
        }
        
        # Act
        value = Util.get_dict_value_with_either_key(dic, ['body'])
        
        #Assert
        assert value == expected_value


    def test_first_key_exists(self):
        # Arrange
        expected_value = 'body123'
        dic = {
            'body': expected_value,
            'Key1': 'bbbb789'
        }
        
        # Act
        value = Util.get_dict_value_with_either_key(dic, ['body', 'Body'])
        
        #Assert
        assert value == expected_value

    def test_second_key_exists(self):
        # Arrange
        expected_value = 'Body123'
        dic = {
            'Body': expected_value,
            'Key1': 'bbbb789'
        }
        
        # Act
        value = Util.get_dict_value_with_either_key(dic, ['body', 'Body'])
        
        #Assert
        assert value == expected_value

    
    def test_both_keys_exist(self):
        # Arrange
        first_value = 'body123'
        second_value = 'Body456'
        dic = {
            'body': first_value,
            'Body': second_value,
            'Key1': 'bbbb789'
        }
        
        # Act
        value = Util.get_dict_value_with_either_key(dic, ['body', 'Body'])
        
        #Assert
        assert value == first_value

    def test_none_keys_exist(self):
        # Arrange
        dic = {
            'body1': 'some Value',
            'Key1': 'bbbb789'
        }
        
        # Act
        value = Util.get_dict_value_with_either_key(dic, ['body', 'Body'], raise_if_not_found=False)
        
        #Assert
        assert value is None
