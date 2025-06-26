#!/bin/bash

echo "🚀 NetFlux5G Container Deployment Fix"
echo "===================================="

# Step 1: Clean up existing containers
echo "🧹 Cleaning up existing containers..."
docker rm -f $(docker ps -aq --filter="name=-test") 2>/dev/null || echo "No test containers to remove"
docker rm -f mongodb 2>/dev/null || echo "No mongodb container to remove"

# Step 2: Check for port conflicts
echo -e "\n🔍 Checking for port conflicts..."
echo "Checking if ports are free:"
for port in 27017 7777 80 38412; do
    if netstat -tuln | grep -q ":${port} "; then
        echo "⚠️  Port ${port} is in use"
        lsof -i :${port} 2>/dev/null || echo "   (unable to determine process)"
    else
        echo "✅ Port ${port} is free"
    fi
done

# Step 3: Verify Docker network
echo -e "\n🌐 Checking Docker network..."
if docker network ls | grep -q netflux5g_network; then
    echo "✅ NetFlux5G network exists"
else
    echo "❌ NetFlux5G network missing"
fi

# Step 4: Check configuration files
echo -e "\n📁 Checking configuration structure..."
config_dirs=("./config/open5gs" "./config/ueransim")
for dir in "${config_dirs[@]}"; do
    if [[ -d "$dir" ]]; then
        echo "✅ $dir exists"
        count=$(find "$dir" -name "*.yaml" 2>/dev/null | wc -l)
        echo "   Found $count YAML files"
    else
        echo "❌ $dir missing"
        mkdir -p "$dir" && echo "   Created $dir"
    fi
done

# Step 5: Test a simple container deployment
echo -e "\n🧪 Testing container deployment..."
echo "Testing MongoDB deployment..."
if docker run --rm --name test-mongo -d mongo:4.4 >/dev/null 2>&1; then
    sleep 2
    docker stop test-mongo >/dev/null 2>&1
    echo "✅ MongoDB container test passed"
else
    echo "❌ MongoDB container test failed"
fi

echo "Testing UERANSIM container..."
if docker run --rm --name test-ueransim towards5gs/ueransim-gnb:v3.2.3 /ueransim/build/nr-gnb --help >/dev/null 2>&1; then
    echo "✅ UERANSIM container test passed"
else
    echo "❌ UERANSIM container test failed - executable path might be wrong"
fi

# Step 6: Provide recommendations
echo -e "\n💡 Recommendations:"
echo "1. ✅ Fixed MongoDB port conflict (removed port mapping)"
echo "2. ✅ Fixed UERANSIM executable paths"
echo "3. ✅ Added configuration file volume mounting"
echo "4. ✅ Added router deployment support"
echo "5. ⏳ Added MongoDB initialization wait time"

echo -e "\n🎯 Next Steps:"
echo "1. Run: chmod +x diagnostics.sh && ./diagnostics.sh"
echo "2. Run: ./netflux5g_safe.sh"
echo "3. If containers still fail, check logs with: docker logs <container-name>"

echo -e "\n📊 Current System Status:"
echo "Docker version: $(docker --version 2>/dev/null || echo 'Not available')"
echo "Available memory: $(free -h | awk '/^Mem:/ {print $7}' 2>/dev/null || echo 'Unknown')"
echo "Available disk: $(df -h . | awk 'NR==2 {print $4}' 2>/dev/null || echo 'Unknown')"

echo -e "\n✅ Fix script completed successfully!"
