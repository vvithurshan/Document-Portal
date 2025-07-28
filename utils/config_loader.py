import yaml
import os

config_path = os.path.join('config', 'config.yaml')

def load_config(config_path: str = config_path):
    with open(config_path, 'r') as config_file:
        config = yaml.safe_load(config_file)
    print(config)
    return config

load_config()