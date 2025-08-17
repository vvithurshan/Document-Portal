import yaml
import os
from logger.custom_logger import CustomLogger

# Assuming this file is in /utils and config is at the project root.
# This makes the path resolution independent of the current working directory.
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
_DEFAULT_CONFIG_PATH = os.path.join(_PROJECT_ROOT, 'config', 'config.yaml')

log = CustomLogger().get_logger(__name__)

def load_config(config_path: str = _DEFAULT_CONFIG_PATH):
    """
    Loads a YAML configuration file.

    Args:
        config_path (str): The path to the configuration file.

    Returns:
        dict: The loaded configuration.

    Raises:
        FileNotFoundError: If the config file is not found.
        yaml.YAMLError: If there is an error parsing the file.
    """
    if not os.path.exists(config_path):
        log.error(f"Configuration file not found. path={config_path}")
        raise FileNotFoundError(f"Config file not found at {config_path}")
    
    try:
        with open(config_path, 'r', encoding='utf-8') as config_file:
            config = yaml.safe_load(config_file)
        log.info(f"Configuration loaded successfully. path={config_path}")
        return config
    except yaml.YAMLError as e:
        log.error(f"Error parsing YAML configuration file. path={config_path}, error={e}")
        raise

if __name__ == '__main__':
    try:
        config = load_config()
        print("Config loaded successfully:")
        import json
        print(json.dumps(config, indent=2))
    except (FileNotFoundError, yaml.YAMLError) as e:
        print(f"Failed to load config: {e}")