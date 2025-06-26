#!/usr/bin/env python3
"""
NetFlux5G App Integration Test
Test the new YAML configuration system with the actual NetFlux5G application
"""

import os
import sys
import time

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_app_integration():
    """Test integration with NetFlux5G app"""
    print("🧪 Testing NetFlux5G App Integration with YAML Config System")
    print("=" * 65)
    
    # Test 1: Verify configuration system is ready
    print("\n1️⃣ Verifying Configuration System...")
    
    try:
        from utils.config_manager import ConfigManager
        config_mgr = ConfigManager()
        templates = config_mgr.list_available_templates()
        
        print(f"✅ ConfigManager imported successfully")
        print(f"✅ Open5GS templates available: {len(templates['open5gs'])}")
        print(f"✅ UERANSIM templates available: {len(templates['ueransim'])}")
        
    except Exception as e:
        print(f"❌ Configuration system error: {e}")
        return False
    
    # Test 2: Verify Enhanced Container Manager integration
    print("\n2️⃣ Verifying Enhanced Container Manager...")
    
    try:
        from simulation.enhanced_container_manager import EnhancedContainerManager
        container_mgr = EnhancedContainerManager()
        
        if hasattr(container_mgr, 'config_manager'):
            print("✅ ConfigManager integrated with Enhanced Container Manager")
        else:
            print("❌ ConfigManager not integrated")
            return False
            
        if container_mgr.client:
            print("✅ Docker client connected")
        else:
            print("❌ Docker client not available")
            return False
            
    except Exception as e:
        print(f"❌ Container manager error: {e}")
        return False
    
    # Test 3: Create test configurations for app deployment
    print("\n3️⃣ Creating Test Component Configurations...")
    
    test_components = [
        ('nrf', 'nrf-app-test', {'name': 'nrf-app-test'}),
        ('amf', 'amf-app-test', {'name': 'amf-app-test', 'mcc': '999', 'mnc': '70'}),
        ('smf', 'smf-app-test', {'name': 'smf-app-test'}),
        ('gnb', 'gnb-app-test', {'name': 'gnb-app-test', 'mcc': '999', 'mnc': '70'}),
        ('ue', 'ue-app-test', {'name': 'ue-app-test', 'imsi': '999700000000001'})
    ]
    
    configs_created = []
    
    for comp_type, comp_name, properties in test_components:
        try:
            config_file = config_mgr.create_instance_config(comp_type, comp_name, properties)
            if config_file:
                configs_created.append((comp_name, config_file))
                print(f"✅ Created {comp_type} config: {comp_name}")
            else:
                print(f"❌ Failed to create {comp_type} config")
        except Exception as e:
            print(f"❌ Error creating {comp_type} config: {e}")
    
    # Test 4: Verify configurations are valid
    print("\n4️⃣ Validating Generated Configurations...")
    
    valid_count = 0
    for comp_name, config_file in configs_created:
        try:
            if config_mgr.validate_config(config_file):
                print(f"✅ {comp_name}: Valid")
                valid_count += 1
            else:
                print(f"❌ {comp_name}: Invalid")
        except Exception as e:
            print(f"❌ {comp_name}: Validation error - {e}")
    
    print(f"\n📊 Validation Results: {valid_count}/{len(configs_created)} configurations valid")
    
    # Test 5: Show configuration directories for app usage
    print("\n5️⃣ Configuration Directories for App Usage...")
    
    for comp_name, _ in configs_created:
        config_dir = config_mgr.get_instance_config_dir(comp_name)
        print(f"📁 {comp_name}: {config_dir}")
    
    # Cleanup test configurations
    print("\n🧹 Cleaning up test configurations...")
    for comp_name, _ in configs_created:
        config_mgr.cleanup_instance_config(comp_name)
        print(f"🗑️  Cleaned: {comp_name}")
    
    print("\n" + "=" * 65)
    print("🎉 NetFlux5G App Integration Test Complete!")
    print("=" * 65)
    
    if valid_count == len(configs_created) and configs_created:
        print("\n✅ ALL TESTS PASSED - Ready for NetFlux5G GUI testing!")
        return True
    else:
        print("\n❌ Some tests failed - Check configuration system")
        return False

def show_gui_testing_instructions():
    """Show instructions for testing with GUI"""
    print("\n📋 GUI Testing Instructions")
    print("=" * 40)
    
    print("\n🚀 Steps to Test with NetFlux5G GUI:")
    
    print("\n1️⃣ Start NetFlux5G Application:")
    print("   ./netflux5g.sh")
    print("   # or")
    print("   python src/main.py")
    
    print("\n2️⃣ Load or Create 5G Network Topology:")
    print("   • Click 'File' → 'Load Template' → '5g_core_test'")
    print("   • Or create a new topology with 5G components")
    
    print("\n3️⃣ Add 5G Components:")
    print("   • NRF (Network Repository Function)")
    print("   • AMF (Access and Mobility Management Function)")
    print("   • SMF (Session Management Function)")
    print("   • UPF (User Plane Function)")
    print("   • gNB (Next Generation NodeB)")
    print("   • UE (User Equipment)")
    print("   • MongoDB (Database)")
    
    print("\n4️⃣ Configure Component Properties:")
    print("   • Right-click on components to set properties")
    print("   • MCC/MNC, TAC, IMSI, etc.")
    print("   • The new YAML config system will use these properties")
    
    print("\n5️⃣ Run Simulation:")
    print("   • Click 'Run Simulation' button (F5)")
    print("   • Watch the deployment process")
    print("   • New YAML configs will be automatically generated")
    
    print("\n6️⃣ Monitor Deployment:")
    print("   • Check terminal output for config creation messages")
    print("   • Look for: 'Created instance config: ./config/instances/...'")
    print("   • Verify containers start successfully")
    
    print("\n7️⃣ Access Container Terminal:")
    print("   • Use Terminal Dialog to access running containers")
    print("   • Test connectivity between components")
    
    print("\n8️⃣ View Generated Configurations:")
    print("   • Check './config/instances/' directory")
    print("   • Each component will have its own config directory")
    print("   • Configurations are mounted into containers")
    
    print("\n🔍 What to Look For:")
    print("   ✅ Config creation messages during deployment")
    print("   ✅ Successful container startup")
    print("   ✅ Configuration files in './config/instances/'")
    print("   ✅ Volume mounts in container logs")
    
    print("\n🚨 Troubleshooting:")
    print("   • If deployment fails, check Docker is running")
    print("   • Ensure no old containers are blocking network")
    print("   • Check logs for configuration creation errors")
    print("   • Verify YAML files are valid")

if __name__ == "__main__":
    print("NetFlux5G YAML Configuration System")
    print("App Integration Testing")
    print()
    
    # Run integration tests
    success = test_app_integration()
    
    # Show GUI testing instructions
    show_gui_testing_instructions()
    
    if success:
        print("\n🎉 System Ready! You can now test with the NetFlux5G GUI.")
        print("Run: ./netflux5g.sh")
    else:
        print("\n⚠️  Please fix the configuration system issues before GUI testing.")
