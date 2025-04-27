import yaml
from loguru import logger as log


class Configuration:

    REPOSITORIES_CLONE_PATH = 'repositories_clone_path'

    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = self.read_config()

    def read_config(self):
        with open(self.config_path, 'r') as file:
            config = yaml.safe_load(file)
        return config
    
    def get_repo_path(self):
        return self.config.get(self.REPOSITORIES_CLONE_PATH, '/repositories/')