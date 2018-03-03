import os

def local_file(path_relative_to_script):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), path_relative_to_script)
