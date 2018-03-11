import os

_base_path = './'

def set_base_path(path):
    global _base_path
    _base_path = path

def local_file(path_relative_to_project_base):
    return os.path.abspath(os.path.join(_base_path, path_relative_to_project_base))
