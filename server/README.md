# Server
This server receives a POST request with a JSON body containing the URL of the repository to clone.

## Configuration
The path where the repositories will be cloned can be specified in the [./resources/config.yml](./resources/config.yml) file using the **repositories_clone_path** variable.

## Building
A [Makefile](./Makefile) is available for creating the image and running the container.

## Deployment
There is a [Dockerfile](./devops/Dockerfile) for running the server using a container, the exposed port is 5000.

## Usage
For sending a repo URL to the server, send a POST request with a JSON body containing the URL of the repository to clone to **/repo**.