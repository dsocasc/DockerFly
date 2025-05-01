from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src import Server, RepoRequest
from loguru import logger as log
import sys
from os import getenv

log.add(sys.stderr, level="INFO")

app = FastAPI()
server = Server((getenv('REPO_PATH', '/repositories')))

# Lista de orígenes permitidos
origins = [
    "http://dockerfly.nimbus.net",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            
    allow_credentials=True,
    allow_methods=["*"],              
    allow_headers=["*"],
)

"""
Receives a POST request with a JSON body containing the URL of the repository to clone
"""
@app.post('/repo')
async def send_repo(repo: RepoRequest):
    server.clone_git(repo.url)