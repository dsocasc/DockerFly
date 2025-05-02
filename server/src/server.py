from git import Repo, GitCommandError
import os
import yaml
from loguru import logger as log
import io
import shutil
from typing import Optional, Tuple, Dict, Any
import docker
from docker.errors import BuildError, APIError, NotFound
from git.remote import FetchInfo

class Server:

    # Constructor for the Server class
    def __init__(self, path: str = '/repositories/', main_config: Dict[str, Any] = None):
        # Path
        try:
            os.makedirs(path, exist_ok=True)
            self.path = path
            self.main_config = main_config or {}
            log.info(f'Repository base path set to {path}')
        except OSError as e:
            log.critical(f'Cannot create or access repository base path {path}: {e}')
            raise

        # Docker client
        try:
            self.docker_client = docker.from_env()
            self.docker_client.ping()
            log.info('Docker client initialized successfully.')
        except Exception as e:
            log.critical(f'Error initializing Docker client: {e}')
            raise

        self.deployed_apps: Dict[str, Dict[str, Any]] = {}


    def _log_git_progress(self, op_code, cur_count, max_count=None, message=''):
        log.debug(f"Cloning progress: Op={op_code}, Count={cur_count}, Max={max_count or 'N/A'}, Msg='{message.strip() or '...'}'")

    # Receives the URL of the repository to clone
    def clone_git(self, repo_url: str) -> tuple[str, str] | None:
        """
        Clones a Git repository from the given URL into the specified path.
        :param repo_url: URL of the Git repository to clone.
        :return: Tuple containing the path to the cloned repository, the name and URL.
        """
        log.info(f'Received URL in clone_git: "{repo_url}"')

        # Validación básica de URL
        if not isinstance(repo_url, str) or not repo_url.startswith(("https://", "http://", "git@")):
            log.error(f'Invalid or unsupported URL provided: {repo_url}')

        log.info(f'Attempting to clone repository from {repo_url} into {self.path}')
        repo_clone_path = None

        try:
            repo_name = repo_url.split('/')[-1].replace('.git', '')

            if not repo_name:
                raise ValueError('Repository name could not be extracted from the URL.')

            repo_clone_path = os.path.join(self.path, repo_name)
            log.debug(f'Calculated clone path: {repo_clone_path}')

            if os.path.exists(repo_clone_path):
                log.error(f'Repository {repo_name} already exists. Skipping clone.')
                # TODO: Decidir si ignorar o actualizar el repositorio existente
                return repo_clone_path, repo_name, repo_url

            Repo.clone_from(repo_url, repo_clone_path, progress=self._log_git_progress)
            log.success(f'Repository cloned successfully to {repo_clone_path}')
            return repo_clone_path, repo_name, repo_url

        except ValueError as ve:
            log.error(f'Error processing repository URL/name: {ve}')
            return None
        except GitCommandError as gce:
            log.error(f'Git command error: {gce.command} - {gce.stderr}')

            # Clean up the partially cloned repository
            if repo_clone_path and os.path.exists(repo_clone_path):
                try:
                    shutil.rmtree(repo_clone_path)
                    log.info(f'Cleaned up partial clone at {repo_clone_path}')
                except Exception as e:
                    log.error(f'Error during cleanup of {repo_clone_path}: {e}')
            return None
        except Exception as e:
            log.error(f'Unexpected error during git clone: {e}')
            if repo_clone_path and os.path.exists(repo_clone_path):
                try:
                    shutil.rmtree(repo_clone_path)
                    log.info(f'Cleaned up partial clone at {repo_clone_path}')
                except Exception as e:
                    log.error(f'Error during cleanup of {repo_clone_path}: {e}')

            return None

    def generate_dockerfile_content(self, repo_path: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        """
        Generates the content of the Dockerfile based on dockerfly.yaml in the repo.
        Returns a tuple [dockerfile_content, parsed_config], or None if it fails.
        """
        dockerfly_yaml_path = os.path.join(repo_path, 'dockerfly.yaml')
        log.info(f"Looking for configuration file: {dockerfly_yaml_path}")

        if not os.path.isfile(dockerfly_yaml_path):
            log.error(f"Configuration file 'dockerfly.yaml' not found or is not a file in {repo_path}")
            return None

        try:
            with open(dockerfly_yaml_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            if not isinstance(config, dict):
                 log.error(f"Configuration file '{dockerfly_yaml_path}' is empty or has invalid format.")
                 return None
            log.success(f"Loaded configuration from {dockerfly_yaml_path}")
        except yaml.YAMLError as e:
            log.error(f"Error parsing YAML file {dockerfly_yaml_path}: {e}")
            return None
        except IOError as e:
             log.error(f"Error reading file {dockerfly_yaml_path}: {e}")
             return None
        except Exception as e:
             log.error(f"Unexpected error processing config {dockerfly_yaml_path}: {e}")
             return None


        python_version = config.get('python_version', '3.10')
        requirements_file = config.get('requirements_file', 'requirements.txt')
        port = config.get('port')
        start_command_list = config.get('start_command')
        # volumes = config.get('volumes', []) # Volumes are optional.

        errors = []
        if not isinstance(python_version, str): errors.append("'python_version' must be a string (e.g., '3.10').")
        if not isinstance(requirements_file, str) or not requirements_file: errors.append("'requirements_file' must be a non-empty string (path).")
        if not isinstance(port, int) or port <= 0 or port > 65535: errors.append("'port' must be a valid integer (1-65535).")
        if not start_command_list or not isinstance(start_command_list, list) or not all(isinstance(item, str) for item in start_command_list):
            errors.append("'start_command' must be a list of strings (e.g., ['python', 'app.py']).")

        if errors:
            for error in errors: log.error(f"Invalid dockerfly.yaml: {error}")
            return None

        req_file_path_in_repo = os.path.join(repo_path, requirements_file)
        if not os.path.isfile(req_file_path_in_repo):
            log.error(f"Specified requirements file '{requirements_file}' not found at '{req_file_path_in_repo}'. Cannot proceed.")
            return None

        # Dockerfile content generation
        log.info("Generating Dockerfile content...")
        dockerfile_lines = [
            "# Auto-generated by DockerFly",
            f"FROM python:{python_version}-slim",
            "",
            "WORKDIR /app",
            "",
        ]
        # Copy requirements file to the working directory
        # (Docker COPY command uses the context path, not the absolute path)
        req_copy_path = requirements_file.replace(os.path.sep, '/') # Asegurar formato path para Docker COPY
        dockerfile_lines.append("# Copy and install requirements")
        dockerfile_lines.append(f"COPY {req_copy_path} ./{os.path.basename(req_copy_path)}") # Copiar al directorio de trabajo
        dockerfile_lines.extend(
            (
                f"RUN pip install --no-cache-dir -r {os.path.basename(req_copy_path)}",
                "",
                "# Copy application code",
                "COPY . .",
                "",
                "# Expose the application port",
            )
        )
        dockerfile_lines.extend((f"EXPOSE {port}", ""))
        cmd_json_array = '[' + ', '.join(f'"{item}"' for item in start_command_list) + ']'
        dockerfile_lines.append("# Set the start command")
        dockerfile_lines.append(f"CMD {cmd_json_array}")

        dockerfile_content = "\n".join(dockerfile_lines)
        log.debug(f"Generated Dockerfile:\n---\n{dockerfile_content}\n---")
        log.success("Dockerfile content generated successfully.")

        return dockerfile_content, config

    def deploy_app(self, repo_path: str, repo_name: str, repo_url: str, dockerfile_content: str, app_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Construye la imagen Docker y lanza el contenedor para la aplicación.
        Devuelve un diccionario con info del despliegue o None si falla.
        """
        app_name = app_config.get('app_name', repo_name)
        image_tag = f"dockerfly/{app_name}:latest".lower().replace(" ", "-")
        container_name = f"app-{app_name}".lower().replace(" ", "-")
        network_name = self.main_config.get('docker', {}).get('network_name', 'bridge')
        container_port = app_config.get('port')

        generated_dockerfile_path = os.path.join(repo_path, "Dockerfile.dockerfly") # Usar nombre distinto? O 'Dockerfile'
        try:
            with open(generated_dockerfile_path, 'w', encoding='utf-8') as f:
                f.write(dockerfile_content)
            log.info(f"Generated Dockerfile content written to: {generated_dockerfile_path}")
        except IOError as e:
            log.error(f"Failed to write generated Dockerfile to {generated_dockerfile_path}: {e}")
            return None

        log.info(f"Starting deployment for app '{app_name}'...")

        # 1. Build the image using the Dockerfile content
        try:
            log.info(f"Building image '{image_tag}' from context path '{repo_path}'...")
            image, build_logs_stream = self.docker_client.images.build(
                path=repo_path,
                dockerfile=os.path.basename(generated_dockerfile_path),
                tag=image_tag,
                rm=True,
                forcerm=True
            )
            log.success(f"Image built successfully: {image.short_id} ({image.tags[0]})")

        except BuildError as e:
            log.error(f"Docker build failed for image '{image_tag}':")
            log.error("Attempting to log detailed build output:")
            # Iterar sobre el generador de logs del build
            for line in e.build_log:
                if isinstance(line, dict) and 'stream' in line:
                    log.error(line['stream'].strip())
                elif isinstance(line, str):
                    log.error(line.strip())
            return None
        except APIError as e:
            log.error(f"Docker API error during build for '{image_tag}': {e}")
            return None
        except Exception as e:
            log.exception(f"Unexpected error during image build for '{image_tag}': {e}")
            return None

        # 2. Stop and remove existing container (if any)
        try:
            existing_container = self.docker_client.containers.get(container_name)
            log.warning(f"Found existing container '{container_name}'. Stopping and removing...")
            existing_container.stop(timeout=10) # Dar tiempo para parar grácilmente
            existing_container.remove()
            log.info(f"Existing container '{container_name}' removed.")
        except NotFound:
            log.info(f"No existing container named '{container_name}'.")
        except APIError as e:
            log.error(f"Docker API error stopping/removing container '{container_name}': {e}")
            return None

        # 3. Launch the new container with dynamic port mapping
        try:
            log.info(f"Starting new container '{container_name}' from image '{image_tag}'...")

            volumes_to_mount = {}
            for volume_mapping in app_config.get('volumes', []):
                 if isinstance(volume_mapping, str) and ':' in volume_mapping:
                     host_part, container_part = volume_mapping.split(':', 1)
                     if host_part.startswith('/'):
                         log.warning(f"Mounting host path '{host_part}' - Ensure permissions are correct on the host.")
                         # Crear ruta host si no existe? Podría ser peligroso.
                         # os.makedirs(host_part, exist_ok=True)
                     volumes_to_mount[host_part] = {'bind': container_part, 'mode': 'rw'}
                 else:
                     log.warning(f"Skipping invalid volume format in dockerfly.yaml: '{volume_mapping}'. Expected 'host_path_or_named_volume:container_path'.")

            # --- Preparar Variables de Entorno ---
            environment_vars = app_config.get('environment_variables', {})
            if not isinstance(environment_vars, dict):
                 log.warning("'environment_variables' in dockerfly.yaml is not a dictionary. Ignoring.")
                 environment_vars = {}


            container = self.docker_client.containers.run(
                image=image_tag,
                name=container_name,
                network=network_name,
                ports={f'{container_port}/tcp': None},
                volumes=volumes_to_mount,
                environment=environment_vars,
                detach=True,
                restart_policy={"Name": "unless-stopped"}
            )

            container.reload()

            assigned_host_port = None
            try:
                port_data = container.ports.get(f'{container_port}/tcp')
                if port_data and isinstance(port_data, list) and len(port_data) > 0:
                    assigned_host_port = port_data[0].get('HostPort')
                if not assigned_host_port: raise ValueError("HostPort not found") # Forzar error si no se encuentra
            except Exception as port_e:
                 log.error(f"Could not determine assigned host port for container '{container_name}': {port_e}")
                 raise

            # Build access URL (assuming localhost, could be configurable)
            # TODO: Get the host IP/hostname more reliably if not localhost
            host_access_point = "localhost"
            access_url = f"http://{host_access_point}:{assigned_host_port}"

            log.success(f"Container '{container_name}' started successfully (ID: {container.short_id}).")
            log.info(f"App '{app_name}' running internally on port {container_port}. Access via: {access_url}")

            try:
                cloned_repo_git = Repo(repo_path)
                current_commit_hash = cloned_repo_git.head.commit.hexsha
                log.debug(f"Stored state for '{container_name}': {current_commit_hash[:7]}")

                self.deployed_apps[container_name] = {
                    "repo_url": repo_url,
                    "repo_path": repo_path,
                    "repo_name": repo_name,
                    "app_name": app_name,
                    "last_commit": current_commit_hash,
                    "container_id": container.id,
                    "image_tag": image_tag,
                    "app_config": app_config,
                }

                deployment_info = {
                    "message": "Deployment successful",
                    "app_name": app_name,
                    "container_name": container_name,
                    "container_id": container.short_id,
                    "image_tag": image_tag,
                    "internal_port": container_port,
                    "assigned_host_port": assigned_host_port,
                    "access_url": access_url,
                    "current_commit": current_commit_hash
                }

                return deployment_info
            except Exception as e:
                log.error(f"Failed to get current commit or store state for '{container_name}': {e}")
                deployment_info = {
                    "message": "Deployment succesful but failed to store state",
                    "app_name": app_name,
                    "container_name": container_name,
                    "container_id": container.short_id,
                    "image_tag": image_tag,
                    "internal_port": container_port,
                    "assigned_host_port": assigned_host_port,
                    "access_url": access_url,
                    "current_commit": None
                }
        except APIError as e:
            log.error(f"Docker API error starting container '{container_name}': {e}")
            return None
        except Exception as e:
            log.exception(f"Unexpected error running container '{container_name}': {e}")
            return None
    
    async def check_all_updates(self):
        log.info(f"Checking updates for {len(self.deployed_apps)} deployed app(s).")
        apps_to_update = []
        for container_name, app_state in self.deployed_apps.items():
            repo_path = app_state.get('repo_path')
            last_known_commit = app_state.get('last_commit')
            log.debug(f"Checking app '{container_name}' at {repo_path} for updates...")
            if not repo_path or not last_known_commit:
                log.error(f"Skipping app '{container_name}': missing state information.")
                continue

            try:
                cloned_repo = Repo(repo_path)
                # Fetch updates from the remote repository
                try:
                    origin = cloned_repo.remotes.origin
                    log.debug(f"Fetching updates for '{container_name}' from remote '{origin.name}'...")
                    origin.fetch()
                except Exception as fetch_e:
                    log.error(f"Failed to fetch updates for '{container_name}': {fetch_e}")
                    continue

                # Get current HEAD
                default_branch = 'main'
                local_commit = cloned_repo.head.commit
                remote_commit = None
                if default_branch in origin.refs:
                    remote_commit = origin.refs[default_branch].commit
                else:
                    default_branch = 'master'
                    if default_branch in origin.refs:
                        remote_commit = origin.refs[default_branch].commit
                
                if not remote_commit:
                    log.warning(f"Could not find default branch ({default_branch} or master) in remote for '{container_name}'. Skipping update check.")
                    continue

                # Compare hashes
                if local_commit.hexsha != remote_commit.hexsha:
                    log.info(f"Update detected for '{container_name}'! Local: {local_commit.hexsha[:7]}, Remote: {remote_commit.hexsha[:7]}")
                    # It woould be ideal to launch the update in a separate thread or task
                    # to avoid blocking the main thread. For now, we will just call the update function directly.
                    await self.trigger_update(container_name, app_state)
                else:
                    log.debug(f"App '{container_name}' is up-to-date.")
            
            except Exception as e:
                log.error(f"Error checking repository at '{repo_path}' for app '{container_name}': {e}")

    async def trigger_update(self, container_name: str, app_state: Dict[str, Any]):
        """Realiza git pull y redespliega la aplicación."""
        repo_path = app_state['repo_path']
        repo_name = app_state['repo_name'] # Necesitamos el repo_name original
        log.info(f"Triggering update for '{container_name}'...")

        try:
            cloned_repo = Repo(repo_path)
            origin = cloned_repo.remotes.origin
            log.info(f"Pulling changes for '{container_name}'...")
            pull_info = origin.pull()

            if pull_info[0].flags & FetchInfo.HEAD_UPTODATE:
                log.info(f"Pull completed for '{container_name}', but no changes detected.")
                app_state['last_commit'] = cloned_repo.head.commit.hexsha
                return # Doesn't need to redeploy if no changes

            new_commit_hash = cloned_repo.head.commit.hexsha
            log.success(f"Successfully pulled updates for '{container_name}'. New commit: {new_commit_hash[:7]}")

            # Generate a new Dockerfile content (in case the dockerfly.yaml changed)
            generation_result = self.generate_dockerfile_content(repo_path)
            if generation_result is None:
                log.error(f"Update failed for '{container_name}': Could not regenerate Dockerfile after pull.")
                return
            dockerfile_content, new_app_config = generation_result

            log.info(f"Redeploying application '{container_name}'...")
            deployment_result = self.deploy_app(repo_path, repo_name, dockerfile_content, new_app_config)

            if deployment_result:
                log.success(f"Update deployment successful for '{container_name}'.")
                self.deployed_apps[container_name].update({
                    "last_commit": new_commit_hash,
                    "container_id": deployment_result.get("container_id"),
                    "image_tag": deployment_result.get("image_tag"),
                    "app_config": new_app_config
                })
            else:
                # Only log for now, could implement rollback logic later.
                log.error(f"Update failed for '{container_name}' during redeployment step.")

        except GitCommandError as git_err:
            log.error(f"Update failed for '{container_name}': Git pull failed. Command: '{git_err.command}'. Stderr: '{git_err.stderr.strip()}'")
        except Exception as e:
            log.exception(f"Unexpected error during update trigger for '{container_name}': {e}")

