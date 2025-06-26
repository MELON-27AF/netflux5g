#!/bin/bash

echo "🔧 Testing NetFlux5G Container Deployment"
echo "========================================"

echo "Current containers:"
docker ps -a

echo -e "\n📋 Checking container logs for errors..."

echo -e "\n🔍 NRF Container Logs:"
docker logs nrf-test 2>&1 | head -10

echo -e "\n🔍 AMF Container Logs:"
docker logs amf-test 2>&1 | head -10

echo -e "\n🔍 gNB Container Logs:"
docker logs gnb-test 2>&1 | head -10

echo -e "\n🔍 UE Container Logs:"
docker logs ue-test 2>&1 | head -10

echo -e "\n🔍 Router Container Logs:"
docker logs internet-gw 2>&1 | head -10

echo -e "\n📁 Checking configuration files:"
echo "Open5GS configs:"
find ./config/open5gs -name "*.yaml" 2>/dev/null | head -5

echo -e "\nUERANSIM configs:"
find ./config/ueransim -name "*.yaml" 2>/dev/null | head -5

echo -e "\n🧹 Cleaning up failed containers..."
docker rm -f $(docker ps -aq --filter="name=-test") 2>/dev/null || echo "No test containers to remove"

echo -e "\n✅ Test completed. You can now try running NetFlux5G again."
