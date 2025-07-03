#!/usr/bin/env python3
"""
NetFlux5G Production Health Check Script
This script performs various health checks for a production NetFlux5G deployment.
"""

import os
import sys
import subprocess
import json
import time
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('health_check.log'),
        logging.StreamHandler()
    ]
)

class NetFlux5GHealthCheck:
    def __init__(self):
        self.checks = []
        self.failed_checks = []
        
    def add_check(self, name, func):
        """Add a health check function"""
        self.checks.append((name, func))
    
    def run_check(self, name, func):
        """Run a single health check"""
        try:
            logging.info(f"Running check: {name}")
            result = func()
            if result:
                logging.info(f"✅ {name}: PASSED")
                return True
            else:
                logging.error(f"❌ {name}: FAILED")
                self.failed_checks.append(name)
                return False
        except Exception as e:
            logging.error(f"❌ {name}: ERROR - {str(e)}")
            self.failed_checks.append(name)
            return False
    
    def check_docker_running(self):
        """Check if Docker is running"""
        try:
            result = subprocess.run(['docker', 'info'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except:
            return False
    
    def check_docker_images(self):
        """Check if required Docker images are available"""
        required_images = [
            'openverso/open5gs:latest',
            'openverso/ueransim:latest',
            'mongo:4.4'
        ]
        
        try:
            result = subprocess.run(['docker', 'images', '--format', 'json'], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                return False
            
            available_images = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    image_info = json.loads(line)
                    repo_tag = f"{image_info['Repository']}:{image_info['Tag']}"
                    available_images.append(repo_tag)
            
            missing_images = []
            for required in required_images:
                if required not in available_images:
                    missing_images.append(required)
            
            if missing_images:
                logging.warning(f"Missing images: {missing_images}")
                return False
            
            return True
        except:
            return False
    
    def check_python_dependencies(self):
        """Check if Python dependencies are installed"""
        required_packages = [
            'PyQt5', 'docker', 'PyYAML', 'requests', 'psutil',
            'matplotlib', 'numpy'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package.lower().replace('pyqt5', 'PyQt5'))
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            logging.warning(f"Missing Python packages: {missing_packages}")
            return False
        
        return True
    
    def check_config_files(self):
        """Check if configuration files exist and are readable"""
        config_files = [
            'config/open5gs/amf.yaml',
            'config/open5gs/smf.yaml',
            'config/open5gs/upf.yaml',
            'config/ueransim/gnb.yaml',
            'config/ueransim/ue.yaml'
        ]
        
        missing_files = []
        for config_file in config_files:
            if not os.path.exists(config_file):
                missing_files.append(config_file)
            elif not os.access(config_file, os.R_OK):
                missing_files.append(f"{config_file} (not readable)")
        
        if missing_files:
            logging.warning(f"Missing/unreadable config files: {missing_files}")
            return False
        
        return True
    
    def check_docker_network(self):
        """Check if Docker network is properly configured"""
        try:
            result = subprocess.run(['docker', 'network', 'ls', '--format', 'json'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                return False
            
            networks = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    network_info = json.loads(line)
                    networks.append(network_info['Name'])
            
            # Check if bridge network exists (default Docker network)
            return 'bridge' in networks
        except:
            return False
    
    def check_disk_space(self):
        """Check available disk space"""
        try:
            import shutil
            total, used, free = shutil.disk_usage('.')
            free_gb = free // (1024**3)
            
            # Require at least 5GB free space
            if free_gb < 5:
                logging.warning(f"Low disk space: {free_gb}GB free")
                return False
            
            logging.info(f"Disk space: {free_gb}GB free")
            return True
        except:
            return False
    
    def check_memory_usage(self):
        """Check system memory usage"""
        try:
            import psutil
            memory = psutil.virtual_memory()
            available_gb = memory.available // (1024**3)
            
            # Require at least 2GB available memory
            if available_gb < 2:
                logging.warning(f"Low memory: {available_gb}GB available")
                return False
            
            logging.info(f"Memory: {available_gb}GB available")
            return True
        except:
            return False
    
    def check_running_containers(self):
        """Check for any running NetFlux5G containers"""
        try:
            result = subprocess.run(['docker', 'ps', '--filter', 'name=netflux', '--format', 'json'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                return True  # No containers is OK
            
            containers = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    container_info = json.loads(line)
                    containers.append(container_info['Names'])
            
            if containers:
                logging.info(f"Running containers: {containers}")
            
            return True
        except:
            return False
    
    def run_all_checks(self):
        """Run all health checks"""
        self.add_check("Docker Running", self.check_docker_running)
        self.add_check("Docker Images", self.check_docker_images)
        self.add_check("Python Dependencies", self.check_python_dependencies)
        self.add_check("Configuration Files", self.check_config_files)
        self.add_check("Docker Network", self.check_docker_network)
        self.add_check("Disk Space", self.check_disk_space)
        self.add_check("Memory Usage", self.check_memory_usage)
        self.add_check("Running Containers", self.check_running_containers)
        
        logging.info("="*50)
        logging.info("NetFlux5G Production Health Check")
        logging.info(f"Timestamp: {datetime.now()}")
        logging.info("="*50)
        
        passed = 0
        total = len(self.checks)
        
        for name, func in self.checks:
            if self.run_check(name, func):
                passed += 1
        
        logging.info("="*50)
        logging.info(f"Health Check Summary: {passed}/{total} checks passed")
        
        if self.failed_checks:
            logging.error(f"Failed checks: {self.failed_checks}")
            logging.error("❌ System is NOT ready for production")
            return False
        else:
            logging.info("✅ System is ready for production")
            return True

def main():
    """Main function"""
    health_checker = NetFlux5GHealthCheck()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--json':
        # JSON output for automated monitoring
        result = health_checker.run_all_checks()
        output = {
            'timestamp': datetime.now().isoformat(),
            'status': 'healthy' if result else 'unhealthy',
            'passed_checks': len(health_checker.checks) - len(health_checker.failed_checks),
            'total_checks': len(health_checker.checks),
            'failed_checks': health_checker.failed_checks
        }
        print(json.dumps(output, indent=2))
    else:
        # Human-readable output
        result = health_checker.run_all_checks()
    
    sys.exit(0 if result else 1)

if __name__ == "__main__":
    main()
