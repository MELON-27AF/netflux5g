#!/bin/bash

echo "🔧 NetFlux5G Container Diagnostic Script"
echo "========================================"

echo "📋 Current Container Status:"
docker ps -a --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"

echo -e "\n🔍 Container Logs Analysis:"

containers=("nrf-test" "amf-test" "smf-test" "upf-test" "ausf-test" "udm-test" "pcf-test" "gnb-test" "ue-test" "internet-gw" "mongodb")

for container in "${containers[@]}"; do
    if docker ps -a --format '{{.Names}}' | grep -q "^${container}$"; then
        echo -e "\n📄 ${container} logs (last 10 lines):"
        echo "----------------------------------------"
        docker logs "${container}" 2>&1 | tail -10
        
        # Check if container is running
        status=$(docker inspect "${container}" --format='{{.State.Status}}' 2>/dev/null)
        echo "Status: ${status}"
        
        if [[ "${status}" == "exited" ]]; then
            exit_code=$(docker inspect "${container}" --format='{{.State.ExitCode}}' 2>/dev/null)
            echo "Exit code: ${exit_code}"
        fi
    else
        echo -e "\n❌ ${container} not found"
    fi
done

echo -e "\n📁 Configuration Files Check:"
echo "----------------------------------------"
if [[ -d "./config" ]]; then
    echo "Open5GS configs:"
    find ./config/open5gs -name "*.yaml" 2>/dev/null | head -5
    
    echo -e "\nUERANSIM configs:"
    find ./config/ueransim -name "*.yaml" 2>/dev/null | head -5
    
    echo -e "\nSample config content (NRF):"
    if [[ -f "./config/open5gs/nrf-test/nrf.yaml" ]]; then
        head -15 "./config/open5gs/nrf-test/nrf.yaml"
    fi
else
    echo "❌ Config directory not found"
fi

echo -e "\n🔧 Recommended Actions:"
echo "1. MongoDB deployment failed - port conflict fixed"
echo "2. Check container logs above for specific errors"
echo "3. Verify configuration file contents"
echo "4. Try restarting NetFlux5G after fixes"

echo -e "\n💡 Quick Fix Commands:"
echo "# Remove all test containers:"
echo "docker rm -f \$(docker ps -aq --filter='name=-test')"
echo ""
echo "# Remove mongodb container:"
echo "docker rm -f mongodb"
echo ""
echo "# Restart NetFlux5G:"
echo "./netflux5g_safe.sh"
