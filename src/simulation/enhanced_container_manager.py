import logging
from datetime import datetime
import subprocess
import os
import time
import json
import sys

# Add the src directory to the path to import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.config_manager import ConfigManager

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
        
        # Initialize configuration manager
        self.config_manager = ConfigManager()
        
        # 5G Core component configurations
        self.open5gs_config = {
            "mongodb": {
                "image": "mongo:4.4",
                "ports": {},  # Remove port mapping - MongoDB only needs internal access
                "environment": {},
                "volumes": {},
                "mem_limit": "256m",
                "memswap_limit": "256m"
            },
            "nrf": {
                "image": "openverso/open5gs:latest",
                "command": ["open5gs-nrfd", "-c", "/etc/open5gs/nrf.yaml"],
                "ports": {},  # Remove port mapping - NRF communicates internally
                "depends_on": ["mongodb"],
                "volumes": {},
                "mem_limit": "128m",
                "memswap_limit": "128m"
            },
            "amf": {
                "image": "openverso/open5gs:latest",
                "command": ["open5gs-amfd", "-c", "/etc/open5gs/amf.yaml"],
                "ports": {"38412": "38412"},
                "depends_on": ["nrf"],
                "volumes": {},
                "mem_limit": "128m",
                "memswap_limit": "128m"
            },
            "smf": {
                "image": "openverso/open5gs:latest",
                "command": ["open5gs-smfd", "-c", "/etc/open5gs/smf.yaml"],
                "depends_on": ["nrf"],
                "volumes": {},
                "mem_limit": "128m",
                "memswap_limit": "128m"
            },
            "upf": {
                "image": "openverso/open5gs:latest",
                "command": ["open5gs-upfd", "-c", "/etc/open5gs/upf.yaml"],
                "ports": {"8805": "8805"},
                "cap_add": ["NET_ADMIN"],
                "depends_on": ["smf"],
                "volumes": {},
                "mem_limit": "256m",
                "memswap_limit": "256m"
            },
            "ausf": {
                "image": "openverso/open5gs:latest",
                "command": ["open5gs-ausfd", "-c", "/etc/open5gs/ausf.yaml"],
                "depends_on": ["nrf"],
                "volumes": {},
                "mem_limit": "128m",
                "memswap_limit": "128m"
            },
            "udm": {
                "image": "openverso/open5gs:latest",
                "command": ["open5gs-udmd", "-c", "/etc/open5gs/udm.yaml"],
                "depends_on": ["nrf"],
                "volumes": {},
                "mem_limit": "128m",
                "memswap_limit": "128m"
            },
            "pcf": {
                "image": "openverso/open5gs:latest",
                "command": ["open5gs-pcfd", "-c", "/etc/open5gs/pcf.yaml"],
                "depends_on": ["nrf"],
                "volumes": {},
                "mem_limit": "128m",
                "memswap_limit": "128m"
            }
        }
        
        self.ueransim_config = {
            "gnb": {
                "image": "towards5gs/ueransim-gnb:v3.2.3",
                "command": ["/ueransim/build/nr-gnb", "-c", "/etc/ueransim/gnb.yaml"],
                "cap_add": ["NET_ADMIN"],
                "privileged": True,
                "volumes": {},
                "mem_limit": "256m",
                "memswap_limit": "256m"
            },
            "ue": {
                "image": "towards5gs/ueransim-ue:v3.2.3",
                "command": ["/ueransim/build/nr-ue", "-c", "/etc/ueransim/ue.yaml"],
                "cap_add": ["NET_ADMIN"],
                "privileged": True,
                "volumes": {},
                "mem_limit": "128m",
                "memswap_limit": "128m"
            }
        }
        
        # Network infrastructure components
        self.network_config = {
            "router": {
                "image": "alpine:latest",
                "command": ["sh", "-c", "apk add --no-cache iptables && sleep infinity"],
                "cap_add": ["NET_ADMIN"],
                "privileged": True,
                "volumes": {},
                "mem_limit": "64m",
                "memswap_limit": "64m"
            }
        }
        
    def cleanup_existing_containers(self):
        """Clean up any existing containers with our naming pattern"""
        try:
            # Get all containers (including stopped ones)
            all_containers = self.client.containers.list(all=True)
            
            # Names to look for
            container_patterns = [
                'nrf-test', 'amf-test', 'smf-test', 'upf-test', 
                'ausf-test', 'udm-test', 'pcf-test', 'gnb-test', 
                'ue-test', 'internet-gw', 'router'
            ]
            
            for container in all_containers:
                container_name = container.name
                if any(pattern in container_name for pattern in container_patterns):
                    try:
                        logging.info(f"Cleaning up existing container: {container_name}")
                        if container.status == 'running':
                            container.stop(timeout=5)
                        container.remove()
                        print(f"✅ Removed existing container: {container_name}")
                    except Exception as e:
                        logging.warning(f"Could not remove container {container_name}: {e}")
                        
        except Exception as e:
            logging.error(f"Error during cleanup of existing containers: {e}")
        
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

        print("Checking Docker connection...")
        try:
            # Test Docker connection
            self.client.ping()
            print("✅ Docker is running and accessible")
            
            # Clean up any existing containers first
            self.cleanup_existing_containers()
            
        except Exception as e:
            print(f"❌ Docker connection failed: {e}")
            return False, f"Docker connection failed: {e}"

        # Pre-pull required images with better error handling
        print("Preparing Docker images...")
        try:
            if not self.pull_required_images():
                print("⚠️ Image pulling was interrupted")
                return False, "Image pulling was interrupted by user"
        except Exception as e:
            print(f"⚠️ Error during image pulling: {e}")
            print("Continuing with deployment - Docker will attempt to pull images as needed...")

        # Create network first
        network = self.create_5g_network()
        if not network:
            return False, "Failed to create network"

        deployed = []

        # Ensure MongoDB is deployed first (required by Open5GS components)
        mongodb_deployed = False
        for component in components:
            if component.component_type == 'mongodb':
                mongodb_deployed = True
                break
        
        if not mongodb_deployed:
            # Create a virtual MongoDB component if not found
            print("📦 MongoDB not found in components, deploying it automatically...")
            mongodb_container = self.deploy_mongodb_standalone()
            if mongodb_container:
                deployed.append(mongodb_container)
                self.deployed_containers.append(mongodb_container)

        # Sort components by deployment order (mongodb, nrf, then others)
        deployment_order = ['mongodb', 'nrf', 'amf', 'smf', 'upf', 'ausf', 'udm', 'pcf', 'gnb', 'ue']
        sorted_components = sorted(components, key=lambda c: 
                                 deployment_order.index(c.component_type) 
                                 if c.component_type in deployment_order else 999)
        
        for component in sorted_components:
            # Check memory before deploying each component
            try:
                import psutil
                available_memory = psutil.virtual_memory().available / (1024**3)
                print(f"Available memory before deploying {component.component_type}: {available_memory:.1f}GB")
                
                if available_memory < 1.0:  # Less than 1GB available
                    print(f"⚠️ Low memory warning: {available_memory:.1f}GB available")
                    print("Stopping deployment to prevent system instability")
                    return False, f"Insufficient memory to continue deployment. Available: {available_memory:.1f}GB"
            except ImportError:
                pass  # psutil not available, continue anyway
            
            container = None
            comp_type = component.component_type
            
            print(f"Deploying {comp_type}: {getattr(component, 'properties', {}).get('name', 'unnamed')}")
            
            if comp_type == 'mongodb':
                container = self.deploy_mongodb_component(component)
            elif comp_type in ['amf', 'smf', 'upf', 'pcf', 'udm', 'ausf', 'nrf']:
                container = self.deploy_open5gs_component(component)
            elif comp_type == 'gnb':
                container = self.deploy_gnb_component(component)
            elif comp_type == 'ue':
                container = self.deploy_ue_component(component)
            elif comp_type == 'router':
                container = self.deploy_router_component(component)
                
            if container:
                deployed.append(container)
                # Store container reference for terminal access
                self.deployed_containers.append(container)
                
                if comp_type in self.open5gs_config:
                    self.open5gs_containers[comp_type] = container
                elif comp_type in ['gnb', 'ue']:
                    self.ueransim_containers[comp_type] = container
                
                # Wait for container to stabilize before deploying next
                import time
                time.sleep(3)
                print(f"✅ {comp_type} deployed and stabilizing...")
            
            else:
                print(f"❌ Failed to deploy {comp_type}")
                # Continue with other components even if one fails
        
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
            
            # Store a copy of properties to prevent accidental overwriting
            props_copy = dict(properties)
                
            name = props_copy.get("name", f"{comp_type}_{comp_id}")
            
            if comp_type not in self.open5gs_config:
                print(f"Unknown Open5GS component type: {comp_type}")
                return None
            
            config = self.open5gs_config[comp_type]
            
            # Ensure config is a dictionary (defensive programming)
            if not isinstance(config, dict):
                print(f"Config for {comp_type} is not a dictionary: {type(config)}")
                config = {"image": "openverso/open5gs:latest"}
            
            # Create configuration files if needed
            self.create_open5gs_config(comp_type, name, props_copy)
            
            # Deploy container
            # Prepare volumes correctly for Docker
            volumes_config = config.get("volumes", {})
            volumes_list = []
            
            # Add configuration file volume mount using ConfigManager
            config_dir = self.config_manager.get_instance_config_dir(name)
            volumes_list.append(f"{config_dir}:/etc/open5gs:ro")
            
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
            
            # Create proper startup command with dependencies
            if comp_type == "nrf":
                # NRF only needs to wait for MongoDB
                startup_command = [
                    "sh", "-c", 
                    f"echo 'Waiting for MongoDB...' && "
                    f"while ! nc -z mongodb 27017; do sleep 2; done && "
                    f"echo 'MongoDB is ready, starting NRF...' && "
                    f"exec {' '.join(config.get('command', ['open5gs-nrfd']))}"
                ]
            else:
                # Other Open5GS services need to wait for both MongoDB and NRF
                startup_command = [
                    "sh", "-c", 
                    f"echo 'Waiting for MongoDB...' && "
                    f"while ! nc -z mongodb 27017; do sleep 2; done && "
                    f"echo 'Waiting for NRF...' && "
                    f"while ! nc -z nrf 7777; do sleep 2; done && "
                    f"echo 'Dependencies ready, starting {comp_type}...' && "
                    f"exec {' '.join(config.get('command', [f'open5gs-{comp_type}d']))}"
                ]
            
            container = self.client.containers.run(
                config.get("image", "openverso/open5gs:latest"),
                command=startup_command,
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
                volumes=volumes_list if volumes_list else None,
                restart_policy={"Name": "no"},
                mem_limit=config.get("mem_limit", "256m"),
                memswap_limit=config.get("memswap_limit", "256m")
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
            
            # Store a copy of properties to prevent accidental overwriting
            props_copy = dict(properties)
                
            name = props_copy.get("name", f"gnb_{comp_id}")
            
            # Create gNB configuration
            self.create_gnb_config(name, props_copy)
            
            config = self.ueransim_config["gnb"]
            
            # Ensure config is a dictionary (defensive programming)
            if not isinstance(config, dict):
                print(f"gNB config is not a dictionary: {type(config)}")
                config = {"image": "towards5gs/ueransim-gnb:v3.2.3"}
            
            # Prepare volumes correctly for Docker
            volumes_config = config.get("volumes", {})
            volumes_list = []
            
            # Add configuration file volume mount using ConfigManager
            config_dir = self.config_manager.get_instance_config_dir(name)
            volumes_list.append(f"{config_dir}:/etc/ueransim:ro")
            
            if volumes_config:
                for host_path, container_path in volumes_config.items():
                    volumes_list.append(f"{host_path}:{container_path}")
            
            container = self.client.containers.run(
                config.get("image", "towards5gs/ueransim-gnb:v3.2.3"),
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
                    'TAC': str(props_copy.get('tac', 1)),
                    'POWER': str(props_copy.get('power', 20))
                },
                volumes=volumes_list if volumes_list else None,
                restart_policy={"Name": "no"},
                mem_limit=config.get("mem_limit", "256m"),
                memswap_limit=config.get("memswap_limit", "256m")
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
            
            # Store a copy of properties to prevent accidental overwriting
            props_copy = dict(properties)
                
            name = props_copy.get("name", f"ue_{comp_id}")
            
            # Create UE configuration
            self.create_ue_config(name, props_copy)
            
            config = self.ueransim_config["ue"]
            
            # Ensure config is a dictionary (defensive programming)
            if not isinstance(config, dict):
                print(f"UE config is not a dictionary: {type(config)}")
                config = {"image": "towards5gs/ueransim-ue:v3.2.3"}
            
            # Prepare volumes correctly for Docker
            volumes_config = config.get("volumes", {})
            volumes_list = []
            
            # Add configuration file volume mount using ConfigManager
            config_dir = self.config_manager.get_instance_config_dir(name)
            volumes_list.append(f"{config_dir}:/etc/ueransim:ro")
            
            if volumes_config:
                for host_path, container_path in volumes_config.items():
                    volumes_list.append(f"{host_path}:{container_path}")
            
            container = self.client.containers.run(
                config.get("image", "towards5gs/ueransim-ue:v3.2.3"),
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
                    'IMSI': props_copy.get('imsi', '001010000000001')
                },
                volumes=volumes_list if volumes_list else None,
                restart_policy={"Name": "no"},
                mem_limit=config.get("mem_limit", "128m"),
                memswap_limit=config.get("memswap_limit", "128m")
            )
            
            print(f"Deployed UERANSIM UE: {name}")
            return container
            
        except Exception as e:
            print(f"Error deploying UE: {e}")
            return None
    
    def deploy_router_component(self, component):
        """Deploy router component using Alpine Linux with networking tools"""
        try:
            properties = getattr(component, 'properties', {})
            comp_id = getattr(component, 'component_id', id(component))
            
            # Ensure properties is a dictionary
            if not isinstance(properties, dict):
                properties = {}
            
            name = properties.get("name", f"router_{comp_id}")
            
            config = self.network_config["router"]
            
            container = self.client.containers.run(
                config.get("image", "alpine:latest"),
                command=config.get("command"),
                name=name,
                network=self.network_name,
                detach=True,
                remove=False,
                cap_add=config.get("cap_add", []),
                privileged=config.get("privileged", False),
                environment={
                    'COMPONENT_TYPE': 'router',
                    'COMPONENT_NAME': name,
                },
                mem_limit=config.get("mem_limit", "64m"),
                memswap_limit=config.get("memswap_limit", "64m")
            )
            
            print(f"Deployed router: {name}")
            return container
            
        except Exception as e:
            print(f"Error deploying router: {e}")
            return None
    
    def deploy_mongodb_component(self, component):
        """Deploy MongoDB component for Open5GS"""
        try:
            properties = getattr(component, 'properties', {})
            comp_id = getattr(component, 'component_id', id(component))
            
            # Debug logging
            print(f"DEBUG: Deploying mongodb, properties type: {type(properties)}, value: {properties}")
            
            # Ensure properties is a dictionary
            if not isinstance(properties, dict):
                print(f"WARNING: MongoDB properties was {type(properties)}, converting to dict")
                properties = {}
            
            # Store a copy of properties to prevent accidental overwriting
            props_copy = dict(properties)
                
            name = props_copy.get("name", f"mongodb_{comp_id}")
            
            config = self.open5gs_config["mongodb"]
            
            # Ensure config is a dictionary (defensive programming)
            if not isinstance(config, dict):
                print(f"MongoDB config is not a dictionary: {type(config)}")
                config = {"image": "mongo:4.4"}
            
            # Prepare ports correctly for Docker
            ports_config = config.get("ports", {})
            ports_dict = {}
            if ports_config:
                for container_port, host_port in ports_config.items():
                    if host_port:
                        ports_dict[f"{container_port}"] = host_port
            
            container = self.client.containers.run(
                config.get("image", "mongo:4.4"),
                command=config.get("command", None),
                name=name,
                network=self.network_name,
                detach=True,
                remove=False,
                environment=config.get("environment", {}),
                ports=ports_dict if ports_dict else None,
                restart_policy={"Name": "no"},
                mem_limit=config.get("mem_limit", "256m"),
                memswap_limit=config.get("memswap_limit", "256m")
            )
            
            print(f"Deployed MongoDB: {name}")
            return container
            
        except Exception as e:
            print(f"Error deploying MongoDB: {e}")
            return None

    def deploy_mongodb_standalone(self):
        """Deploy MongoDB as a standalone service for Open5GS"""
        try:
            name = "mongodb"
            config = self.open5gs_config["mongodb"]
            
            # Don't use any port mapping for MongoDB - internal access only
            container = self.client.containers.run(
                config.get("image", "mongo:4.4"),
                name=name,
                network=self.network_name,
                detach=True,
                remove=False,
                environment=config.get("environment", {}),
                restart_policy={"Name": "no"},
                mem_limit=config.get("mem_limit", "256m"),
                memswap_limit=config.get("memswap_limit", "256m")
            )
            
            # Wait for MongoDB to be ready
            import time
            print("⏳ Waiting for MongoDB to initialize...")
            
            # Check if MongoDB is ready by trying to connect
            max_wait = 30  # Maximum wait time in seconds
            wait_interval = 2  # Check every 2 seconds
            mongodb_ready = False
            
            for i in range(0, max_wait, wait_interval):
                try:
                    # Try to execute a simple command to check if MongoDB is ready
                    result = container.exec_run("mongosh --eval 'db.adminCommand(\"ping\")'", timeout=5)
                    if result.exit_code == 0:
                        mongodb_ready = True
                        print(f"✅ MongoDB is ready after {i + wait_interval} seconds")
                        break
                except:
                    pass
                
                print(f"   Waiting... ({i + wait_interval}/{max_wait}s)")
                time.sleep(wait_interval)
            
            if not mongodb_ready:
                print("⚠️ MongoDB may not be fully ready, but continuing with deployment...")
            
            print(f"Deployed standalone MongoDB: {name}")
            return container
            
        except Exception as e:
            print(f"Error deploying standalone MongoDB: {e}")
            return None

    def create_open5gs_config(self, comp_type, name, properties=None):
        """Create Open5GS configuration files using ConfigManager"""
        try:
            # Use the new configuration manager to create instance-specific config
            config_file = self.config_manager.create_instance_config(
                comp_type, name, properties
            )
            
            if config_file:
                print(f"Created Open5GS config file: {config_file}")
                return config_file
            else:
                print(f"Failed to create config for {comp_type}")
                return None
                
        except Exception as e:
            print(f"Error creating config for {comp_type}: {e}")
            return None
    
    def create_gnb_config(self, name, properties=None):
        """Create UERANSIM gNB configuration using ConfigManager"""
        try:
            # Use the new configuration manager to create instance-specific config
            config_file = self.config_manager.create_instance_config(
                'gnb', name, properties
            )
            
            if config_file:
                print(f"Created gNB config: {config_file}")
                return config_file
            else:
                print(f"Failed to create gNB config for {name}")
                return None
                
        except Exception as e:
            print(f"Error creating gNB config: {e}")
            return None
    
    def create_ue_config(self, name, properties=None):
        """Create UERANSIM UE configuration using ConfigManager"""
        try:
            # Use the new configuration manager to create instance-specific config
            config_file = self.config_manager.create_instance_config(
                'ue', name, properties
            )
            
            if config_file:
                print(f"Created UE config: {config_file}")
                return config_file
            else:
                print(f"Failed to create UE config for {name}")
                return None
                
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
            print("🧹 Cleaning up containers and configurations...")
            
            # Stop and remove containers and clean up their configurations
            for container in self.deployed_containers:
                try:
                    container_name = getattr(container, 'name', 'unknown')
                    
                    # Clean up configuration for this instance
                    self.config_manager.cleanup_instance_config(container_name)
                    
                    # Stop and remove container
                    container.stop(timeout=10)
                    container.remove()
                    print(f"Cleaned up container: {container_name}")
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
            
            print("✅ Cleanup completed")
            
        except Exception as e:
            print(f"Error during cleanup: {e}")
    
    def cleanup_containers(self):
        """Alias for cleanup method to maintain compatibility"""
        self.cleanup()
    
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
    
    def pull_required_images(self):
        """Pre-pull all required Docker images to avoid timeout during deployment"""
        required_images = [
            "mongo:4.4",
            "openverso/open5gs:latest", 
            "towards5gs/ueransim-gnb:v3.2.3",
            "towards5gs/ueransim-ue:v3.2.3"
        ]
        
        print("Pre-pulling required Docker images...")
        
        # First check which images already exist locally
        for image in required_images:
            try:
                # Check if image already exists locally
                try:
                    self.client.images.get(image)
                    print(f"✅ {image} already exists locally")
                    continue
                except:
                    pass  # Image doesn't exist, need to pull it
                
                print(f"Pulling {image}... (this may take several minutes)")
                
                # Pull with streaming to show progress
                response = self.client.api.pull(image, stream=True, decode=True)
                layers_downloaded = set()
                
                for line in response:
                    if 'status' in line:
                        status = line['status']
                        layer_id = line.get('id', '')
                        
                        if status == 'Downloading' and layer_id:
                            if layer_id not in layers_downloaded:
                                print(f"  📥 Downloading layer {layer_id[:12]}")
                                layers_downloaded.add(layer_id)
                        elif status == 'Pull complete' and layer_id:
                            print(f"  ✅ Layer {layer_id[:12]} complete")
                        elif 'downloaded' in status.lower():
                            print(f"  📦 {status}")
                
                print(f"✅ Successfully pulled {image}")
                
            except KeyboardInterrupt:
                print(f"\n⚠️ Image pulling interrupted by user")
                return False
            except Exception as e:
                print(f"⚠️ Warning: Failed to pull {image}: {e}")
                print(f"   💡 Tip: You can manually pull this image with: docker pull {image}")
                # Continue anyway - Docker will try to pull during container creation
        
        print("Image pre-pull completed.")
        return True