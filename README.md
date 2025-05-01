# DockerFly
This project proposes the creation of a tool to automate the deployment of Python applications. The goal is for a user to specify a project, so that the system receives it, processes it, and automatically launches it inside a container, without requiring any additional technical intervention.

![Alt text](DockerFly.png)

## Configuration
All the configuratio can be set in [config.yml](./config.yml):
- The name of the docker network for all containers can be specified using the **network_name** variable, under the **docker** section.
- The server configuration can be specified under the **server** section (explained in [README.md](./server/README.md) of the server).
- The ui configuration can be specified under the **ui** section (explained in [README.md](./ui/README.md) of the ui).
