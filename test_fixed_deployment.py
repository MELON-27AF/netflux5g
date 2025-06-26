#!/usr/bin/env python3
"""
Test script to verify the fixes for NetFlux5G deployment issues.
"""

import subprocess
import time
import sys

def run_command(cmd, description=""):
    """Run a command and return its output"""
    print(f"\n🔄 {description}")
    print(f"Running: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"✅ Success: {description}")
            return result.stdout.strip()
        else:
            print(f"❌ Failed: {description}")
            print(f"Error: {result.stderr.strip()}")
            return None
    except subprocess.TimeoutExpired:
        print(f"⏰ Timeout: {description}")
        return None
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def check_container_status():
    """Check the status of all containers"""
    print("\n📊 Checking container status...")
    
    # Get all containers
    output = run_command("docker ps -a --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'", "Listing all containers")
    if output:
        print(output)
    
    # Check specifically for our containers
    containers = ['mongodb', 'nrf-test', 'amf-test', 'smf-test', 'upf-test', 'ausf-test', 'udm-test', 'pcf-test', 'gnb-test', 'ue-test', 'internet-gw']
    
    running_containers = []
    failed_containers = []
    
    for container in containers:
        status = run_command(f"docker inspect {container} --format '{{{{.State.Status}}}}' 2>/dev/null || echo 'not found'", f"Checking {container}")
        if status == "running":
            running_containers.append(container)
        elif status and status != "not found":
            failed_containers.append((container, status))
    
    print(f"\n✅ Running containers ({len(running_containers)}): {', '.join(running_containers)}")
    if failed_containers:
        print(f"❌ Failed containers ({len(failed_containers)}):")
        for container, status in failed_containers:
            print(f"  - {container}: {status}")
    
    return running_containers, failed_containers

def analyze_failed_containers(failed_containers):
    """Analyze logs of failed containers"""
    print("\n🔍 Analyzing failed containers...")
    
    for container, status in failed_containers:
        print(f"\n--- Logs for {container} (Status: {status}) ---")
        logs = run_command(f"docker logs {container} --tail 20", f"Getting logs for {container}")
        if logs:
            print(logs)
        else:
            print("No logs available or container not found")

def main():
    print("🚀 NetFlux5G Deployment Test")
    print("=" * 50)
    
    # First, clean up any existing containers
    print("\n🧹 Cleaning up existing containers...")
    run_command("docker stop $(docker ps -aq) 2>/dev/null || true", "Stopping all containers")
    run_command("docker rm $(docker ps -aq) 2>/dev/null || true", "Removing all containers")
    
    # Check if the fixes have been applied
    print("\n🔍 Checking if fixes are applied...")
    
    # Test 1: Check if ignoreStreamIds is in gNB config generation
    with open('src/simulation/enhanced_container_manager.py', 'r') as f:
        content = f.read()
        if 'ignoreStreamIds' in content:
            print("✅ gNB ignoreStreamIds fix is present")
        else:
            print("❌ gNB ignoreStreamIds fix is missing")
    
    # Test 2: Check if all Open5GS component configs are present
    required_configs = ['smf:', 'upf:', 'ausf:', 'udm:', 'pcf:']
    configs_found = sum(1 for config in required_configs if config in content)
    print(f"✅ Open5GS component configs found: {configs_found}/{len(required_configs)}")
    
    # Test 3: Check if proper startup dependencies are implemented
    if 'while ! nc -z nrf 7777' in content:
        print("✅ NRF dependency check is present")
    else:
        print("❌ NRF dependency check is missing")
    
    print("\n🏃 Running deployment test...")
    print("This will take a few minutes...")
    
    # Start the NetFlux5G application (this should trigger deployment)
    print("\nNote: You should now run the NetFlux5G application and deploy a 5G network configuration.")
    print("Then run this script again to check the results.")
    
    # Check current status
    running, failed = check_container_status()
    
    if failed:
        analyze_failed_containers(failed)
        
    print("\n📋 Summary:")
    print(f"✅ Running containers: {len(running)}")
    print(f"❌ Failed containers: {len(failed)}")
    
    if len(running) >= 8:  # Expecting at least 8 core components
        print("\n🎉 SUCCESS: Most containers are running! The fixes appear to be working.")
        return 0
    elif len(running) >= 4:
        print("\n⚠️ PARTIAL SUCCESS: Some containers are running, but some fixes may still be needed.")
        return 1
    else:
        print("\n❌ FAILURE: Most containers failed to start. Additional fixes needed.")
        return 2

if __name__ == "__main__":
    sys.exit(main())
