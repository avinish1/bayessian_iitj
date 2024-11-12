import yaml
from models import Config

class ConfigParser:
    def __init__(self, yaml_file):
        self.yaml_file = yaml_file
        self.config = self.load_and_validate_config()

    def load_and_validate_config(self):
        with open(self.yaml_file, 'r') as file:
            config_data = yaml.safe_load(file)
        return Config(**config_data)

    def get_variable_data(self):
        return self.config.variables
