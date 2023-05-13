import os
from pathlib import Path


class Util:
    
    @staticmethod
    def write_file(file_path, content, newline=None):
        file_dir = os.path.dirname(file_path)
        if file_dir:
            Path(file_dir).mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', newline=newline) as output_file:
            output_file.write(content)
