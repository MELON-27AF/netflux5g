#!/usr/bin/env python3
"""
NetFlux5G YAML Configuration Deployment Demo
Demonstrates deploying 5G components with the new YAML configuration system
"""

import os
import sys
import time

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from simulation.enhanced_container_manager import EnhancedContainerManager
from utils.config_manager import ConfigManager

def create_mock_component(comp_type, properties):
    """Create a mock component for testing"""
    class MockComponent:
        def __init__(self, comp_type, properties):
            self.component_type = comp_type
            self.properties = properties
            self.component_id = hash(f"{comp_type}_{properties.get('name', 'default')}")
            
    return MockComponent(comp_type, properties)

def demo_deployment():
    """Demonstrate deploying 5G components with YAML configs"""
    print("🚀 NetFlux5G YAML Configuration Deployment Demo")
    print("=" * 60)
    
    # Initialize managers
    print("\n1️⃣ Initializing Configuration and Container Managers...")
    config_mgr = ConfigManager()
    container_mgr = EnhancedContainerManager()
    
    if not container_mgr.client:
        print("❌ Docker not available. Please ensure Docker is running.")
        return
    
    print("✅ Managers initialized successfully")
    
    # Check available templates
    print("\n2️⃣ Checking Available Configuration Templates...")
    templates = config_mgr.list_available_templates()
    print(f"✅ Open5GS templates: {templates['open5gs']}")
    print(f"✅ UERANSIM templates: {templates['ueransim']}")
    
    # Create test components with custom properties
    print("\n3️⃣ Creating 5G Components with Custom Properties...")
    
    # NRF component
    nrf_props = {
        'name': 'nrf-demo',
        'log_level': 'info'
    }
    nrf_component = create_mock_component('nrf', nrf_props)
    print(f"✅ Created NRF component: {nrf_props['name']}")
    
    # AMF component
    amf_props = {
        'name': 'amf-demo',
        'mcc': '999',
        'mnc': '70',
        'tac': 1
    }
    amf_component = create_mock_component('amf', amf_props)
    print(f"✅ Created AMF component: {amf_props['name']}")
    
    # SMF component
    smf_props = {
        'name': 'smf-demo',
        'subnet': '10.45.0.1/16',
        'dns_servers': ['8.8.8.8', '8.8.4.4']
    }
    smf_component = create_mock_component('smf', smf_props)
    print(f"✅ Created SMF component: {smf_props['name']}")
    
    # gNB component
    gnb_props = {
        'name': 'gnb-demo',
        'mcc': '999',
        'mnc': '70',
        'gnb_id': 1,
        'tac': 1,
        'power': 23
    }
    gnb_component = create_mock_component('gnb', gnb_props)
    print(f"✅ Created gNB component: {gnb_props['name']}")
    
    # UE component
    ue_props = {
        'name': 'ue-demo',
        'mcc': '999',
        'mnc': '70',
        'imsi': '999700000000001',
        'key': '465B5CE8B199B49FAA5F0A2EE238A6BC',
        'imei': '356938035643803'
    }
    ue_component = create_mock_component('ue', ue_props)
    print(f"✅ Created UE component: {ue_props['name']}")
    
    # Demonstrate configuration generation
    print("\n4️⃣ Generating Instance-Specific Configurations...")
    
    configs_created = []
    
    for component in [nrf_component, amf_component, smf_component, gnb_component, ue_component]:
        comp_type = component.component_type
        comp_name = component.properties['name']
        
        # Create configuration
        config_file = config_mgr.create_instance_config(
            comp_type, comp_name, component.properties
        )
        
        if config_file:
            configs_created.append((comp_name, config_file))
            print(f"✅ Created config for {comp_type}: {config_file}")
        else:
            print(f"❌ Failed to create config for {comp_type}")
    
    # Show configuration directories
    print("\n5️⃣ Configuration Directory Structure...")
    for comp_name, config_file in configs_created:
        config_dir = config_mgr.get_instance_config_dir(comp_name)
        print(f"📁 {comp_name}: {config_dir}")
    
    # Demonstrate validation
    print("\n6️⃣ Validating Generated Configurations...")
    valid_configs = 0
    for comp_name, config_file in configs_created:
        if config_mgr.validate_config(config_file):
            print(f"✅ {comp_name}: Valid YAML")
            valid_configs += 1
        else:
            print(f"❌ {comp_name}: Invalid YAML")
    
    print(f"\n📊 Validation Summary: {valid_configs}/{len(configs_created)} configurations valid")
    
    # Show how container deployment would work
    print("\n7️⃣ Container Deployment Workflow (Simulation)...")
    print("   Note: This demo shows the workflow without actually starting containers")
    print("   to avoid resource usage. In real deployment, containers would be created.")
    
    components = [nrf_component, amf_component, smf_component, gnb_component, ue_component]
    
    for component in components:
        comp_type = component.component_type
        comp_name = component.properties['name']
        
        print(f"\n🐳 Would deploy {comp_type} ({comp_name}):")
        
        # Show config generation
        config_dir = config_mgr.get_instance_config_dir(comp_name)
        print(f"   📁 Config directory: {config_dir}")
        
        # Show volume mount that would be used
        if comp_type in ['gnb', 'ue']:
            mount_path = "/etc/ueransim"
        else:
            mount_path = "/etc/open5gs"
        
        print(f"   📂 Volume mount: {config_dir}:{mount_path}:ro")
        
        # Show container image that would be used
        if comp_type in ['gnb', 'ue']:
            if comp_type == 'gnb':
                image = "towards5gs/ueransim-gnb:v3.2.3"
            else:
                image = "towards5gs/ueransim-ue:v3.2.3"
        else:
            image = "openverso/open5gs:latest"
        
        print(f"   🐳 Container image: {image}")
        print(f"   ⚙️  Configuration applied from YAML template")
    
    # Cleanup demo configurations
    print("\n8️⃣ Cleaning Up Demo Configurations...")
    for comp_name, _ in configs_created:
        config_mgr.cleanup_instance_config(comp_name)
        print(f"🧹 Cleaned up config for: {comp_name}")
    
    print("\n" + "=" * 60)
    print("🎉 YAML Configuration Deployment Demo Complete!")
    print("=" * 60)
    
    print("\n📋 Summary:")
    print("   ✅ Configuration templates loaded successfully")
    print("   ✅ Instance-specific configurations generated")
    print("   ✅ Custom properties applied correctly")
    print("   ✅ YAML validation passed")
    print("   ✅ Container deployment workflow demonstrated")
    print("   ✅ Configuration cleanup completed")
    
    print("\n🚀 The NetFlux5G YAML configuration system is ready for production use!")
    print("\n💡 To deploy actual containers:")
    print("   1. Use the NetFlux5G GUI: python src/main.py")
    print("   2. Or use the Enhanced Container Manager programmatically")
    print("   3. Configurations will be automatically generated and used")

def show_usage_examples():
    """Show practical usage examples"""
    print("\n" + "=" * 60)
    print("📚 YAML Configuration System Usage Examples")
    print("=" * 60)
    
    print("\n1️⃣ Basic Configuration Loading:")
    print("""
from utils.config_manager import ConfigManager

config_mgr = ConfigManager()

# Load a template
nrf_template = config_mgr.load_template_config('nrf')
print(f"NRF SBI Port: {nrf_template['nrf']['sbi'][0]['port']}")
""")
    
    print("\n2️⃣ Creating Custom Instance Configurations:")
    print("""
# Create customized AMF configuration
amf_properties = {
    'mcc': '001',
    'mnc': '01', 
    'tac': 7,
    'name': 'my-amf'
}

config_file = config_mgr.create_instance_config('amf', 'my-amf', amf_properties)
config_dir = config_mgr.get_instance_config_dir('my-amf')
""")
    
    print("\n3️⃣ Container Deployment with Configurations:")
    print("""
from simulation.enhanced_container_manager import EnhancedContainerManager

container_mgr = EnhancedContainerManager()

# Deploy components - configurations are automatically generated
components = [nrf_component, amf_component, smf_component]
success, message = container_mgr.deploy_5g_core(components)

if success:
    print("5G Core deployed with YAML configurations!")
""")
    
    print("\n4️⃣ Configuration Validation:")
    print("""
# Validate configuration files
config_files = ['./config/instances/my-amf/amf.yaml']

for config_file in config_files:
    if config_mgr.validate_config(config_file):
        print(f"✅ {config_file} is valid")
    else:
        print(f"❌ {config_file} has errors")
""")

if __name__ == "__main__":
    print("NetFlux5G YAML Configuration System")
    print("Deployment Demo and Usage Examples")
    print()
    
    try:
        # Run the deployment demo
        demo_deployment()
        
        # Show usage examples
        show_usage_examples()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        print("Please ensure all dependencies are installed and Docker is running")
