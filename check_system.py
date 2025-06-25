#!/usr/bin/env python3
"""
NetFlux5G System Requirements Checker
Checks system resources and provides recommendations for running NetFlux5G.
"""

import subprocess
import sys
import os
import platform
import psutil

def get_system_info():
    """Get basic system information"""
    info = {
        'os': platform.system(),
        'os_version': platform.version(),
        'architecture': platform.machine(),
        'cpu_count': psutil.cpu_count(),
        'memory_gb': round(psutil.virtual_memory().total / (1024**3), 1),
        'available_memory_gb': round(psutil.virtual_memory().available / (1024**3), 1),
        'disk_free_gb': round(psutil.disk_usage('/').free / (1024**3), 1) if os.name != 'nt' else round(psutil.disk_usage('C:').free / (1024**3), 1)
    }
    return info

def check_docker_resources():
    """Check Docker resource allocation"""
    try:
        # Get Docker system info
        result = subprocess.run(['docker', 'system', 'info'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return True, result.stdout
        else:
            return False, "Could not get Docker system info"
    except:
        return False, "Docker not available"

def check_requirements():
    """Check if system meets requirements"""
    info = get_system_info()
    
    print("🖥️  System Information")
    print("======================")
    print(f"OS: {info['os']} {info['os_version']}")
    print(f"Architecture: {info['architecture']}")
    print(f"CPU Cores: {info['cpu_count']}")
    print(f"Total Memory: {info['memory_gb']} GB")
    print(f"Available Memory: {info['available_memory_gb']} GB")
    print(f"Free Disk Space: {info['disk_free_gb']} GB")
    
    print("\n📋 Requirements Check")
    print("=====================")
    
    # Check memory
    if info['memory_gb'] >= 8:
        print("✅ Memory: Sufficient (>= 8 GB recommended)")
    elif info['memory_gb'] >= 4:
        print("⚠️ Memory: Minimal (4-8 GB, may experience slowdowns)")
    else:
        print("❌ Memory: Insufficient (< 4 GB, not recommended)")
    
    # Check available memory
    if info['available_memory_gb'] >= 3:
        print("✅ Available Memory: Good (>= 3 GB)")
    elif info['available_memory_gb'] >= 2:
        print("⚠️ Available Memory: Minimal (2-3 GB)")
    else:
        print("❌ Available Memory: Low (< 2 GB, may cause issues)")
    
    # Check disk space
    if info['disk_free_gb'] >= 10:
        print("✅ Disk Space: Sufficient (>= 10 GB recommended)")
    elif info['disk_free_gb'] >= 5:
        print("⚠️ Disk Space: Minimal (5-10 GB)")
    else:
        print("❌ Disk Space: Low (< 5 GB, not enough for Docker images)")
    
    # Check CPU
    if info['cpu_count'] >= 4:
        print("✅ CPU Cores: Good (>= 4 cores)")
    elif info['cpu_count'] >= 2:
        print("⚠️ CPU Cores: Minimal (2-4 cores)")
    else:
        print("❌ CPU Cores: Insufficient (< 2 cores)")
    
    print("\n🐳 Docker Information")
    print("====================")
    
    docker_ok, docker_info = check_docker_resources()
    if docker_ok:
        print("✅ Docker is running")
        
        # Parse some useful info from docker system info
        lines = docker_info.split('\n')
        for line in lines:
            if 'Total Memory:' in line:
                print(f"Docker Memory: {line.split(':')[1].strip()}")
            elif 'CPUs:' in line:
                print(f"Docker CPUs: {line.split(':')[1].strip()}")
    else:
        print(f"❌ Docker issue: {docker_info}")
    
    print("\n💡 Recommendations")
    print("==================")
    
    if info['memory_gb'] < 8:
        print("• Close unnecessary applications to free up memory")
        print("• Consider upgrading to at least 8 GB RAM")
    
    if info['available_memory_gb'] < 3:
        print("• Free up memory by closing applications")
        print("• Restart your system if memory usage is high")
    
    if info['disk_free_gb'] < 10:
        print("• Free up disk space (Docker images require ~2-3 GB)")
        print("• Clean up old Docker images: docker system prune")
    
    if info['cpu_count'] < 4:
        print("• Performance may be slower with fewer CPU cores")
        print("• Consider running simpler network topologies")
    
    print("\n🔧 Performance Tips")
    print("===================")
    print("• Close web browsers and other memory-intensive applications")
    print("• Ensure Docker Desktop has adequate resource allocation")
    print("• Use wired internet connection for faster image downloads")
    print("• Run the environment preparation script before starting NetFlux5G")
    
    return info

def main():
    """Main function"""
    print("🔍 NetFlux5G System Requirements Checker")
    print("========================================\n")
    
    try:
        check_requirements()
    except Exception as e:
        print(f"Error checking system requirements: {e}")
        sys.exit(1)
    
    print("\n🚀 Next Steps")
    print("=============")
    print("1. Run: python3 prepare_environment.py")
    print("2. Run: ./netflux5g.sh")

if __name__ == "__main__":
    main()
