# Server
This server receives a POST request with a JSON body containing the URL of the repository to clone.

## Configuration
Under the **server** section in [config.yml](../config.yml):
- The path where the repositories will be cloned can be specified in the [config.yml](../config.yml) file using the **repositories_clone_path** variable.
- The exposed port can be specified in the [config.yml](../config.yml) file using the **exposed_port** variable.
- The URL (for nginx reverse proxy) where the server will respond can be specified in the [config.yml](../config.yml) file using the **url** variable.

## Building and running
A [Makefile](./Makefile) is available for creating the image and running the container.

- To build the image for the container, you can use the ```make build``` command.
- To create and run the container, you can use the ```make run``` command that uses the [container_run.sh](./devops/container_run.sh) script. The script reads the [config.yml](../config.yml) file, creates the necessary directory, and runs the container with the directory mounted as a volume. (Make sure the script has execute permissions)

## Usage
For sending a repo URL to the server, send a POST request with a JSON body containing the URL of the repository to clone.

```
curl -X 'POST' \
  'http://server:8000/repo' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "url": "repo.git"
}'
```