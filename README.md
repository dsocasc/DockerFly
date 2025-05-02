# DockerFly
This project proposes the creation of a tool to automate the deployment of Python applications. The goal is for a user to specify a project, so that the system receives it, processes it, and automatically launches it inside a container, without requiring any additional technical intervention.

![Alt text](DockerFly.png)

## Configuration
All the configuratio can be set in [config.yml](./config.yml):
- The name of the docker network for all containers can be specified using the **network_name** variable, under the **docker** section.
- The server configuration can be specified under the **server** section (explained in [README.md](./server/README.md) of the server).
- The ui configuration can be specified under the **ui** section (explained in [README.md](./ui/README.md) of the ui).

A second [configuration file](./ui/resources/config.yml) is needed for specifying the server URL where the POST request should be sent.
  - Under the section **ui**, set the variable **server_url** with the URL of the server (Eg: ```http://{server url}/repo```)

## App Structure for deployment
The repository must have this three elements:
- **dockerfly.yaml**: configuration file for defining the parameters for the deployment of the app.
- **main.py**: main program for execution of the app.
- **requirements.txt**: libraries needed for python program to work.

### dockerfly.yaml
```yaml
app_name: "{URL for nginx reverse proxy}"

python_version: "{python version}"

requirements_file: "{name of the requirements file}"

port: 5000

network_name: "{docker network name for the containers}"

start_command:
  - "{start command}"
  - "param 1"
  - "param 2"
  - ...
```

## Running

For starting the server and the web UI, execute the [./start.sh](./start.sh) script.

You may also atert each component individually simply by executing ```make run``` in each directory.

## Troubleshooting
If error with ```yq``` install with ```apt install yq```.