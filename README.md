# Software Defined Network & Virtual Network Function: Monitoring and Adaptation

## Overview  
This project outlines the topology of a basic IoT network by simulating devices that act as sensors, sending data to gateways. The gateways then transit the data to an application server.  

The primary aim of this project is to explore **Software-Defined Networking (SDN)** and **Virtual Network Functions (VNF)** by implementing two main functionalities:  

1. **Overload Detection**  
   - Monitors traffic to identify and respond to congestion on network nodes.  

2. **Regulation Mechanism**  
   - Implements a dynamic solution to redistribute traffic when overloads are detected.  

Follow the steps below to set up the network topology and implement the specified functionalities:  

---

## Docker Images
Docker images are stored in the [dockers](https://github.com/MICHEL-Hugo/SDCI-REOC_Projet/tree/main/dockers) file.
Use the following functions to build the necessary Docker images for the project.

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

## Running the Topology
After building the Docker images, run the `topology.py` script in the [topologies](https://github.com/MICHEL-Hugo/SDCI-REOC_Projet/tree/main/topologies) folder to create and start the network topology.

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
### Network Evolution Overview  
This project allows you to observe the evolution of the network.  

- **Device 1 in the topology** runs a unique service that alternates between two phases:  
  1. **High data sending**  
  2. **Regular data sending**  

You can modify the duration of these phases in the [topology.py](https://github.com/MICHEL-Hugo/SDCI-REOC_Projet/blob/main/topologies/topology.py) file.  

### Observing the Topology  
You can monitor the topology using the following commands:  

#### Containernet Commands  
- **Display nodes and links**:  
  ```bash
  nodes
  links
  ```  

#### Ryu Controller Commands  
- **List switches**:  
  ```bash
  curl -X GET http://localhost:8080/stats/switches
  ```  
- **Flow statistics for switch 1**:  
  ```bash
  curl -X GET http://localhost:8080/stats/flow/1
  ```  
- **Switch description for switch 1**:  
  ```bash
  curl -X GET http://localhost:8080/stats/desc/1
  ```  

