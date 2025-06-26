#!/usr/bin/env python3
"""
Debug script to check container logs and diagnose 5G connectivity issues
"""
import docker
import time

def check_container_logs():
    """Check logs of running containers to diagnose issues"""
    try:
        client = docker.from_env()
        
        # Container names to check
        container_names = [
            'mongodb', 'internet-gw', 'nrf-test', 'amf-test', 
            'smf-test', 'upf-test', 'gnb-test', 'ue-test'
        ]
        
        print("🔍 Checking container status and logs...")
        print("=" * 60)
        
        # Get all containers
        containers = client.containers.list(all=True)
        
        for container_name in container_names:
            # Find container
            container = None
            for c in containers:
                if container_name in c.name:
                    container = c
                    break
            
            if container:
                print(f"\n📦 Container: {container.name}")
                print(f"   Status: {container.status}")
                
                if container.status == 'running':
                    # Get recent logs
                    try:
                        logs = container.logs(tail=20).decode('utf-8', errors='ignore')
                        if logs.strip():
                            print(f"   Recent logs:")
                            for line in logs.strip().split('\n')[-10:]:  # Last 10 lines
                                print(f"   > {line}")
                        else:
                            print("   > No recent logs")
                    except Exception as e:
                        print(f"   > Error getting logs: {e}")
                        
                    # Check if it's a 5G component, get some network info
                    if container_name in ['gnb-test', 'ue-test']:
                        try:
                            # Check network interfaces
                            exec_result = container.exec_run("ip addr")
                            if exec_result.exit_code == 0:
                                print(f"   Network interfaces:")
                                output = exec_result.output.decode('utf-8', errors='ignore')
                                for line in output.split('\n'):
                                    if 'inet' in line or 'uesimtun' in line:
                                        print(f"   > {line.strip()}")
                        except Exception as e:
                            print(f"   > Error checking network: {e}")
                else:
                    print(f"   > Container not running")
            else:
                print(f"\n📦 Container: {container_name} - NOT FOUND")
        
        print("\n" + "=" * 60)
        print("🔍 Network status:")
        
        # Check network
        try:
            networks = client.networks.list()
            for net in networks:
                if 'netflux5g' in net.name:
                    print(f"   Network: {net.name}")
                    print(f"   Containers: {len(net.containers)}")
                    for container in net.containers:
                        print(f"   > {container.name}")
        except Exception as e:
            print(f"   Error checking networks: {e}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_container_logs()
