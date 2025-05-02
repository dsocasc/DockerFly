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
@app.post('/repo', status_code=202, summary="Clone a repo, generate Dockerfile and deploy application")
async def send_repo(repo_request: RepoRequest):
    """
    Received Git repo URL, clones it, generates Dockerfile based on dockerfly.yaml,
    builds the image and runs the container.
    """

    log.info(f'Received request for repository: {repo_request.url}')

    # 1. Clone repo
    clone_result = server.clone_git(repo_request.url)
    if clone_result is None:
        raise HTTPException(
            status_code=400,
            detail="Failed to clone the repository. Check URL or server logs"
        )
    repo_path, repo_name = clone_result
    log.info(f"Repository '{repo_name}' cloned at: '{repo_path}'")

    # 2. Generate Dockerfile
    generation_result = server.generate_dockerfile_content(repo_path)
    if generation_result is None:
        raise HTTPException(
            status_code=400,
            detail="Failed to generate Dockerfile for '{repo_name}'. Check 'dockerfly.yaml' or server logs"
        )

    dockerfile_content, app_config = generation_result
    log.info(f"Dockerfile content generated for '{repo_name}' based on its 'dockerfly.yaml'")

    # 3. Deploy application
    try:
        deployment_result = server.deploy_app(repo_path, repo_name, dockerfile_content, app_config)
        if deployment_result is None:
            raise HTTPException(
                status_code=500,
                detail=f"Deployment failed for '{repo_name}'. Check server logs"
            )

        log.success(f"Deployment succesful for '{repo_name}'. Result: {deployment_result}")
        return deployment_result
    except Exception as e:
        log.exception(f"Unexpected error during deployment step for '{repo_name}': {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Deployment step failed unexpectedly for '{repo_name}'. Check server logs",
        ) from e

@app.get("/", summary="Check API status")
async def root():
    return {"message": "DockerFly Server is running"}


