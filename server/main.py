from fastapi import FastAPI
from src import Server, RepoRequest, Configuration
from loguru import logger as log
import sys


log.add(sys.stderr, level="INFO")

app = FastAPI()
config = Configuration('./resources/config.yml')
server = Server(config.get_repo_path())

"""
Receives a POST request with a JSON body containing the URL of the repository to clone
"""
@app.post('/repo')
async def send_repo(repo: RepoRequest):
    server.clone_git(repo.url)