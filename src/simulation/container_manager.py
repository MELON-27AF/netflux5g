import docker
import subprocess
import time
import json
import os
import logging
import docker
import logging
from datetime import datetime
import subprocess
import os
import time

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
            name = properties.get("name", f"{comp_type}_{comp_id}")              # Use Open5GS Docker images for 5G core components
            image_map = {
                'nrf': 'openverso/open5gs:latest',
                'amf': 'openverso/open5gs:latest', 
                'smf': 'openverso/open5gs:latest',
                'upf': 'openverso/open5gs:latest',
                'pcf': 'openverso/open5gs:latest',
                'udm': 'openverso/open5gs:latest',
                'ausf': 'openverso/open5gs:latest'
            }
            
            image = image_map.get(component.component_type, 'openverso/open5gs:latest')
            
            # Get component-specific command and configuration
            command = self.get_open5gs_command(component.component_type)
            
            # Create container with Open5GS configuration
            container = self.client.containers.run(
                image,
                command=command,
                name=name,
                network=self.network_name,
                detach=True,
                remove=False,
                cap_add=['NET_ADMIN'],
                ports={f'{self.get_component_port(component.component_type)}/tcp': None} if self.get_component_port(component.component_type) else None,
                environment={
                    'COMPONENT_TYPE': component.component_type,
                    'COMPONENT_NAME': name,
                    'OPEN5GS_LOG_LEVEL': 'info'
                },
                volumes={
                    '/etc/open5gs': {'bind': '/etc/open5gs', 'mode': 'rw'}
                } if os.path.exists('/etc/open5gs') else None            )
            
            # Install networking tools
            self.setup_container_networking(container)
            
            print(f"Deployed {component.component_type}: {name}")
            return container
            
        except Exception as e:
            logging.error(f"Error deploying {getattr(component, 'component_type', 'unknown')}: {e}")
            print(f"Error deploying {getattr(component, 'component_type', 'unknown')}: {e}")
            return None

    def deploy_gnb_component(self, component):
        """Deploy gNB component using UERANSIM"""
        try:
            name = component.properties.get("name", f"gnb_{component.component_id}")
            
            container = self.client.containers.run(
                'openverso/ueransim:latest',
                command="sleep infinity",  # Will be configured later
                name=name,
                network=self.network_name,
                detach=True,
                remove=False,
                cap_add=['NET_ADMIN'],
                privileged=True,
                environment={
                    'COMPONENT_TYPE': 'gnb',
                    'COMPONENT_NAME': name,
                    'MCC': str(component.properties.get('mcc', '001')),
                    'MNC': str(component.properties.get('mnc', '01')),
                    'TAC': str(component.properties.get('tac', 1)),
                    'PLMN_ID': f"{component.properties.get('mcc', '001')}{component.properties.get('mnc', '01')}",
                    'AMF_IP': component.properties.get('amf_ip', '172.17.0.1'),
                    'GNB_ID': str(component.properties.get('gnb_id', 1))
                }
            )
            
            self.setup_container_networking(container)
            print(f"Deployed gNB: {name}")
            return container
            
        except Exception as e:
            print(f"Error deploying gNB: {e}")
            return None
    
    def deploy_ue_component(self, component):
        """Deploy UE component using UERANSIM"""
        try:
            name = component.properties.get("name", f"ue_{component.component_id}")
            
            container = self.client.containers.run(
                'openverso/ueransim:latest',
                command="sleep infinity",  # Will be configured later
                name=name,
                network=self.network_name,
                detach=True,
                remove=False,
                cap_add=['NET_ADMIN'],
                environment={
                    'COMPONENT_TYPE': 'ue',
                    'COMPONENT_NAME': name,
                    'IMSI': component.properties.get('imsi', '001010000000001'),
                    'IMEI': component.properties.get('imei', '356938035643803'),
                    'MCC': str(component.properties.get('mcc', '001')),
                    'MNC': str(component.properties.get('mnc', '01')),
                    'PLMN_ID': f"{component.properties.get('mcc', '001')}{component.properties.get('mnc', '01')}",
                    'GNB_IP': component.properties.get('gnb_ip', '172.17.0.1')
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
                        output = exec_result.output.decode('utf-8');
                        
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
    
    def get_open5gs_command(self, component_type):
        """Get the appropriate Open5GS command for each component"""
        command_map = {
            'nrf': '/usr/bin/open5gs-nrfd -c /etc/open5gs/nrf.yaml',
            'amf': '/usr/bin/open5gs-amfd -c /etc/open5gs/amf.yaml',
            'smf': '/usr/bin/open5gs-smfd -c /etc/open5gs/smf.yaml',
            'upf': '/usr/bin/open5gs-upfd -c /etc/open5gs/upf.yaml',
            'pcf': '/usr/bin/open5gs-pcfd -c /etc/open5gs/pcf.yaml',
            'udm': '/usr/bin/open5gs-udmd -c /etc/open5gs/udm.yaml',
            'ausf': '/usr/bin/open5gs-ausfd -c /etc/open5gs/ausf.yaml'
        }
        return command_map.get(component_type, 'sleep infinity')
    
    def get_component_port(self, component_type):
        """Get the default port for each Open5GS component"""
        port_map = {
            'nrf': 7777,
            'amf': 38412,
            'smf': 8805,
            'upf': 8805,
            'pcf': 7777,
            'udm': 7777,
            'ausf': 7777
        }
        return port_map.get(component_type)
    
    def create_open5gs_config(self, component_type, component_name):
        """Create Open5GS configuration for component"""
        configs = {
            'nrf': {
                'logger': {'level': 'info'},
                'nrf': {
                    'sbi': [{'addr': '0.0.0.0', 'port': 7777}]
                }
            },
            'amf': {
                'logger': {'level': 'info'},
                'amf': {
                    'sbi': [{'addr': '0.0.0.0', 'port': 7777}],
                    'ngap': [{'addr': '0.0.0.0'}],
                    'guami': [{'plmn_id': {'mcc': '001', 'mnc': '01'}, 'amf_id': {'region': 2, 'set': 1}}],
                    'tai': [{'plmn_id': {'mcc': '001', 'mnc': '01'}, 'tac': 1}],
                    'plmn_support': [{'plmn_id': {'mcc': '001', 'mnc': '01'}, 's_nssai': [{'sst': 1}]}],
                    'security': {'integrity_order': ['NIA2', 'NIA1', 'NIA0'], 'ciphering_order': ['NEA0', 'NEA1', 'NEA2']}
                },
                'nrf': {'sbi': [{'addr': 'nrf', 'port': 7777}]}
            }
        }
        return configs.get(component_type, {})
    
    def setup_ueransim_config(self, container, component_type, properties):
        """Setup UERANSIM configuration files"""
        try:
            if component_type == 'gnb':
                config = self.create_gnb_config(properties)
                container.exec_run(f"echo '{config}' > /etc/ueransim/gnb.yaml", detach=False)
            elif component_type == 'ue':
                config = self.create_ue_config(properties)
                container.exec_run(f"echo '{config}' > /etc/ueransim/ue.yaml", detach=False)
        except Exception as e:
            print(f"Warning: Failed to setup UERANSIM config: {e}")
    
    def create_gnb_config(self, properties):
        """Create gNB configuration for UERANSIM"""
        return f"""mcc: '{properties.get('mcc', '001')}'
mnc: '{properties.get('mnc', '01')}'
nci: {properties.get('gnb_id', 1)}
idLength: 32
tac: {properties.get('tac', 1)}
linkIp: 0.0.0.0
ngapIp: 0.0.0.0
gtpIp: 0.0.0.0
amfConfigs:
  - address: {properties.get('amf_ip', '172.17.0.1')}
    port: 38412
slices:
  - sst: 0x01
    sd: 0x010203
ignoreStreamIds: true"""
    
    def create_ue_config(self, properties):
        """Create UE configuration for UERANSIM"""
        return f"""supi: 'imsi-{properties.get('imsi', '001010000000001')}'
mcc: '{properties.get('mcc', '001')}'
mnc: '{properties.get('mnc', '01')}'
routingIndicator: '0000'
protectionScheme: 0
homeNetworkPublicKey: '5a8d38864820197c3394b92613b20b76b976fdeb15f69e45b8a6194db36d7045'
homeNetworkPrivateKey: 'f69e45b8a6194db36d7045' 
homeNetworkPublicKeyId: 1
pdnList:
  - apn: 'internet'
    slice:
      sst: 0x01
      sd: 0x010203
integrityList: ['NIA1', 'NIA2', 'NIA3']
cipheringList: ['NEA1', 'NEA2', 'NEA3']
gnbSearchList:
  - {properties.get('gnb_ip', '172.17.0.1')}"""
