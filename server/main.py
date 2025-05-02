from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src import Server, RepoRequest
from loguru import logger as log
import sys
from os import getenv


log.add(sys.stderr, level="INFO")

app = FastAPI(title='DockerFly API')

try:
    repo_base_path = getenv('REPO_PATH', '/repositories')
    server = Server(path=repo_base_path)
except Exception as e:
    log.critical(f'Error initializing Server: {e}')
    sys.exit(1)

# Lista de orígenes permitidos
origins = [
    "*",
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
@app.post('/repo', status_code=202, summary="Clone a repo and deploy it")
async def send_repo(repo: RepoRequest):
    log.info(f'Received request to clone repository: {repo.url}')

    # Clone repo
    clone_result = server.clone_git(repo.url)
    if clone_result is None:
        raise HTTPException(status_code=400, detail="Failed to clone the repository.")
    repo_path, repo_name = clone_result
    log.info(f"Repository '{repo_name}' cloned at: '{repo_path}'")

    # Generate Dockerfile
    dockerfile_content = server.generate_dockerfile_content(repo_path)
    if dockerfile_content is None:
        raise HTTPException(status_code=400, detail=f"Failed to process or generate Dockerfile for '{repo_name}'. Check 'dockerfly.yaml' in the repository or server logs.")
    log.info(f"Dockerfile content generated for '{repo_name}'")

    # Desplegar app
    # TODO: Issue #4

@app.get("/", summary="Check API status")
async def root():
    return {"message": "DockerFly Server is running"}


