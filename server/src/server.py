from git import Repo, GitCommandError
import os
import yaml
from loguru import logger as log
import io
import shutil
from typing import Optional, Tuple


class Server:

    # Constructor for the Server class
    def __init__(self, path: str = '/repositories/'):
        try:
            os.makedirs(path, exist_ok=True)
            self.path = path
            log.info(f'Repository base path set to {path}')
        except OSError as e:
            log.critical(f'Cannot create or access repository base path {path}: {e}')
            raise

    def _log_git_progress(self, op_code, cur_count, max_count=None, message=''):
        log.debug(f"Cloning progress: Op={op_code}, Count={cur_count}, Max={max_count or 'N/A'}, Msg='{message.strip() or '...'}'")

    # Receives the URL of the repository to clone
    def clone_git(self, repo_url: str) -> tuple[str, str] | None:
        """
        Clones a Git repository from the given URL into the specified path.
        :param repo_url: URL of the Git repository to clone.
        :return: Tuple containing the path to the cloned repository and the URL.
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
                return repo_clone_path, repo_url

            Repo.clone_from(repo_url, repo_clone_path, progress=self._log_git_progress)
            log.success(f'Repository cloned successfully to {repo_clone_path}')
            return repo_clone_path, repo_url

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

    def generate_dockerfile_content(self, repo_path: str) -> str | None:
        """
        Genera el contenido del Dockerfile basado en dockerfly.yaml en el repo.
        Devuelve el contenido del Dockerfile como string, o None si falla.
        """
        dockerfly_yaml_path = os.path.join(repo_path, 'dockerfly.yaml')
        log.info(f"Looking for configuration file: {dockerfly_yaml_path}")

        if not os.path.isfile(dockerfly_yaml_path): # Usar isfile para asegurar que no es un directorio
            log.error(f"Configuration file 'dockerfly.yaml' not found or is not a file in {repo_path}")
            return None

        try:
            with open(dockerfly_yaml_path, 'r', encoding='utf-8') as f: # Especificar encoding
                config = yaml.safe_load(f)
            if not isinstance(config, dict): # Asegurar que el YAML parsea a un diccionario
                 log.error(f"Configuration file '{dockerfly_yaml_path}' is empty or has invalid format.")
                 return None
            log.success(f"Loaded configuration from {dockerfly_yaml_path}")
        except yaml.YAMLError as e:
            log.error(f"Error parsing YAML file {dockerfly_yaml_path}: {e}")
            return None
        except IOError as e:
             log.error(f"Error reading file {dockerfly_yaml_path}: {e}")
             return None
        except Exception as e: # Captura genérica por si acaso
             log.error(f"Unexpected error processing config {dockerfly_yaml_path}: {e}")
             return None


        # --- Extraer config con valores por defecto y validaciones ---
        # app_name = config.get('app_name', os.path.basename(repo_path)) # Ya tenemos repo_name
        python_version = config.get('python_version', '3.10') # Default Python version
        requirements_file = config.get('requirements_file', 'requirements.txt') # Default requirements file
        port = config.get('port') # Puerto es importante, quizás no poner default? O validar después.
        start_command_list = config.get('start_command') # Comando de inicio es crucial.
        # volumes = config.get('volumes', []) # Volúmenes son opcionales.

        # --- Validar campos obligatorios ---
        errors = []
        if not isinstance(python_version, str): errors.append("'python_version' must be a string (e.g., '3.10').")
        if not isinstance(requirements_file, str) or not requirements_file: errors.append("'requirements_file' must be a non-empty string (path).")
        if not isinstance(port, int) or port <= 0 or port > 65535: errors.append("'port' must be a valid integer (1-65535).")
        if not start_command_list or not isinstance(start_command_list, list) or not all(isinstance(item, str) for item in start_command_list):
            errors.append("'start_command' must be a list of strings (e.g., ['python', 'app.py']).")

        if errors:
            for error in errors: log.error(f"Invalid dockerfly.yaml: {error}")
            return None

        # Verificar si el archivo de requisitos existe realmente
        req_file_path_in_repo = os.path.join(repo_path, requirements_file)
        if not os.path.isfile(req_file_path_in_repo):
            log.error(f"Specified requirements file '{requirements_file}' not found at '{req_file_path_in_repo}'. Cannot proceed.")
            return None

        # --- Construir contenido del Dockerfile ---
        log.info("Generating Dockerfile content...")
        dockerfile_lines = [
            "# Auto-generated by DockerFly",
            f"FROM python:{python_version}-slim",
            "",
            "WORKDIR /app",
            "",
        ]
        # Copiar requisitos e instalar (primero para caché de capas)
        # Nota: Si requirements_file está en subdirectorio, COPY necesita la ruta completa relativa
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
        # Comando de inicio
        # Formato JSON preferido para CMD: ["executable", "param1", "param2"]
        cmd_json_array = '[' + ', '.join(f'"{item}"' for item in start_command_list) + ']'
        dockerfile_lines.append("# Set the start command")
        dockerfile_lines.append(f"CMD {cmd_json_array}")

        dockerfile_content = "\n".join(dockerfile_lines)
        log.debug(f"Generated Dockerfile:\n---\n{dockerfile_content}\n---")
        log.success("Dockerfile content generated successfully.")
        return dockerfile_content