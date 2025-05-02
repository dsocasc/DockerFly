# Web UI
A web UI is available for sending the repo link to the server.

## Configuration
Under the **ui** section in [config.yml](../config.yml):
- The exposed port can be specified in the [config.yml](../config.yml) file using the **exposed_port** variable.
- The URL of the server receiving the POST request can be specified using the **server_url** variable.
- The URL (for nginx reverse proxy) where the server will respond can be specified in the [config.yml](../config.yml) file using the **url** variable.

A second [configuration file](./resources/config.yml) is needed for specifying the server URL where the POST request should be sent.
  - Under the section **ui**, set the variable **server_url** with the URL of the server (Eg: http://server.net/repo)

## Building
A [Makefile](./Makefile) is available for creating the image and running the container.

- To build the image for the container, you can use the ```make build``` command.
- To create and run the container, you can use the ```make run``` command.

## Usage
When the container is running, the webpage should be available at the URL defined in the [config.yml](../config.yml) file using the **url** variable.

