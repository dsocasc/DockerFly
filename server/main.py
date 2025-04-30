from fastapi import FastAPI
from src import Server, RepoRequest
from loguru import logger as log
import sys
from os import getenv


log.add(sys.stderr, level="INFO")

app = FastAPI()
server = Server((getenv('REPO_PATH', '/repositories')))

"""
Receives a POST request with a JSON body containing the URL of the repository to clone
"""
@app.post('/repo')
async def send_repo(repo: RepoRequest):
    server.clone_git(repo.url)