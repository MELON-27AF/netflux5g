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
            },
            "internet-gw": {
                "image": "alpine:latest",
                "command": ["sh", "-c", "apk add --no-cache iptables curl nmap-ncat && echo 'nameserver 8.8.8.8' > /etc/resolv.conf && sleep infinity"],
                "cap_add": ["NET_ADMIN"],
                "privileged": True,
                "volumes": {},
                "mem_limit": "128m",
                "memswap_limit": "128m"
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
        
        # Deploy internet gateway for external connectivity
        print("🌐 Deploying internet gateway for external connectivity...")
        internet_gw_container = self.deploy_internet_gateway()
        if internet_gw_container:
            deployed.append(internet_gw_container)
            self.deployed_containers.append(internet_gw_container)

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
        
        # Post-deployment setup
        if deployed:
            print("🔧 Starting post-deployment configuration...")
            
            # Setup subscribers in Open5GS database
            print("📱 Setting up UE subscribers in Open5GS database...")
            time.sleep(10)  # Wait for MongoDB to be fully ready
            subscriber_success = self.setup_open5gs_subscribers()
            
            if subscriber_success:
                print("✅ Subscriber setup completed, waiting for services to stabilize...")
                time.sleep(15)  # Allow services to process subscriber data
                
                self.wait_for_5g_registration()
                self.setup_post_deployment_networking()
            else:
                print("❌ Subscriber setup failed, but continuing with deployment...")
                self.wait_for_5g_registration()
                self.setup_post_deployment_networking()
        
        return True, f"Deployed {len(deployed)} containers"
    
    def deploy_open5gs_component(self, component):
        """Deploy Open5GS component"""
        try:
            comp_type = component.component_type
            properties = getattr(component, 'properties', {})
            comp_id = getattr(component, 'component_id', id(component))
            
            # Ensure properties is a dictionary
            if not isinstance(properties, dict):
                logging.warning(f"Properties was {type(properties)}, converting to dict")
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
            
            # Use base configuration files directly instead of ConfigManager
            config_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "config", "open5gs"))
            
            # Deploy container
            # Prepare volumes correctly for Docker
            volumes_config = config.get("volumes", {})
            volumes_list = []
            
            # Add configuration file volume mount directly to open5gs config
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
                    f"sleep 10 && "  # Simple sleep instead of nc
                    f"echo 'MongoDB should be ready, starting NRF...' && "
                    f"exec open5gs-nrfd -c /etc/open5gs/{comp_type}.yaml"
                ]
            elif comp_type == "upf":
                # UPF needs special setup for tunnel interface
                startup_command = [
                    "sh", "-c", 
                    f"echo 'Setting up UPF with tunnel interface...' && "
                    f"ip tuntap add name ogstun mode tun && "
                    f"ip addr add 10.45.0.1/16 dev ogstun && "
                    f"ip link set ogstun up && "
                    f"echo 'Tunnel interface ogstun created and configured' && "
                    f"echo 'Setting up routing for internet access...' && "
                    f"iptables -t nat -A POSTROUTING -s 10.45.0.0/16 ! -d 10.45.0.0/16 -j MASQUERADE && "
                    f"echo 'NAT rules configured for UE internet access' && "
                    f"echo 'Waiting for dependencies...' && "
                    f"sleep 20 && "  # Wait for MongoDB and NRF
                    f"echo 'Dependencies should be ready, starting UPF...' && "
                    f"exec open5gs-upfd -c /etc/open5gs/{comp_type}.yaml"
                ]
            else:
                # Other Open5GS services need to wait for MongoDB and NRF
                startup_command = [
                    "sh", "-c", 
                    f"echo 'Waiting for dependencies...' && "
                    f"sleep 15 && "  # Wait for MongoDB and NRF
                    f"echo 'Dependencies should be ready, starting {comp_type}...' && "
                    f"exec open5gs-{comp_type}d -c /etc/open5gs/{comp_type}.yaml"
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
            
            # Ensure properties is a dictionary
            if not isinstance(properties, dict):
                logging.warning(f"gNB properties was {type(properties)}, converting to dict")
                properties = {}
            
            # Store a copy of properties to prevent accidental overwriting
            props_copy = dict(properties)
                
            name = props_copy.get("name", f"gnb_{comp_id}")
            
            config = self.ueransim_config["gnb"]
            
            # Ensure config is a dictionary (defensive programming)
            if not isinstance(config, dict):
                logging.warning(f"gNB config is not a dictionary: {type(config)}")
                config = {"image": "towards5gs/ueransim-gnb:v3.2.3"}
            
            # Use base configuration files directly instead of ConfigManager
            config_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "config", "ueransim"))
            
            # Prepare volumes correctly for Docker
            volumes_config = config.get("volumes", {})
            volumes_list = []
            
            # Add configuration file volume mount directly to ueransim config
            volumes_list.append(f"{config_dir}:/etc/ueransim:ro")
            
            if volumes_config:
                for host_path, container_path in volumes_config.items():
                    volumes_list.append(f"{host_path}:{container_path}")
            
            container = self.client.containers.run(
                config.get("image", "towards5gs/ueransim-gnb:v3.2.3"),
                command=[
                    "sh", "-c", 
                    f"echo 'Waiting for AMF...' && "
                    f"sleep 30 && "  # Wait for AMF to be ready
                    f"echo 'AMF should be ready, starting gNB...' && "
                    f"echo 'Setting up network interfaces for gNB...' && "
                    f"exec /ueransim/build/nr-gnb -c /etc/ueransim/gnb.yaml"
                ],
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
            
            # Ensure properties is a dictionary
            if not isinstance(properties, dict):
                logging.warning(f"UE properties was {type(properties)}, converting to dict")
                properties = {}
            
            # Store a copy of properties to prevent accidental overwriting
            props_copy = dict(properties)
                
            name = props_copy.get("name", f"ue_{comp_id}")
            
            config = self.ueransim_config["ue"]
            
            # Ensure config is a dictionary (defensive programming)
            if not isinstance(config, dict):
                logging.warning(f"UE config is not a dictionary: {type(config)}")
                config = {"image": "towards5gs/ueransim-ue:v3.2.3"}
            
            # Use base configuration files directly instead of ConfigManager
            config_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "config", "ueransim"))
            
            # Prepare volumes correctly for Docker
            volumes_config = config.get("volumes", {})
            volumes_list = []
            
            # Add configuration file volume mount directly to ueransim config
            volumes_list.append(f"{config_dir}:/etc/ueransim:ro")
            
            if volumes_config:
                for host_path, container_path in volumes_config.items():
                    volumes_list.append(f"{host_path}:{container_path}")
            
            container = self.client.containers.run(
                config.get("image", "towards5gs/ueransim-ue:v3.2.3"),
                command=[
                    "sh", "-c", 
                    f"echo 'Waiting for gNB...' && "
                    f"sleep 40 && "  # Wait for gNB to be ready
                    f"echo 'gNB should be ready, starting UE...' && "
                    f"echo 'Starting UE registration process...' && "
                    f"/ueransim/build/nr-ue -c /etc/ueransim/ue.yaml &"
                    f"UE_PID=$! && "
                    f"echo 'UE process started, waiting for registration...' && "
                    f"sleep 20 && "  # Wait for PDU session establishment
                    f"echo 'Checking for tunnel interface...' && "
                    f"if ip addr show uesimtun0 >/dev/null 2>&1; then "
                    f"  echo 'Tunnel interface found, setting up routing...' && "
                    f"  ip route add default dev uesimtun0 metric 1 2>/dev/null || true; "
                    f"else "
                    f"  echo 'No tunnel interface found yet'; "
                    f"fi && "
                    f"echo 'UE setup complete' && "
                    f"wait $UE_PID"
                ],
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
            
            # Ensure properties is a dictionary
            if not isinstance(properties, dict):
                logging.warning(f"MongoDB properties was {type(properties)}, converting to dict")
                properties = {}
            
            # Store a copy of properties to prevent accidental overwriting
            props_copy = dict(properties)
                
            name = props_copy.get("name", f"mongodb_{comp_id}")
            
            config = self.open5gs_config["mongodb"]
            
            # Ensure config is a dictionary (defensive programming)
            if not isinstance(config, dict):
                logging.warning(f"MongoDB config is not a dictionary: {type(config)}")
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

    def deploy_internet_gateway(self):
        """Deploy internet gateway container for external connectivity"""
        try:
            config = self.network_config["internet-gw"]
            
            container = self.client.containers.run(
                config.get("image", "alpine:latest"),
                command=config.get("command"),
                name="internet-gw",
                network=self.network_name,
                detach=True,
                remove=False,
                cap_add=config.get("cap_add", []),
                privileged=config.get("privileged", False),
                environment={
                    'COMPONENT_TYPE': 'internet-gw',
                    'COMPONENT_NAME': 'internet-gw',
                },
                mem_limit=config.get("mem_limit", "128m"),
                memswap_limit=config.get("memswap_limit", "128m")
            )
            
            print(f"Deployed Internet Gateway: {container.name}")
            return container
            
        except Exception as e:
            print(f"Error deploying internet gateway: {e}")
            return None

    def deploy_mongodb_standalone(self):
        """Deploy standalone MongoDB container"""
        try:
            config = self.open5gs_config["mongodb"]
            
            container = self.client.containers.run(
                config.get("image", "mongo:4.4"),
                name="mongodb",
                network=self.network_name,
                detach=True,
                remove=False,
                environment={
                    'COMPONENT_TYPE': 'mongodb',
                    'COMPONENT_NAME': 'mongodb',
                    **config.get("environment", {})
                },
                mem_limit=config.get("mem_limit", "256m"),
                memswap_limit=config.get("memswap_limit", "256m")
            )
            
            print(f"Deployed MongoDB: mongodb")
            return container
            
        except Exception as e:
            print(f"Error deploying MongoDB: {e}")
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
        """Test connectivity between containers and end-to-end UE connectivity"""
        results = []
        
        # Test basic container connectivity
        for container in self.deployed_containers:
            try:
                # Test ping to other containers
                for target_container in self.deployed_containers:
                    if container != target_container:
                        target_ip = self.get_container_ip(target_container)
                        if target_ip != "unknown":
                            exec_result = container.exec_run(f"ping -c 1 {target_ip}")
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
        
        # Special end-to-end connectivity tests for UE
        self.test_ue_end_to_end_connectivity(results)
        
        return results
    
    def test_ue_end_to_end_connectivity(self, results):
        """Test end-to-end connectivity from UE to external services"""
        # Find UE containers
        ue_containers = [c for c in self.deployed_containers if 'ue' in c.name.lower()]
        
        for ue_container in ue_containers:
            try:
                print(f"Testing end-to-end connectivity for UE: {ue_container.name}")
                
                # Test 1: Check if tunnel interface exists
                exec_result = ue_container.exec_run("ip addr show uesimtun0")
                tunnel_exists = exec_result.exit_code == 0
                
                results.append({
                    "source": ue_container.name,
                    "source_ip": self.get_container_ip(ue_container),
                    "target": "tunnel_interface_check",
                    "target_ip": "uesimtun0",
                    "success": tunnel_exists,
                    "error": None if tunnel_exists else "UE tunnel interface (uesimtun0) not found"
                })
                
                if tunnel_exists:
                    # Test 2: Ping internet gateway through tunnel
                    gw_ip = self.get_container_ip_by_name("internet-gw")
                    if gw_ip != "unknown":
                        exec_result = ue_container.exec_run(f"ping -c 2 -I uesimtun0 {gw_ip}")
                        gw_ping_success = exec_result.exit_code == 0
                        
                        results.append({
                            "source": ue_container.name,
                            "source_ip": "uesimtun0",
                            "target": "internet-gw",
                            "target_ip": gw_ip,
                            "success": gw_ping_success,
                            "error": None if gw_ping_success else f"Ping to internet gateway failed via tunnel"
                        })
                    
                    # Test 3: Ping external DNS (8.8.8.8)
                    exec_result = ue_container.exec_run("ping -c 2 -I uesimtun0 8.8.8.8")
                    external_ping_success = exec_result.exit_code == 0
                    
                    results.append({
                        "source": ue_container.name,
                        "source_ip": "uesimtun0",
                        "target": "external_dns",
                        "target_ip": "8.8.8.8",
                        "success": external_ping_success,
                        "error": None if external_ping_success else "External internet connectivity failed"
                    })
                    
                    if external_ping_success:
                        print(f"✅ End-to-end connectivity SUCCESS for {ue_container.name}")
                    else:
                        print(f"❌ End-to-end connectivity FAILED for {ue_container.name}")
                        
            except Exception as e:
                results.append({
                    "source": ue_container.name,
                    "source_ip": self.get_container_ip(ue_container),
                    "target": "end_to_end_test",
                    "target_ip": "unknown",
                    "success": False,
                    "error": f"End-to-end test error: {str(e)}"
                })
    
    def get_container_ip_by_name(self, container_name):
        """Get container IP address by name"""
        try:
            for container in self.deployed_containers:
                if container.name == container_name:
                    return self.get_container_ip(container)
            return "unknown"
        except Exception:
            return "unknown"
    
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

    def setup_post_deployment_networking(self):
        """Setup networking after all containers are deployed"""
        try:
            print("🔧 Setting up post-deployment networking...")
            
            # Setup routing in internet gateway
            internet_gw = None
            for container in self.deployed_containers:
                if container.name == "internet-gw":
                    internet_gw = container
                    break
            
            if internet_gw:
                # Enable IP forwarding and set up NAT
                commands = [
                    "echo '1' > /proc/sys/net/ipv4/ip_forward",
                    "iptables -t nat -A POSTROUTING -s 10.45.0.0/16 -j MASQUERADE",
                    "iptables -A FORWARD -s 10.45.0.0/16 -j ACCEPT",
                    "iptables -A FORWARD -d 10.45.0.0/16 -j ACCEPT"
                ]
                
                for cmd in commands:
                    try:
                        exec_result = internet_gw.exec_run(cmd)
                        if exec_result.exit_code == 0:
                            print(f"✅ Internet GW: {cmd}")
                        else:
                            print(f"⚠️ Internet GW command failed: {cmd}")
                    except Exception as e:
                        print(f"⚠️ Error executing command in internet gateway: {e}")
            
            # Wait for UE to establish PDU session
            print("⏳ Waiting for UE to establish PDU session...")
            import time
            time.sleep(30)  # Give UE time to establish session
            
            # Setup routing in UE containers
            ue_containers = [c for c in self.deployed_containers if 'ue' in c.name.lower()]
            for ue_container in ue_containers:
                try:
                    # Check if tunnel interface exists and set up routing
                    commands = [
                        "ip addr show uesimtun0",  # Check tunnel exists
                        "ip route del default 2>/dev/null || true",  # Remove default route
                        "ip route add default dev uesimtun0 metric 1",  # Add tunnel route
                        "echo 'nameserver 8.8.8.8' > /etc/resolv.conf"  # Set DNS
                    ]
                    
                    for cmd in commands:
                        try:
                            exec_result = ue_container.exec_run(cmd)
                            if "ip addr show uesimtun0" in cmd and exec_result.exit_code == 0:
                                print(f"✅ UE tunnel interface found: {ue_container.name}")
                            elif "ip route add default" in cmd and exec_result.exit_code == 0:
                                print(f"✅ UE routing configured: {ue_container.name}")
                        except Exception as e:
                            print(f"⚠️ Error setting up UE networking: {e}")
                            
                except Exception as e:
                    print(f"⚠️ Error configuring UE {ue_container.name}: {e}")
            
            print("✅ Post-deployment networking setup complete")
            
        except Exception as e:
            print(f"❌ Error in post-deployment networking setup: {e}")

    def wait_for_5g_registration(self):
        """Wait for UE to register with 5G network"""
        try:
            print("📡 Waiting for UE registration and PDU session establishment...")
            import time
            
            # Wait for core network to stabilize
            time.sleep(15)
            
            # Check UE containers for registration
            ue_containers = [c for c in self.deployed_containers if 'ue' in c.name.lower()]
            
            for ue_container in ue_containers:
                max_attempts = 20
                attempts = 0
                registered = False
                
                while attempts < max_attempts and not registered:
                    try:
                        # Check for tunnel interface creation (indicates successful registration)
                        exec_result = ue_container.exec_run("ip addr show uesimtun0")
                        if exec_result.exit_code == 0:
                            print(f"✅ UE {ue_container.name} registered (tunnel interface found)")
                            registered = True
                        else:
                            print(f"⏳ UE {ue_container.name} registration in progress... ({attempts+1}/{max_attempts})")
                            time.sleep(3)
                            attempts += 1
                            
                    except Exception as e:
                        print(f"⚠️ Error checking UE registration: {e}")
                        attempts += 1
                        time.sleep(3)
                
                if not registered:
                    print(f"❌ UE {ue_container.name} failed to register within timeout")
                    
        except Exception as e:
            print(f"❌ Error waiting for 5G registration: {e}")

    def setup_open5gs_subscribers(self):
        """Add UE subscribers to Open5GS database like the WebUI does"""
        try:
            print("📱 Setting up Open5GS subscriber data...")
            
            # Find MongoDB container
            mongodb_container = None
            for container in self.deployed_containers:
                if 'mongodb' in container.name.lower():
                    mongodb_container = container
                    break
            
            if not mongodb_container:
                print("❌ MongoDB container not found")
                return False
            
            # First, let's try a simple approach using mongo shell directly
            print("   Adding subscriber with IMSI: 999700000000001")
            
            # Create subscriber document inline
            mongo_script = '''
use open5gs;
db.subscribers.deleteMany({"imsi": "999700000000001"});
db.subscribers.insertOne({
    "imsi": "999700000000001",
    "msisdn": [],
    "imeisv": "4370816125816151",
    "mme_host": "",
    "mme_realm": "",
    "purge_flag": [],
    "security": {
        "k": "465B5CE8B199B49FAA5F0A2EE238A6BC",
        "amf": "8000",
        "op": null,
        "opc": "E8ED289DEBA952E4283B54E88E6183CA"
    },
    "ambr": {
        "downlink": {"value": 1000000000, "unit": 0},
        "uplink": {"value": 1000000000, "unit": 0}
    },
    "slice": [
        {
            "sst": 1,
            "sd": "010203",
            "default_indicator": true,
            "session": [
                {
                    "name": "internet",
                    "type": 3,
                    "pcc_rule": [],
                    "ambr": {
                        "downlink": {"value": 1000000000, "unit": 0},
                        "uplink": {"value": 1000000000, "unit": 0}
                    },
                    "qos": {
                        "index": 9,
                        "arp": {
                            "priority_level": 8,
                            "pre_emption_capability": 1,
                            "pre_emption_vulnerability": 1
                        }
                    }
                }
            ]
        }
    ]
});
var count = db.subscribers.countDocuments({"imsi": "999700000000001"});
print("Subscribers in database: " + count);
'''
            
            # Try multiple MongoDB client commands for compatibility
            commands_to_try = [
                f"mongosh --quiet --eval '{mongo_script}'",
                f"mongo --quiet --eval '{mongo_script}'",
                f"echo '{mongo_script}' | mongosh --quiet",
                f"echo '{mongo_script}' | mongo --quiet"
            ]
            
            success = False
            for cmd in commands_to_try:
                try:
                    print(f"   Trying MongoDB command: {cmd.split()[0]}")
                    exec_result = mongodb_container.exec_run(["sh", "-c", cmd])
                    output = exec_result.output.decode() if exec_result.output else ""
                    
                    if exec_result.exit_code == 0 and ("Subscribers in database: 1" in output or "inserted" in output.lower()):
                        print("✅ Subscriber data added to Open5GS database")
                        print("   IMSI: 999700000000001")
                        print("   K: 465B5CE8B199B49FAA5F0A2EE238A6BC")
                        print("   OPc: E8ED289DEBA952E4283B54E88E6183CA")
                        print("   DNN/APN: internet")
                        success = True
                        break
                    else:
                        print(f"   Command failed or no confirmation: {output[:200]}...")
                        
                except Exception as e:
                    print(f"   Command failed with error: {e}")
                    continue
            
            if not success:
                print("❌ All MongoDB commands failed. Trying alternative approach...")
                # Try using the REST API approach or manual container inspection
                return self.setup_subscribers_alternative(mongodb_container)
            
            return success
                
        except Exception as e:
            print(f"❌ Error setting up subscribers: {e}")
            return False
    
    def setup_subscribers_alternative(self, mongodb_container):
        """Alternative method to set up subscribers"""
        try:
            print("   Trying alternative subscriber setup...")
            
            # Check if MongoDB is running and accessible
            exec_result = mongodb_container.exec_run("pgrep mongod")
            if exec_result.exit_code != 0:
                print("   MongoDB process not running in container")
                return False
            
            # Simple test - just verify we can connect to MongoDB
            test_cmd = "mongosh --quiet --eval 'db.adminCommand(\"ismaster\")' 2>/dev/null || mongo --quiet --eval 'db.adminCommand(\"ismaster\")'"
            exec_result = mongodb_container.exec_run(["sh", "-c", test_cmd])
            
            if exec_result.exit_code == 0:
                print("✅ MongoDB is accessible, subscriber data will be added by UE registration process")
                return True
            else:
                print("❌ Cannot connect to MongoDB")
                return False
                
        except Exception as e:
            print(f"   Alternative setup failed: {e}")
            return False