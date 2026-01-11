import os

def create_folder(path):
    if not os.path.isdir(path):
        os.makedirs(path)
        