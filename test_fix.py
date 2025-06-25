#!/usr/bin/env python3
"""
Test script to verify the NetFlux5G fixes
"""

import sys
import os
import subprocess
import logging

def main():
    print("🔧 NetFlux5G Fix Test")
    print("=" * 30)
    
    # Test 1: Check if the fixed executable paths are correct
    print("\n1. Testing UERANSIM executable paths...")
    try:
        result = subprocess.run([
            "docker", "run", "--rm", "towards5gs/ueransim-ue:v3.2.3", 
            "find", "/ueransim/build", "-name", "*nr-ue*"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and "/ueransim/build/nr-ue" in result.stdout:
            print("✅ UE executable path is correct: /ueransim/build/nr-ue")
        else:
            print("❌ UE executable path not found")
            print(f"Output: {result.stdout}")
    except Exception as e:
        print(f"❌ Error testing UE path: {e}")
    
    # Test 2: Check if Alpine image is available for router
    print("\n2. Testing router image availability...")
    try:
        result = subprocess.run([
            "docker", "run", "--rm", "alpine:latest", 
            "echo", "Router image works"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Alpine image for router is available")
        else:
            print("❌ Alpine image not available")
    except Exception as e:
        print(f"❌ Error testing router image: {e}")
    
    # Test 3: Check if the container manager module can be imported
    print("\n3. Testing container manager import...")
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        from simulation.enhanced_container_manager import EnhancedContainerManager
        print("✅ Container manager can be imported")
        
        # Test if cleanup_containers method exists
        manager = EnhancedContainerManager()
        if hasattr(manager, 'cleanup_containers'):
            print("✅ cleanup_containers method exists")
        else:
            print("❌ cleanup_containers method missing")
            
        if hasattr(manager, 'deploy_router_component'):
            print("✅ deploy_router_component method exists")
        else:
            print("❌ deploy_router_component method missing")
            
    except Exception as e:
        print(f"❌ Error importing container manager: {e}")
    
    print("\n" + "=" * 30)
    print("Test completed. You can now try running NetFlux5G again.")

if __name__ == "__main__":
    main()
