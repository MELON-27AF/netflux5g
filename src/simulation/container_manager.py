import docker
import subprocess
import time
import json
import os
import logging
from datetime import datetime

class ContainerManager:
    def __init__(self):
        try:
            logging.info("Initializing ContainerManager...")
            self.client = docker.from_env()
            logging.info("Docker client connected successfully")
        except Exception as e:
            logging.error(f"Error connecting to Docker: {e}")
            print(f"Error connecting to Docker: {e}")
            self.client = None
        
        self.deployed_containers = []
        self.network_name = "netflux5g_network"
        
    def create_5g_network(self):
        """Create a Docker network for 5G components"""
        try:
            # Remove existing network if it exists
            try:
                existing_network = self.client.networks.get(self.network_name)
                existing_network.remove()
                print(f"Removed existing network: {self.network_name}")
            except docker.errors.NotFound:
                pass
            
            # Create new network
            network = self.client.networks.create(
                self.network_name,
                driver="bridge",
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
        """Deploy 5G core components as Docker containers"""
        if not self.client:
            return False, "Docker client not available"
        
        # Create network first
        network = self.create_5g_network()
        if not network:
            return False, "Failed to create Docker network"
        
        deployed = []
        
        # Deploy each component
        for component in components:
            if component.component_type in ['amf', 'smf', 'upf', 'pcf', 'udm', 'ausf', 'nrf']:
                container = self.deploy_core_component(component)
                if container:
                    deployed.append(container)
            elif component.component_type == 'gnb':
                container = self.deploy_gnb_component(component)
                if container:
                    deployed.append(container)
            elif component.component_type == 'ue':
                container = self.deploy_ue_component(component)
                if container:
                    deployed.append(container)
        
        self.deployed_containers = deployed
        return True, f"Deployed {len(deployed)} containers"
    
    def deploy_core_component(self, component):
        """Deploy a 5G core component"""
        try:
            # Safe property access
            properties = getattr(component, 'properties', {})
            comp_type = getattr(component, 'component_type', 'unknown')
            comp_id = getattr(component, 'component_id', id(component))
            
            name = properties.get("name", f"{comp_type}_{comp_id}")
            
            # Use open5gs images or ubuntu with networking tools for simulation
            image_map = {
                'nrf': 'ubuntu:20.04',
                'amf': 'ubuntu:20.04', 
                'smf': 'ubuntu:20.04',
                'upf': 'ubuntu:20.04',
                'pcf': 'ubuntu:20.04',
                'udm': 'ubuntu:20.04',
                'ausf': 'ubuntu:20.04'
            }
            
            image = image_map.get(component.component_type, 'ubuntu:20.04')
            
            # Create container with networking tools
            container = self.client.containers.run(
                image,
                command="sleep infinity",
                name=name,
                network=self.network_name,
                detach=True,
                remove=False,
                cap_add=['NET_ADMIN'],
                environment={
                    'COMPONENT_TYPE': component.component_type,
                    'COMPONENT_NAME': name
                }
            )
            
            # Install networking tools
            self.setup_container_networking(container)
            
            print(f"Deployed {component.component_type}: {name}")
            return container
            
        except Exception as e:
            logging.error(f"Error deploying {getattr(component, 'component_type', 'unknown')}: {e}")
            print(f"Error deploying {getattr(component, 'component_type', 'unknown')}: {e}")
            return None
    
    def deploy_gnb_component(self, component):
        """Deploy gNB component"""
        try:
            name = component.properties.get("name", f"gnb_{component.component_id}")
            
            container = self.client.containers.run(
                'ubuntu:20.04',
                command="sleep infinity",
                name=name,
                network=self.network_name,
                detach=True,
                remove=False,
                cap_add=['NET_ADMIN'],
                privileged=True,
                environment={
                    'COMPONENT_TYPE': 'gnb',
                    'COMPONENT_NAME': name,
                    'TAC': str(component.properties.get('tac', 1)),
                    'POWER': str(component.properties.get('power', 20))
                }
            )
            
            self.setup_container_networking(container)
            print(f"Deployed gNB: {name}")
            return container
            
        except Exception as e:
            print(f"Error deploying gNB: {e}")
            return None
    
    def deploy_ue_component(self, component):
        """Deploy UE component"""
        try:
            name = component.properties.get("name", f"ue_{component.component_id}")
            
            container = self.client.containers.run(
                'ubuntu:20.04',
                command="sleep infinity", 
                name=name,
                network=self.network_name,
                detach=True,
                remove=False,
                cap_add=['NET_ADMIN'],
                environment={
                    'COMPONENT_TYPE': 'ue',
                    'COMPONENT_NAME': name,
                    'IMSI': component.properties.get('imsi', '001010000000001')
                }
            )
            
            self.setup_container_networking(container)
            print(f"Deployed UE: {name}")
            return container
            
        except Exception as e:
            print(f"Error deploying UE: {e}")
            return None
    
    def setup_container_networking(self, container):
        """Setup networking tools in container"""
        try:
            # Update and install networking tools
            container.exec_run("apt-get update", detach=False)
            container.exec_run("apt-get install -y iputils-ping net-tools iproute2 curl", detach=False)
        except Exception as e:
            print(f"Warning: Failed to setup networking in container: {e}")
    
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
                ip = container.attrs['NetworkSettings']['Networks'][self.network_name]['IPAddress']
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
                        exec_result = source['container'].exec_run(
                            f"ping -c 3 -W 2 {target['ip']}", 
                            stdout=True, 
                            stderr=True
                        )
                        
                        success = exec_result.exit_code == 0
                        output = exec_result.output.decode('utf-8')
                        
                        results.append({
                            'source': source['name'],
                            'source_ip': source['ip'],
                            'target': target['name'], 
                            'target_ip': target['ip'],
                            'success': success,
                            'output': output
                        })
                        
                    except Exception as e:
                        results.append({
                            'source': source['name'],
                            'source_ip': source['ip'],
                            'target': target['name'],
                            'target_ip': target['ip'], 
                            'success': False,
                            'error': str(e)
                        })
        
        return results
    
    def get_container_status(self):
        """Get status of all deployed containers"""
        status = []
        for container in self.deployed_containers:
            try:
                container.reload()
                ip = container.attrs['NetworkSettings']['Networks'][self.network_name]['IPAddress']
                status.append({
                    'name': container.name,
                    'status': container.status,
                    'ip': ip,
                    'id': container.short_id
                })
            except Exception as e:
                status.append({
                    'name': container.name,
                    'status': 'error',
                    'error': str(e)
                })
        
        return status
    
    def cleanup(self):
        """Clean up deployed containers and network"""
        try:
            # Stop and remove containers
            for container in self.deployed_containers:
                try:
                    container.stop()
                    container.remove()
                    print(f"Removed container: {container.name}")
                except Exception as e:
                    print(f"Error removing container {container.name}: {e}")
            
            # Remove network
            try:
                network = self.client.networks.get(self.network_name)
                network.remove()
                print(f"Removed network: {self.network_name}")
            except docker.errors.NotFound:
                pass
            except Exception as e:
                print(f"Error removing network: {e}")
                
            self.deployed_containers = []
            
        except Exception as e:
            print(f"Error during cleanup: {e}")
    
    def open_terminal_to_container(self, container_name):
        """Open terminal to specific container"""
        try:
            # Open terminal using system command
            if os.name == 'nt':  # Windows
                subprocess.Popen([
                    'cmd', '/k', 
                    f'docker exec -it {container_name} /bin/bash'
                ])
            else:  # Linux/Mac
                subprocess.Popen([
                    'gnome-terminal', '--', 
                    'docker', 'exec', '-it', container_name, '/bin/bash'
                ])
        except Exception as e:
            print(f"Error opening terminal: {e}")
            # Fallback: just print the command
            print(f"Run this command in your terminal: docker exec -it {container_name} /bin/bash")
