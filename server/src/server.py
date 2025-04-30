from git import Repo
import os
from loguru import logger as log


class Server:

    # Constructor for the Server class
    def __init__(self, path: str = '/repositories/'):
        self.path = path

    # Receives the URL of the repository to clone
    def clone_git(self, repo: str):
        log.info(f'Cloning repository from {repo}...')

        repo_name = repo.split('/')[-1].replace('.git', '')

        path = os.path.join(self.path, repo_name)

        if os.path.exists(path):
            log.error(f'Repository {repo_name} already exists. Skipping clone.')
            return
        
        os.makedirs(path)
        Repo.clone_from(repo, path)