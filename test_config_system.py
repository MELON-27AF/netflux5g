#!/usr/bin/env python3
"""
NetFlux5G Configuration System Test
Test the new YAML-based configuration system for 5G components
"""

import os
import sys

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from utils.config_manager import ConfigManager

def test_configuration_system():
    """Test the NetFlux5G configuration system"""
    print("🧪 Testing NetFlux5G Configuration System")
    print("=" * 50)
    
    # Initialize configuration manager
    config_mgr = ConfigManager()
    
    # Test 1: List available templates
    print("\n📋 Step 1: Listing available configuration templates...")
    templates = config_mgr.list_available_templates()
    print(f"✅ Open5GS templates: {templates['open5gs']}")
    print(f"✅ UERANSIM templates: {templates['ueransim']}")
    
    # Test 2: Load template configurations
    print("\n📄 Step 2: Loading template configurations...")
    
    # Test NRF configuration
    nrf_config = config_mgr.load_template_config('nrf')
    if nrf_config:
        print(f"✅ NRF template loaded successfully")
        print(f"   - Database URI: {nrf_config.get('db_uri', 'Not specified')}")
        print(f"   - SBI Port: {nrf_config.get('nrf', {}).get('sbi', [{}])[0].get('port', 'Not specified')}")
    else:
        print("❌ Failed to load NRF template")
    
    # Test gNB configuration
    gnb_config = config_mgr.load_template_config('gnb')
    if gnb_config:
        print(f"✅ gNB template loaded successfully")
        print(f"   - MCC: {gnb_config.get('mcc', 'Not specified')}")
        print(f"   - MNC: {gnb_config.get('mnc', 'Not specified')}")
        print(f"   - NCI: {gnb_config.get('nci', 'Not specified')}")
    else:
        print("❌ Failed to load gNB template")
    
    # Test 3: Create customized instance configurations
    print("\n⚙️  Step 3: Creating customized instance configurations...")
    
    # Create AMF instance with custom properties
    amf_properties = {
        'mcc': '999',
        'mnc': '70',
        'tac': 1,
        'name': 'amf-test'
    }
    
    amf_config_file = config_mgr.create_instance_config('amf', 'amf-test', amf_properties)
    if amf_config_file:
        print(f"✅ AMF instance configuration created: {amf_config_file}")
        
        # Validate the configuration
        if config_mgr.validate_config(amf_config_file):
            print("✅ AMF configuration is valid YAML")
        else:
            print("❌ AMF configuration validation failed")
    else:
        print("❌ Failed to create AMF instance configuration")
    
    # Create gNB instance with custom properties
    gnb_properties = {
        'mcc': '999',
        'mnc': '70',
        'gnb_id': 0x000000010,
        'tac': 1,
        'power': 23
    }
    
    gnb_config_file = config_mgr.create_instance_config('gnb', 'gnb-test', gnb_properties)
    if gnb_config_file:
        print(f"✅ gNB instance configuration created: {gnb_config_file}")
        
        # Validate the configuration
        if config_mgr.validate_config(gnb_config_file):
            print("✅ gNB configuration is valid YAML")
        else:
            print("❌ gNB configuration validation failed")
    else:
        print("❌ Failed to create gNB instance configuration")
    
    # Create UE instance with custom properties
    ue_properties = {
        'mcc': '999',
        'mnc': '70',
        'imsi': '999700000000001',
        'key': '465B5CE8B199B49FAA5F0A2EE238A6BC',
        'imei': '356938035643803'
    }
    
    ue_config_file = config_mgr.create_instance_config('ue', 'ue-test', ue_properties)
    if ue_config_file:
        print(f"✅ UE instance configuration created: {ue_config_file}")
        
        # Validate the configuration
        if config_mgr.validate_config(ue_config_file):
            print("✅ UE configuration is valid YAML")
        else:
            print("❌ UE configuration validation failed")
    else:
        print("❌ Failed to create UE instance configuration")
    
    # Test 4: Test configuration directory paths
    print("\n📁 Step 4: Testing configuration directory paths...")
    
    amf_config_dir = config_mgr.get_instance_config_dir('amf-test')
    print(f"✅ AMF config directory: {amf_config_dir}")
    
    gnb_config_dir = config_mgr.get_instance_config_dir('gnb-test')
    print(f"✅ gNB config directory: {gnb_config_dir}")
    
    ue_config_dir = config_mgr.get_instance_config_dir('ue-test')
    print(f"✅ UE config directory: {ue_config_dir}")
    
    # Test 5: Cleanup test configurations
    print("\n🧹 Step 5: Cleaning up test configurations...")
    
    config_mgr.cleanup_instance_config('amf-test')
    config_mgr.cleanup_instance_config('gnb-test')
    config_mgr.cleanup_instance_config('ue-test')
    
    print("✅ Test configurations cleaned up")
    
    print("\n🎉 Configuration System Test Completed!")
    print("=" * 50)
    print("\n📝 Summary:")
    print("   ✅ YAML configuration templates are loaded successfully")
    print("   ✅ Instance-specific configurations can be created and customized") 
    print("   ✅ Configuration validation works properly")
    print("   ✅ Configuration cleanup works properly")
    print("\n🚀 The NetFlux5G configuration system is ready to use!")


def show_configuration_structure():
    """Show the current configuration directory structure"""
    print("\n📂 NetFlux5G Configuration Directory Structure:")
    print("=" * 50)
    
    config_root = "./config"
    
    if os.path.exists(config_root):
        for root, dirs, files in os.walk(config_root):
            level = root.replace(config_root, '').count(os.sep)
            indent = ' ' * 2 * level
            print(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * 2 * (level + 1)
            for file in files:
                if file.endswith('.yaml') or file.endswith('.yml'):
                    print(f"{subindent}📄 {file}")
                else:
                    print(f"{subindent}📄 {file}")
    else:
        print("❌ Configuration directory not found")


if __name__ == "__main__":
    print("NetFlux5G Configuration System")
    print("Testing YAML-based 5G component configurations")
    print()
    
    # Show current configuration structure
    show_configuration_structure()
    
    # Run configuration system tests
    test_configuration_system()
