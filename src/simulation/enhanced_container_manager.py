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
            },            "nrf": {
                "image": "gradiant/open5gs:1.0",
                "command": ["open5gs-nrfd", "-c", "/etc/open5gs/nrf.yaml"],
                "ports": {"7777": "7777"},
                "depends_on": ["mongodb"],
                "volumes": {
                    "/etc/open5gs": "/etc/open5gs"
                }
            },            "amf": {
                "image": "gradiant/open5gs:1.0",
                "command": ["open5gs-amfd", "-c", "/etc/open5gs/amf.yaml"],
                "ports": {"38412": "38412"},
                "depends_on": ["nrf"],
                "volumes": {
                    "/etc/open5gs": "/etc/open5gs"
                }
            },            "smf": {
                "image": "gradiant/open5gs:1.0",
                "command": ["open5gs-smfd", "-c", "/etc/open5gs/smf.yaml"],
                "depends_on": ["nrf"],
                "volumes": {
                    "/etc/open5gs": "/etc/open5gs"
                }
            },            "upf": {
                "image": "gradiant/open5gs:1.0",
                "command": ["open5gs-upfd", "-c", "/etc/open5gs/upf.yaml"],
                "ports": {"8805": "8805"},
                "cap_add": ["NET_ADMIN"],
                "depends_on": ["smf"],
                "volumes": {
                    "/etc/open5gs": "/etc/open5gs"
                }
            },            "ausf": {
                "image": "gradiant/open5gs:1.0",
                "command": ["open5gs-ausfd", "-c", "/etc/open5gs/ausf.yaml"],
                "depends_on": ["nrf"],
                "volumes": {
                    "/etc/open5gs": "/etc/open5gs"
                }
            },            "udm": {
                "image": "gradiant/open5gs:1.0",
                "command": ["open5gs-udmd", "-c", "/etc/open5gs/udm.yaml"],
                "depends_on": ["nrf"],
                "volumes": {
                    "/etc/open5gs": "/etc/open5gs"
                }
            },            "pcf": {
                "image": "gradiant/open5gs:1.0",
                "command": ["open5gs-pcfd", "-c", "/etc/open5gs/pcf.yaml"],
                "depends_on": ["nrf"],
                "volumes": {
                    "/etc/open5gs": "/etc/open5gs"
                }
            }        }
        
        self.ueransim_config = {
            "gnb": {
                "image": "gradiant/ueransim:1.0",
                "command": ["nr-gnb", "-c", "/etc/ueransim/gnb.yaml"],
                "cap_add": ["NET_ADMIN"],
                "privileged": True,
                "volumes": {
                    "/etc/ueransim": "/etc/ueransim"
                }
            },
            "ue": {
                "image": "gradiant/ueransim:1.0", 
                "command": ["nr-ue", "-c", "/etc/ueransim/ue.yaml"],
                "cap_add": ["NET_ADMIN"],
                "privileged": True,
                "volumes": {
                    "/etc/ueransim": "/etc/ueransim"
                }
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
            name = properties.get("name", f"{comp_type}_{comp_id}")
            
            if comp_type not in self.open5gs_config:
                print(f"Unknown Open5GS component type: {comp_type}")
                return None
            
            config = self.open5gs_config[comp_type]
            
            # Create configuration files if needed
            self.create_open5gs_config(comp_type, name, properties)
            
            # Deploy container
            container = self.client.containers.run(
                config["image"],
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
                ports=config.get("ports", {}),
                volumes=config.get("volumes", {})
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
            name = properties.get("name", f"gnb_{comp_id}")
            
            # Create gNB configuration
            self.create_gnb_config(name, properties)
            
            config = self.ueransim_config["gnb"]
            
            container = self.client.containers.run(
                config["image"],
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
                volumes=config.get("volumes", {})
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
            name = properties.get("name", f"ue_{comp_id}")
            
            # Create UE configuration
            self.create_ue_config(name, properties)
            
            config = self.ueransim_config["ue"]
            
            container = self.client.containers.run(
                config["image"],
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
                volumes=config.get("volumes", {})
            )
            
            print(f"Deployed UERANSIM UE: {name}")
            return container
            
        except Exception as e:
            print(f"Error deploying UE: {e}")
            return None
    
    def create_open5gs_config(self, component_type, name, properties):
        """Create Open5GS configuration files"""
        # This would create proper YAML configuration files for Open5GS
        # For now, we'll use default configurations
        pass
    
    def create_gnb_config(self, name, properties):
        """Create gNB configuration file for UERANSIM"""
        # This would create proper YAML configuration for gNB
        pass
    
    def create_ue_config(self, name, properties):
        """Create UE configuration file for UERANSIM"""
        # This would create proper YAML configuration for UE
        pass
    
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
    
    def test_connectivity(self):
        """Test connectivity between containers"""
        if not self.deployed_containers:
            return []
        
        results = []
        containers_info = []
        
        # Get container IPs
        for container in self.deployed_containers:
            try:
                container.reload()
                networks = container.attrs['NetworkSettings']['Networks']
                if self.network_name in networks:
                    ip = networks[self.network_name]['IPAddress']
                    containers_info.append({
                        'name': container.name,
                        'ip': ip,
                        'container': container
                    })
            except Exception as e:
                print(f"Error getting IP for {container.name}: {e}")
        
        # Test ping between all containers
        for i, source in enumerate(containers_info):
            for j, target in enumerate(containers_info):
                if i != j:  # Don't ping self
                    try:
                        # Execute ping command
                        result = source['container'].exec_run(
                            f"ping -c 1 -W 2 {target['ip']}", 
                            detach=False
                        )
                        success = result.exit_code == 0
                        
                        results.append({
                            'source': source['name'],
                            'target': target['name'],
                            'source_ip': source['ip'],
                            'target_ip': target['ip'],
                            'success': success,
                            'output': result.output.decode() if result.output else ""
                        })
                    except Exception as e:
                        results.append({
                            'source': source['name'],
                            'target': target['name'],
                            'source_ip': source['ip'],
                            'target_ip': target['ip'],
                            'success': False,
                            'output': f"Error: {str(e)}"
                        })
        
        return results
    
    def get_container_status(self):
        """Get status of all deployed containers"""
        status = []
        for container in self.deployed_containers:
            try:
                container.reload()
                networks = container.attrs['NetworkSettings']['Networks']
                ip = networks.get(self.network_name, {}).get('IPAddress', 'N/A')
                
                status.append({
                    'name': container.name,
                    'status': container.status,
                    'ip': ip,
                    'image': container.image.tags[0] if container.image.tags else 'unknown'
                })
            except Exception as e:
                status.append({
                    'name': container.name if hasattr(container, 'name') else 'unknown',
                    'status': 'error',
                    'ip': 'N/A',
                    'image': 'unknown',
                    'error': str(e)
                })
        
        return status
    
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
        """Get list of all containers for terminal access"""
        return [(container.name, container) for container in self.deployed_containers]
    
    def execute_command_in_container(self, container_name, command):
        """Execute command in specific container"""
        try:
            for container in self.deployed_containers:
                if container.name == container_name:
                    result = container.exec_run(command, detach=False)
                    return {
                        'exit_code': result.exit_code,
                        'output': result.output.decode() if result.output else ""
                    }
            return {'exit_code': 1, 'output': f'Container {container_name} not found'}
        except Exception as e:
            return {'exit_code': 1, 'output': f'Error: {str(e)}'}
