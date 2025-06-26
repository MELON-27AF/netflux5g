#!/usr/bin/env python3
"""
NetFlux5G Configuration Manager
Loads and customizes YAML configuration files for 5G components
"""

import os
import yaml
import shutil
from typing import Dict, Any, Optional

class ConfigManager:
    """Manages configuration files for NetFlux5G 5G components"""
    
    def __init__(self, config_base_dir: str = "./config"):
        self.config_base_dir = config_base_dir
        self.open5gs_templates_dir = os.path.join(config_base_dir, "open5gs")
        self.ueransim_templates_dir = os.path.join(config_base_dir, "ueransim")
        self.instance_configs_dir = os.path.join(config_base_dir, "instances")
        
        # Ensure instance configurations directory exists
        os.makedirs(self.instance_configs_dir, exist_ok=True)
        
        # Supported component types
        self.open5gs_components = ['nrf', 'amf', 'smf', 'upf', 'ausf', 'udm', 'pcf']
        self.ueransim_components = ['gnb', 'ue']
        
    def load_template_config(self, component_type: str) -> Dict[str, Any]:
        """Load the base template configuration for a component type"""
        try:
            if component_type in self.open5gs_components:
                config_file = os.path.join(self.open5gs_templates_dir, f"{component_type}.yaml")
            elif component_type in self.ueransim_components:
                config_file = os.path.join(self.ueransim_templates_dir, f"{component_type}.yaml")
            else:
                raise ValueError(f"Unknown component type: {component_type}")
                
            if not os.path.exists(config_file):
                raise FileNotFoundError(f"Template config file not found: {config_file}")
                
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
                
            print(f"Loaded template config for {component_type}")
            return config
            
        except Exception as e:
            print(f"Error loading template config for {component_type}: {e}")
            return {}
    
    def customize_config(self, component_type: str, instance_name: str, 
                        properties: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Customize a configuration based on component properties"""
        config = self.load_template_config(component_type)
        
        if not config or not properties:
            return config
            
        try:
            # Apply customizations based on component type
            if component_type == 'amf':
                config = self._customize_amf_config(config, properties)
            elif component_type == 'smf':
                config = self._customize_smf_config(config, properties)
            elif component_type == 'upf':
                config = self._customize_upf_config(config, properties)
            elif component_type == 'gnb':
                config = self._customize_gnb_config(config, properties)
            elif component_type == 'ue':
                config = self._customize_ue_config(config, properties)
            # Add more component-specific customizations as needed
                
            print(f"Customized config for {component_type} instance {instance_name}")
            return config
            
        except Exception as e:
            print(f"Error customizing config for {component_type}: {e}")
            return config
    
    def _customize_amf_config(self, config: Dict[str, Any], properties: Dict[str, Any]) -> Dict[str, Any]:
        """Customize AMF configuration"""
        # Update MCC/MNC if provided
        mcc = properties.get('mcc', '999')
        mnc = properties.get('mnc', '70')
        
        if 'amf' in config:
            # Update GUAMI
            if 'guami' in config['amf']:
                for guami in config['amf']['guami']:
                    guami['plmn_id']['mcc'] = mcc
                    guami['plmn_id']['mnc'] = mnc
                    
            # Update TAI
            if 'tai' in config['amf']:
                for tai in config['amf']['tai']:
                    tai['plmn_id']['mcc'] = mcc
                    tai['plmn_id']['mnc'] = mnc
                    if 'tac' in properties:
                        tai['tac'] = properties['tac']
                        
            # Update PLMN support
            if 'plmn_support' in config['amf']:
                for plmn in config['amf']['plmn_support']:
                    plmn['plmn_id']['mcc'] = mcc
                    plmn['plmn_id']['mnc'] = mnc
                    
        return config
    
    def _customize_smf_config(self, config: Dict[str, Any], properties: Dict[str, Any]) -> Dict[str, Any]:
        """Customize SMF configuration"""
        # Update subnet if provided
        if 'subnet' in properties and 'smf' in config:
            if 'subnet' in config['smf']:
                config['smf']['subnet'][0]['addr'] = properties['subnet']
                
        # Update DNS servers if provided
        if 'dns_servers' in properties and 'smf' in config:
            config['smf']['dns'] = properties['dns_servers']
            
        return config
    
    def _customize_upf_config(self, config: Dict[str, Any], properties: Dict[str, Any]) -> Dict[str, Any]:
        """Customize UPF configuration"""
        # Update subnet if provided
        if 'subnet' in properties and 'upf' in config:
            if 'subnet' in config['upf']:
                config['upf']['subnet'][0]['addr'] = properties['subnet']
                
        return config
    
    def _customize_gnb_config(self, config: Dict[str, Any], properties: Dict[str, Any]) -> Dict[str, Any]:
        """Customize gNB configuration"""
        # Update MCC/MNC
        config['mcc'] = properties.get('mcc', '999')
        config['mnc'] = properties.get('mnc', '70')
        
        # Update gNB ID and TAC
        if 'gnb_id' in properties:
            config['nci'] = hex(properties['gnb_id'])
        if 'tac' in properties:
            config['tac'] = properties['tac']
            
        # Update power settings
        if 'power' in properties:
            if 'cellCfgList' in config and config['cellCfgList']:
                config['cellCfgList'][0]['txPower'] = properties['power']
                
        return config
    
    def _customize_ue_config(self, config: Dict[str, Any], properties: Dict[str, Any]) -> Dict[str, Any]:
        """Customize UE configuration"""
        # Update MCC/MNC
        config['mcc'] = properties.get('mcc', '999')
        config['mnc'] = properties.get('mnc', '70')
        
        # Update IMSI
        if 'imsi' in properties:
            config['supi'] = f"imsi-{properties['imsi']}"
            
        # Update security keys
        if 'key' in properties:
            config['key'] = properties['key']
        if 'op' in properties:
            config['op'] = properties['op']
            
        # Update IMEI
        if 'imei' in properties:
            config['imei'] = properties['imei']
            
        return config
    
    def create_instance_config(self, component_type: str, instance_name: str, 
                             properties: Optional[Dict[str, Any]] = None) -> str:
        """Create and save a configuration file for a specific component instance"""
        try:
            # Create instance-specific directory
            instance_dir = os.path.join(self.instance_configs_dir, instance_name)
            os.makedirs(instance_dir, exist_ok=True)
            
            # Customize configuration
            config = self.customize_config(component_type, instance_name, properties)
            
            # Save to instance-specific file
            config_file = os.path.join(instance_dir, f"{component_type}.yaml")
            with open(config_file, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)
                
            print(f"Created instance config: {config_file}")
            return config_file
            
        except Exception as e:
            print(f"Error creating instance config for {instance_name}: {e}")
            return ""
    
    def get_instance_config_dir(self, instance_name: str) -> str:
        """Get the absolute path to an instance's configuration directory"""
        instance_dir = os.path.join(self.instance_configs_dir, instance_name)
        return os.path.abspath(instance_dir)
    
    def cleanup_instance_config(self, instance_name: str):
        """Remove configuration files for a specific instance"""
        try:
            instance_dir = os.path.join(self.instance_configs_dir, instance_name)
            if os.path.exists(instance_dir):
                shutil.rmtree(instance_dir)
                print(f"Cleaned up config for instance: {instance_name}")
        except Exception as e:
            print(f"Error cleaning up config for {instance_name}: {e}")
    
    def list_available_templates(self) -> Dict[str, list]:
        """List all available configuration templates"""
        templates = {
            'open5gs': [],
            'ueransim': []
        }
        
        # Check Open5GS templates
        if os.path.exists(self.open5gs_templates_dir):
            for file in os.listdir(self.open5gs_templates_dir):
                if file.endswith('.yaml'):
                    templates['open5gs'].append(file.replace('.yaml', ''))
                    
        # Check UERANSIM templates
        if os.path.exists(self.ueransim_templates_dir):
            for file in os.listdir(self.ueransim_templates_dir):
                if file.endswith('.yaml'):
                    templates['ueransim'].append(file.replace('.yaml', ''))
                    
        return templates
    
    def validate_config(self, config_file: str) -> bool:
        """Validate a YAML configuration file"""
        try:
            with open(config_file, 'r') as f:
                yaml.safe_load(f)
            print(f"Configuration file is valid: {config_file}")
            return True
        except Exception as e:
            print(f"Invalid configuration file {config_file}: {e}")
            return False


def test_config_manager():
    """Test the configuration manager functionality"""
    print("Testing NetFlux5G Configuration Manager...")
    
    config_mgr = ConfigManager()
    
    # Test listing templates
    templates = config_mgr.list_available_templates()
    print(f"Available templates: {templates}")
    
    # Test loading a template
    nrf_config = config_mgr.load_template_config('nrf')
    print(f"NRF template loaded: {bool(nrf_config)}")
    
    # Test creating an instance config
    gnb_properties = {
        'mcc': '999',
        'mnc': '70', 
        'gnb_id': 1,
        'tac': 1,
        'power': 23
    }
    
    config_file = config_mgr.create_instance_config('gnb', 'gnb-test', gnb_properties)
    print(f"Created gNB instance config: {config_file}")
    
    # Test validation
    if config_file:
        is_valid = config_mgr.validate_config(config_file)
        print(f"Config validation: {is_valid}")


if __name__ == "__main__":
    test_config_manager()
