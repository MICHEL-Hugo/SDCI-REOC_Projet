# Project README

## Overview
This project describes the topology of a network by creating gateways that simulates the data received by sensor networks. Then it is monitored and create a solution to adress the problem of sudden increase in data traffic load of one of the node.
---

## Docker Images

### 1. `host`

**Function to Build the Image:**
```bash
docker build -f host_dev.Dockerfile -t host:dev .
docker build -f host_dev2.Dockerfile -t host:dev2 .
docker build -f host_gw.Dockerfile -t host:gateway .
docker build -f host_srv.Dockerfile -t host:server .
```

---

### 2. `vnf`

**Function to Build the Image:**
```bash
docker build -f vnfGateway.Dockerfile -t vnf:gateway .
```

---

## Building the Docker Images
Use the above functions to build the necessary Docker images for the project.

---

## Running the Topology
After building the Docker images, run the `topology.py` script to create and start the network topology.

### Script Overview
The `topology.py` script uses the following modules and methods to create the network:

- **Logging and Setup:**
  - Configures logging for debugging.
  - Sets Mininet log level to `info`.
- **Data Center and API Endpoints:**
  - Adds a data center and connects it to OpenStack and REST API endpoints.
- **Switches and Links:**
  - Adds and connects switches to form the network.
- **Containers:**
  - Adds Docker containers for servers, gateways, and devices with appropriate IP addresses, images, and commands.
- **Network Management:**
  - Starts the network and provides a CLI for interaction.

### Command to Run
```bash
python3 topology.py
```

Ensure that all dependencies for the script are installed and the Docker service is running before executing the command.

---

## Running the General Controller
After running the `topology.py` script, execute the `generalController.py` file to monitor and manage the network dynamically.

### Script Overview
The `generalController.py` script:
- Starts the `monitor.py` script for traffic monitoring.
- Dynamically redirects traffic between devices and VNFs based on network conditions.
- Restores original topology settings when conditions normalize.

### Command to Run
```bash
python3 generalController.py
```

Ensure the required Python dependencies are installed and the Docker containers are active.

---

