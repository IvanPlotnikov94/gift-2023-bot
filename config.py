import json
import os

BASE_PATH = os.path.dirname(os.path.realpath(__file__))
path_to_config = BASE_PATH + "/config.json"
error_message = "Can't read a config file"

def read_whole_config():
    try:
        with open(path_to_config, 'r') as f:
            return json.load(f)
    except:
        return error_message
        
def read_config_for_db():
    try:
        with open(path_to_config, 'r') as f:
            return json.load(f)["database_settings"]
    except:
        return error_message

def get_token():
    try:
        with open(path_to_config, 'r') as f:
            return json.load(f)["token"]
    except:
        return error_message

def get_admin_ids():
    try:
        with open(path_to_config, 'r') as f:
            return json.load(f)["admin"]
    except:
        return error_message