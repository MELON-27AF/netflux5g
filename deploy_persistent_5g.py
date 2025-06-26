#!/usr/bin/env python3
"""
NetFlux5G - Persistent 5G Core Deployment for Debugging
This script deploys the 5G core and keeps it running for manual testing
"""

import sys
import os
import time
import logging

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from simulation.enhanced_container_manager import EnhancedContainerManager
except ImportError:
    # Fallback - import directly
    sys.path.append('src')
    from simulation.enhanced_container_manager import EnhancedContainerManager

def deploy_persistent_5g():
    """Deploy 5G core network and keep it running for debugging"""
    print("🚀 NetFlux5G - Persistent 5G Core Deployment")
    print("=" * 60)
    
    # Initialize container manager
    container_manager = EnhancedContainerManager()
    
    if not container_manager.client:
        print("❌ Docker client not available. Please ensure Docker is running.")
        return False
    
    try:
        # Create mock components for testing
        class MockComponent:
            def __init__(self, comp_type, name):
                self.component_type = comp_type
                self.properties = {"name": name}
                self.component_id = f"{comp_type}_test"
        
        # Create test components
        test_components = [
            MockComponent("nrf", "nrf-test"),
            MockComponent("amf", "amf-test"),
            MockComponent("smf", "smf-test"),
            MockComponent("upf", "upf-test"),
            MockComponent("gnb", "gnb-test"),
            MockComponent("ue", "ue-test")
        ]
        
        print(f"📦 Created {len(test_components)} test components")
        
        # Deploy the 5G core
        print("🚀 Deploying 5G core network...")
        success, message = container_manager.deploy_5g_core(test_components)
        
        if not success:
            print(f"❌ Deployment failed: {message}")
            return False
        
        print(f"✅ Deployment successful: {message}")
        
        # Wait for services to start
        print("⏳ Waiting for services to start (30 seconds)...")
        time.sleep(30)
        
        print("\n📋 Container Status:")
        print("-" * 40)
        
        # Show container status
        for container in container_manager.deployed_containers:
            try:
                container.reload()  # Refresh container info
                print(f"   {container.name}: {container.status}")
                
                # Get container IP
                network_settings = container.attrs.get('NetworkSettings', {})
                networks = network_settings.get('Networks', {})
                for net_name, net_info in networks.items():
                    if 'netflux5g' in net_name:
                        ip = net_info.get('IPAddress', 'unknown')
                        print(f"      IP: {ip}")
                        break
                        
            except Exception as e:
                print(f"   {container.name}: Error - {e}")
        
        print(f"\n🎯 5G Core network is running!")
        print(f"📋 Run 'python3 debug_containers.py' to check logs")
        print(f"🧪 Run 'docker exec -it ue-test sh' to access UE container")
        print(f"🛑 Run 'docker stop $(docker ps -q --filter network=netflux5g_network)' to stop all")
        print(f"🧹 Run 'docker container prune -f && docker network prune -f' to cleanup")
        
        print("\n⚠️  Containers will keep running until manually stopped!")
        print("Press Ctrl+C to exit this script (containers will continue running)")
        
        # Keep script running
        try:
            while True:
                time.sleep(60)
                print("💓 5G Core still running... (Press Ctrl+C to exit)")
        except KeyboardInterrupt:
            print("\n👋 Exiting deployment script (containers still running)")
            return True
            
    except Exception as e:
        print(f"❌ Deployment error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    deploy_persistent_5g()
