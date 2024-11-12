# config_loader.py

import yaml

def load_config(file_path):
    """
    Load the YAML configuration file and parse it.
    :param file_path: Path to the YAML configuration file.
    :return: Parsed configuration dictionary.
    """
    with open(file_path, "r") as file:
        config = yaml.safe_load(file)
    return config
