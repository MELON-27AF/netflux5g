import logging
from datetime import datetime
import subprocess
import os
import time
import json

class EnhancedContainerManager:
    """
    Enhanced Container Manager for Open5GS and UERANSIM 5G Core simulation
    Similar to how MiniEdit works with Mininet
    """
    
    def __init__(self):
        try:
            logging.info("Initializing Enhanced ContainerManager...")
            try:
                import docker
                self.client = docker.from_env()
                logging.info("Docker client connected successfully")
            except ImportError:
                logging.error("Docker package not installed. Please install: pip install docker")
                self.client = None
            except Exception as e:
                logging.error(f"Error connecting to Docker: {e}")
                self.client = None
        except Exception as e:
            logging.error(f"Error initializing ContainerManager: {e}")
            self.client = None
        
        self.deployed_containers = []
        self.network_name = "netflux5g_network"
        self.open5gs_containers = {}
        self.ueransim_containers = {}
        self.terminal_processes = {}
        
        # 5G Core component configurations
        self.open5gs_config = {
            "mongodb": {
                "image": "mongo:4.4",
                "ports": {"27017": "27017"},
                "environment": {},
                "volumes": {}
            },
            "nrf": {
                "image": "openverso/open5gs:latest",
                "command": ["open5gs-nrfd", "-c", "/etc/open5gs/nrf.yaml"],
                "ports": {"7777": "7777"},
                "depends_on": ["mongodb"],
                "volumes": {}
            },
            "amf": {
                "image": "openverso/open5gs:latest",
                "command": ["open5gs-amfd", "-c", "/etc/open5gs/amf.yaml"],
                "ports": {"38412": "38412"},
                "depends_on": ["nrf"],
                "volumes": {}
            },
            "smf": {
                "image": "openverso/open5gs:latest",
                "command": ["open5gs-smfd", "-c", "/etc/open5gs/smf.yaml"],
                "depends_on": ["nrf"],
                "volumes": {}
            },
            "upf": {
                "image": "openverso/open5gs:latest",
                "command": ["open5gs-upfd", "-c", "/etc/open5gs/upf.yaml"],
                "ports": {"8805": "8805"},
                "cap_add": ["NET_ADMIN"],
                "depends_on": ["smf"],
                "volumes": {}
            },
            "ausf": {
                "image": "openverso/open5gs:latest",
                "command": ["open5gs-ausfd", "-c", "/etc/open5gs/ausf.yaml"],
                "depends_on": ["nrf"],
                "volumes": {}
            },
            "udm": {
                "image": "openverso/open5gs:latest",
                "command": ["open5gs-udmd", "-c", "/etc/open5gs/udm.yaml"],
                "depends_on": ["nrf"],
                "volumes": {}
            },
            "pcf": {
                "image": "openverso/open5gs:latest",
                "command": ["open5gs-pcfd", "-c", "/etc/open5gs/pcf.yaml"],
                "depends_on": ["nrf"],
                "volumes": {}
            }
        }
        
        self.ueransim_config = {
            "gnb": {
                "image": "openverso/ueransim:latest",
                "command": ["nr-gnb", "-c", "/etc/ueransim/gnb.yaml"],
                "cap_add": ["NET_ADMIN"],
                "privileged": True,
                "volumes": {}
            },
            "ue": {
                "image": "openverso/ueransim:latest",
                "command": ["nr-ue", "-c", "/etc/ueransim/ue.yaml"],
                "cap_add": ["NET_ADMIN"],
                "privileged": True,
                "volumes": {}
            }
        }
        
    def create_5g_network(self):
        """Create a Docker network for 5G components"""
        if not self.client:
            return None
            
        try:
            # Remove existing network if it exists
            try:
                import docker
                existing_network = self.client.networks.get(self.network_name)
                existing_network.remove()
                print(f"Removed existing network: {self.network_name}")
            except docker.errors.NotFound:
                pass
            
            # Create new network with specific subnet for 5G components
            import docker
            network = self.client.networks.create(
                self.network_name,
                driver="bridge",
                ipam=docker.types.IPAMConfig(
                    pool_configs=[docker.types.IPAMPool(subnet="10.45.0.0/16")]
                ),
                options={
                    "com.docker.network.bridge.enable_ip_masquerade": "true"
                }
            )
            print(f"Created network: {self.network_name}")
            return network
        except Exception as e:
            print(f"Error creating network: {e}")
            return None
    
    def deploy_5g_core(self, components):
        """Deploy 5G core components as Docker containers using Open5GS and UERANSIM"""
        if not self.client:
            print("Docker client not available. Please ensure Docker is installed and running.")
            return False, "Docker not available"
        
        # Create network first
        network = self.create_5g_network()
        if not network:
            return False, "Failed to create network"
        
        deployed = []
        
        # Sort components by deployment order (mongodb, nrf, then others)
        deployment_order = ['mongodb', 'nrf', 'amf', 'smf', 'upf', 'ausf', 'udm', 'pcf', 'gnb', 'ue']
        sorted_components = sorted(components, key=lambda c: 
                                 deployment_order.index(c.component_type) 
                                 if c.component_type in deployment_order else 999)
        
        for component in sorted_components:
            container = None
            comp_type = component.component_type
            
            if comp_type in ['amf', 'smf', 'upf', 'pcf', 'udm', 'ausf', 'nrf']:
                container = self.deploy_open5gs_component(component)
            elif comp_type == 'gnb':
                container = self.deploy_gnb_component(component)
            elif comp_type == 'ue':
                container = self.deploy_ue_component(component)
                
            if container:
                deployed.append(container)
                # Store container reference for terminal access
                self.deployed_containers.append(container)
                
                if comp_type in self.open5gs_config:
                    self.open5gs_containers[comp_type] = container
                elif comp_type in ['gnb', 'ue']:
                    self.ueransim_containers[comp_type] = container
        
        return True, f"Deployed {len(deployed)} containers"
    
    def deploy_open5gs_component(self, component):
        """Deploy Open5GS component"""
        try:
            comp_type = component.component_type
            properties = getattr(component, 'properties', {})
            comp_id = getattr(component, 'component_id', id(component))
            
            # Debug logging
            print(f"DEBUG: Deploying {comp_type}, properties type: {type(properties)}, value: {properties}")
            
            # Ensure properties is a dictionary
            if not isinstance(properties, dict):
                print(f"WARNING: Properties was {type(properties)}, converting to dict")
                properties = {}
                
            name = properties.get("name", f"{comp_type}_{comp_id}")
            
            if comp_type not in self.open5gs_config:
                print(f"Unknown Open5GS component type: {comp_type}")
                return None
            
            config = self.open5gs_config[comp_type]
            
            # Ensure config is a dictionary (defensive programming)
            if not isinstance(config, dict):
                print(f"Config for {comp_type} is not a dictionary: {type(config)}")
                config = {"image": "openverso/open5gs:latest"}
            
            # Create configuration files if needed
            self.create_open5gs_config(comp_type, name, properties)
            
            # Deploy container
            # Prepare volumes correctly for Docker
            volumes_config = config.get("volumes", {})
            volumes_list = []
            if volumes_config:
                for host_path, container_path in volumes_config.items():
                    volumes_list.append(f"{host_path}:{container_path}")
            
            # Prepare ports correctly for Docker
            ports_config = config.get("ports", {})
            ports_dict = {}
            if ports_config:
                for container_port, host_port in ports_config.items():
                    if host_port:
                        ports_dict[f"{container_port}"] = host_port
            
            container = self.client.containers.run(
                config.get("image", "openverso/open5gs:latest"),
                command=config.get("command", "sleep infinity"),
                name=name,
                network=self.network_name,
                detach=True,
                remove=False,
                cap_add=config.get("cap_add", []),
                privileged=config.get("privileged", False),
                environment={
                    'COMPONENT_TYPE': comp_type,
                    'COMPONENT_NAME': name,
                    **config.get("environment", {})
                },
                ports=ports_dict if ports_dict else None,
                volumes=volumes_list if volumes_list else None
            )
            
            print(f"Deployed Open5GS {comp_type}: {name}")
            return container
            
        except Exception as e:
            print(f"Error deploying Open5GS {comp_type}: {e}")
            return None
    
    def deploy_gnb_component(self, component):
        """Deploy UERANSIM gNB component"""
        try:
            properties = getattr(component, 'properties', {})
            comp_id = getattr(component, 'component_id', id(component))
            
            # Debug logging
            print(f"DEBUG: Deploying gNB, properties type: {type(properties)}, value: {properties}")
            
            # Ensure properties is a dictionary
            if not isinstance(properties, dict):
                print(f"WARNING: gNB properties was {type(properties)}, converting to dict")
                properties = {}
                
            name = properties.get("name", f"gnb_{comp_id}")
            
            # Create gNB configuration
            self.create_gnb_config(name, properties)
            
            config = self.ueransim_config["gnb"]
            
            # Ensure config is a dictionary (defensive programming)
            if not isinstance(config, dict):
                print(f"gNB config is not a dictionary: {type(config)}")
                config = {"image": "openverso/ueransim:latest"}
            
            # Prepare volumes correctly for Docker
            volumes_config = config.get("volumes", {})
            volumes_list = []
            if volumes_config:
                for host_path, container_path in volumes_config.items():
                    volumes_list.append(f"{host_path}:{container_path}")
            
            container = self.client.containers.run(
                config.get("image", "openverso/ueransim:latest"),
                command=config.get("command", "sleep infinity"),
                name=name,
                network=self.network_name,
                detach=True,
                remove=False,
                cap_add=config.get("cap_add", []),
                privileged=config.get("privileged", False),
                environment={
                    'COMPONENT_TYPE': 'gnb',
                    'COMPONENT_NAME': name,
                    'TAC': str(properties.get('tac', 1)),
                    'POWER': str(properties.get('power', 20))
                },
                volumes=volumes_list if volumes_list else None
            )
            
            print(f"Deployed UERANSIM gNB: {name}")
            return container
            
        except Exception as e:
            print(f"Error deploying gNB: {e}")
            return None
    
    def deploy_ue_component(self, component):
        """Deploy UERANSIM UE component"""
        try:
            properties = getattr(component, 'properties', {})
            comp_id = getattr(component, 'component_id', id(component))
            
            # Debug logging
            print(f"DEBUG: Deploying UE, properties type: {type(properties)}, value: {properties}")
            
            # Ensure properties is a dictionary
            if not isinstance(properties, dict):
                print(f"WARNING: UE properties was {type(properties)}, converting to dict")
                properties = {}
                
            name = properties.get("name", f"ue_{comp_id}")
            
            # Create UE configuration
            self.create_ue_config(name, properties)
            
            config = self.ueransim_config["ue"]
            
            # Ensure config is a dictionary (defensive programming)
            if not isinstance(config, dict):
                print(f"UE config is not a dictionary: {type(config)}")
                config = {"image": "openverso/ueransim:latest"}
            
            # Prepare volumes correctly for Docker
            volumes_config = config.get("volumes", {})
            volumes_list = []
            if volumes_config:
                for host_path, container_path in volumes_config.items():
                    volumes_list.append(f"{host_path}:{container_path}")
            
            container = self.client.containers.run(
                config.get("image", "openverso/ueransim:latest"),
                command=config.get("command", "sleep infinity"), 
                name=name,
                network=self.network_name,
                detach=True,
                remove=False,
                cap_add=config.get("cap_add", []),
                privileged=config.get("privileged", False),
                environment={
                    'COMPONENT_TYPE': 'ue',
                    'COMPONENT_NAME': name,
                    'IMSI': properties.get('imsi', '001010000000001')
                },
                volumes=volumes_list if volumes_list else None
            )
            
            print(f"Deployed UERANSIM UE: {name}")
            return container
            
        except Exception as e:
            print(f"Error deploying UE: {e}")
            return None
    
    def create_open5gs_config(self, comp_type, name, properties=None):
        """Create Open5GS configuration files"""
        try:
            import os
            
            config_dir = f"./config/open5gs/{name}"
            os.makedirs(config_dir, exist_ok=True)
            
            # Base configuration templates
            if comp_type == "nrf":
                config_content = f"""
db_uri: mongodb://mongodb:27017/open5gs

logger:
    level: info

nrf:
    sbi:
        addr: 0.0.0.0
        port: 7777
"""
            elif comp_type == "amf":
                config_content = f"""
db_uri: mongodb://mongodb:27017/open5gs

logger:
    level: info

amf:
    sbi:
        addr: 0.0.0.0
        port: 80
    ngap:
        addr: 0.0.0.0
        port: 38412
    guami:
        - plmn_id:
            mcc: 999
            mnc: 70
          amf_id:
            region: 2
            set: 1
    tai:
        - plmn_id:
            mcc: 999
            mnc: 70
          tac: 1
    plmn_support:
        - plmn_id:
            mcc: 999
            mnc: 70
          s_nssai:
            - sst: 1

nrf:
    sbi:
        addr: nrf
        port: 7777
"""
            # Add more configurations for other components...
            else:
                config_content = f"# Configuration for {comp_type}"
            
            config_file = os.path.join(config_dir, f"{comp_type}.yaml")
            with open(config_file, 'w') as f:
                f.write(config_content)
                
            print(f"Created config file: {config_file}")
            return config_file
            
        except Exception as e:
            print(f"Error creating config for {comp_type}: {e}")
            return None
    
    def create_gnb_config(self, name, properties=None):
        """Create UERANSIM gNB configuration"""
        try:
            import os
            
            config_dir = f"./config/ueransim/{name}"
            os.makedirs(config_dir, exist_ok=True)
            
            mcc = properties.get("mcc", "999") if properties else "999"
            mnc = properties.get("mnc", "70") if properties else "70"
            nci = properties.get("nci", "0x000000010") if properties else "0x000000010"
            
            config_content = f"""
mcc: '{mcc}'
mnc: '{mnc}'
nci: {nci}
idLength: 32
tac: 1
linkIp: 127.0.0.1
ngapIp: 127.0.0.1
gtpIp: 127.0.0.1

amfConfigs:
  - address: amf
    port: 38412

slices:
  - sst: 1

logger:
  level: warn
"""
            
            config_file = os.path.join(config_dir, "gnb.yaml")
            with open(config_file, 'w') as f:
                f.write(config_content)
                
            print(f"Created gNB config: {config_file}")
            return config_file
            
        except Exception as e:
            print(f"Error creating gNB config: {e}")
            return None
    
    def create_ue_config(self, name, properties=None):
        """Create UERANSIM UE configuration"""
        try:
            import os
            
            config_dir = f"./config/ueransim/{name}"
            os.makedirs(config_dir, exist_ok=True)
            
            imsi = properties.get("imsi", "001010000000001") if properties else "001010000000001"
            key = properties.get("key", "465B5CE8B199B49FAA5F0A2EE238A6BC") if properties else "465B5CE8B199B49FAA5F0A2EE238A6BC"
            
            config_content = f"""
# IMSI number of the UE. IMSI = [MCC|MNC|MSISDN] (In total 15 digits)
supi: 'imsi-{imsi}'
mcc: '999'
mnc: '70'
routingIndicator: '0000'

# Permanent subscription key
key: '{key}'
# Operator code (OP or OPC) of the UE
op: 'E8ED289DEBA952E4283B54E88E6183CA'
# This value specifies the OP type and it can be either 'OP' or 'OPC'
opType: 'OPC'

# Authentication Management Field (AMF) value
amf: '8000'
# IMEI number of the device. It is used if no SUPI is provided
imei: '356938035643803'
# IMEISV number of the device. It is used if no SUPI and IMEI is provided
imeiSv: '4370816125816151'

# List of gNB IP addresses for Radio Link Simulation
gnbSearchList:
  - 127.0.0.1

# UAC Access Identities Configuration
uacAic:
  mps: false
  mcs: false

# UAC Access Control Class
uacAcc:
  normalClass: 0
  class11: false
  class12: false
  class13: false
  class14: false
  class15: false

# Initial PDU sessions to be established
sessions:
  - type: 'IPv4'
    apn: 'internet'
    slice:
      sst: 1

# Configured NSSAI for this UE by HPLMN
configured-nssai:
  - sst: 1

# Default Configured NSSAI for this UE
default-nssai:
  - sst: 1
    sd: 1

# Supported integrity algorithms by this UE
integrity:
  IA1: true
  IA2: true
  IA3: true

# Supported encryption algorithms by this UE
ciphering:
  EA1: true
  EA2: true
  EA3: true

# Integrity protection maximum data rate for user plane
integrityMaxRate:
  uplink: 'full'
  downlink: 'full'

logger:
  level: warn
"""
            
            config_file = os.path.join(config_dir, "ue.yaml")
            with open(config_file, 'w') as f:
                f.write(config_content)
                
            print(f"Created UE config: {config_file}")
            return config_file
            
        except Exception as e:
            print(f"Error creating UE config: {e}")
            return None
    
    def open_container_terminal(self, container_name):
        """Open terminal to specific container - like MiniEdit's terminal access"""
        try:
            if os.name == 'nt':  # Windows
                # Use Windows Terminal or PowerShell
                cmd = f'docker exec -it {container_name} /bin/bash'
                subprocess.Popen(['wt', 'powershell', '-Command', cmd], shell=True)
            else:  # Linux/Mac
                # Use xterm or gnome-terminal
                cmd = f'docker exec -it {container_name} /bin/bash'
                subprocess.Popen(['gnome-terminal', '--', 'bash', '-c', cmd])
                
            print(f"Opened terminal for container: {container_name}")
            
        except Exception as e:
            print(f"Error opening terminal for {container_name}: {e}")
    
    def get_container_status(self):
        """Get status of all deployed containers"""
        status_list = []
        
        for container in self.deployed_containers:
            try:
                container.reload()  # Refresh container info
                status_list.append({
                    "name": container.name,
                    "id": container.short_id,
                    "status": container.status,
                    "ip": self.get_container_ip(container),
                    "image": container.image.tags[0] if container.image.tags else "unknown"
                })
            except Exception as e:
                status_list.append({
                    "name": getattr(container, 'name', 'unknown'),
                    "id": getattr(container, 'short_id', 'unknown'),
                    "status": f"error: {e}",
                    "ip": "unknown",
                    "image": "unknown"
                })
        
        return status_list
    
    def get_container_ip(self, container):
        """Get IP address of a container in the 5G network"""
        try:
            networks = container.attrs['NetworkSettings']['Networks']
            if self.network_name in networks:
                return networks[self.network_name]['IPAddress']
            return "unknown"
        except:
            return "unknown"
    
    def test_connectivity(self):
        """Test connectivity between containers"""
        results = []
        
        for container in self.deployed_containers:
            try:
                # Test ping to other containers
                for target_container in self.deployed_containers:
                    if container != target_container:
                        target_ip = self.get_container_ip(target_container)
                        if target_ip != "unknown":
                            exec_result = container.exec_run(f"ping -c 1 {target_ip}", timeout=5)
                            success = exec_result.exit_code == 0
                            
                            results.append({
                                "source": container.name,
                                "source_ip": self.get_container_ip(container),
                                "target": target_container.name,
                                "target_ip": target_ip,
                                "success": success,
                                "error": None if success else f"Ping failed (exit code: {exec_result.exit_code})"
                            })
            except Exception as e:
                results.append({
                    "source": container.name,
                    "source_ip": self.get_container_ip(container),
                    "target": "unknown",
                    "target_ip": "unknown",
                    "success": False,
                    "error": str(e)
                })
        
        return results
    
    def cleanup(self):
        """Clean up deployed containers and network"""
        try:
            # Stop and remove containers
            for container in self.deployed_containers:
                try:
                    container.stop(timeout=10)
                    container.remove()
                    print(f"Cleaned up container: {container.name}")
                except Exception as e:
                    print(f"Error cleaning up container {container.name}: {e}")
            
            # Remove network
            try:
                import docker
                network = self.client.networks.get(self.network_name)
                network.remove()
                print(f"Removed network: {self.network_name}")
            except docker.errors.NotFound:
                pass
            except Exception as e:
                print(f"Error removing network: {e}")
                
            self.deployed_containers = []
            self.open5gs_containers = {}
            self.ueransim_containers = {}
            
        except Exception as e:
            print(f"Error during cleanup: {e}")
    
    def get_all_containers(self):
        """Get all deployed containers as name, container pairs"""
        containers = []
        
        # Add Open5GS containers
        for name, container in self.open5gs_containers.items():
            containers.append((name, container))
            
        # Add UERANSIM containers  
        for name, container in self.ueransim_containers.items():
            containers.append((name, container))
            
        # Add any other deployed containers
        for container in self.deployed_containers:
            if container not in [c for _, c in containers]:
                containers.append((container.name, container))
                
        return containers
    
    def open_terminal(self, container_name):
        """Open terminal for container - compatibility method"""
        return self.open_container_terminal(container_name)

    def execute_command_in_container(self, container_name, command):
        """Execute command in container and return success, output"""
        try:
            # Find container by name
            container = None
            for name, cont in self.get_all_containers():
                if name == container_name or cont.name == container_name:
                    container = cont
                    break
            
            if not container:
                return False, f"Container {container_name} not found"
            
            # Execute command
            exec_result = container.exec_run(command, stdout=True, stderr=True)
            output = exec_result.output.decode('utf-8')
            success = exec_result.exit_code == 0
            
            return success, output
            
        except Exception as e:
            print(f"Error executing command in container {container_name}: {e}")
            return False, f"Error executing command: {e}"
