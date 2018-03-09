import os

def local_file(script, path_relative_to_script):
    return os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(script)), path_relative_to_script))
