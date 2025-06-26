#!/usr/bin/env python3
"""
Quick diagnostic script for NetFlux5G deployment issues.
"""

import subprocess
import sys

def run_cmd(cmd):
    """Run command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except Exception as e:
        return "", str(e), 1

def main():
    print("🔍 NetFlux5G Quick Diagnostics")
    print("=" * 40)
    
    # Check container status
    print("\n📊 Container Status:")
    stdout, _, _ = run_cmd("docker ps -a --format 'table {{.Names}}\t{{.Status}}'")
    if stdout:
        print(stdout)
    
    # Check for failed containers and their main error
    containers = ["gnb-test", "amf-test", "smf-test", "upf-test", "ausf-test", "udm-test", "pcf-test"]
    
    print("\n🚨 Quick Error Analysis:")
    for container in containers:
        stdout, _, rc = run_cmd(f"docker logs {container} --tail 5 2>/dev/null")
        if rc == 0 and stdout:
            # Extract key error information
            lines = stdout.split('\n')
            error_line = None
            for line in lines:
                if any(keyword in line.lower() for keyword in ['error', 'failed', 'fatal', 'aborted']):
                    error_line = line.strip()
                    break
            
            if error_line:
                print(f"❌ {container}: {error_line}")
            else:
                print(f"✅ {container}: No obvious errors in recent logs")
        else:
            print(f"❓ {container}: No logs available")
    
    # Check our fixes
    print("\n🔧 Fix Status:")
    try:
        with open('src/simulation/enhanced_container_manager.py', 'r') as f:
            content = f.read()
            
        fixes = [
            ("gNB ignoreStreamIds", "ignoreStreamIds:" in content),
            ("SMF config", "smf:" in content and "pfcp:" in content),
            ("UPF config", "upf:" in content and "gtpu:" in content),
            ("AUSF config", "ausf:" in content),
            ("UDM config", "udm:" in content),
            ("PCF config", "pcf:" in content),
            ("NRF dependency wait", "while ! nc -z nrf 7777" in content),
        ]
        
        for fix_name, is_present in fixes:
            status = "✅" if is_present else "❌"
            print(f"{status} {fix_name}")
            
    except Exception as e:
        print(f"❌ Could not check fixes: {e}")

if __name__ == "__main__":
    main()
