#!/bin/bash

echo "🔍 NetFlux5G Container Log Analysis"
echo "=================================="

echo "📊 Current Status Summary:"
echo "✅ RUNNING: mongodb, nrf-test, ue-test, internet-gw"
echo "❌ EXITING: amf-test, smf-test, upf-test, ausf-test, udm-test, pcf-test, gnb-test"
echo ""

# Function to analyze container logs
analyze_container() {
    local container=$1
    echo "🔍 Analyzing $container:"
    echo "----------------------------------------"
    
    if docker ps -a --format '{{.Names}}' | grep -q "^${container}$"; then
        # Get exit code
        exit_code=$(docker inspect "$container" --format='{{.State.ExitCode}}' 2>/dev/null)
        status=$(docker inspect "$container" --format='{{.State.Status}}' 2>/dev/null)
        
        echo "Status: $status (Exit Code: $exit_code)"
        
        # Show last 15 lines of logs
        echo "Last logs:"
        docker logs "$container" 2>&1 | tail -15
        echo ""
        
        # Look for specific error patterns
        logs=$(docker logs "$container" 2>&1)
        
        if echo "$logs" | grep -q "cannot open file"; then
            echo "❌ Config file issue detected"
        fi
        
        if echo "$logs" | grep -q "Connection refused\|connection refused"; then
            echo "❌ Connection issue detected (likely MongoDB or service dependency)"
        fi
        
        if echo "$logs" | grep -q "Address already in use"; then
            echo "❌ Port conflict detected"
        fi
        
        if echo "$logs" | grep -q "Permission denied"; then
            echo "❌ Permission issue detected"
        fi
        
        echo "----------------------------------------"
    else
        echo "❌ Container $container not found"
    fi
    echo ""
}

# Analyze failing containers
failing_containers=("amf-test" "smf-test" "upf-test" "ausf-test" "udm-test" "pcf-test" "gnb-test")

for container in "${failing_containers[@]}"; do
    analyze_container "$container"
done

echo "🔧 Quick Diagnostics:"
echo "1. Check if MongoDB is accessible from containers:"
docker exec nrf-test ping -c 2 mongodb 2>/dev/null && echo "✅ MongoDB is reachable" || echo "❌ MongoDB is not reachable"

echo ""
echo "2. Check if config files are mounted correctly:"
docker exec nrf-test ls -la /etc/open5gs/ 2>/dev/null && echo "✅ Config files mounted in NRF" || echo "❌ Config files not mounted"

echo ""
echo "💡 Common fixes to try:"
echo "1. Restart all containers: docker restart \$(docker ps -aq --filter='name=-test')"
echo "2. Check MongoDB connectivity from failing containers"
echo "3. Verify configuration file syntax"
echo "4. Clean restart: Remove all containers and redeploy"
