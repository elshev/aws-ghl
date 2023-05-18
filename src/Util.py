import logging
import os
from pathlib import Path
from typing import Iterable


class Util:
    
    @staticmethod
    def log_lambda_event(event, context):
        logging.info('Event: %s', event)
        if not context is None:
            logging.info('Context: %s', context)

        
    @staticmethod
    def get_dict_value(dic: dict, keys: Iterable[str]):
        """
        Returns a value from nested dictionaries.
        If any key from keys doesn't exist, returns None

        Args:
            dic (dict): Dictionary to get value from
            keys (Iterable[str]): List of keys that form a path to the value

        Returns:
            str: Returns value if all 'keys path' exist
        Example:
            get_str_value(some_dict, ['message', 'headers', 'subject'])
            Returns 'SomeSubjectValue' value for dictionaries like this:
            {
                'message': 
                {
                    'headers': 
                    { 
                        'subject': 'SomeSubjectValue' 
                    }
                }
            }
            
        """
        cur_dict = dic
        for key in keys:
            val = cur_dict.get(key)
            if key == keys[-1]:
                return str(val)
            cur_dict = val
        return None
    
    @staticmethod
    def get_dict_float_value(dic: dict, keys: Iterable[str]):
        s = Util.get_dict_value(dic, keys)
        try:
            return float(s)
        except ValueError:
            return None

    @staticmethod
    def get_dict_int_value(dic: dict, keys: Iterable[str]):
        s = Util.get_dict_value(dic, keys)
        return int(s) if s.isdecimal() else None


    @staticmethod
    def write_file(file_path, content, newline=None):
        file_dir = os.path.dirname(file_path)
        if file_dir:
            Path(file_dir).mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', newline=newline) as output_file:
            output_file.write(content)
