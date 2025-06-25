#!/bin/bash

# Script to pull required Docker images for NetFlux5G
# This ensures all necessary images are available before running the simulation

echo "Pulling required Docker images for NetFlux5G..."
echo "============================================================"

# List of required images
images=(
    "openverso/open5gs:latest"         # Open5GS 5G Core components
    "towards5gs/ueransim-gnb:v3.2.3"   # UERANSIM gNB component
    "towards5gs/ueransim-ue:v3.2.3"    # UERANSIM UE component
    "mongo:4.4"                        # MongoDB for Open5GS
    "ubuntu:20.04"                     # Base Ubuntu for custom containers
    "alpine:latest"                    # Lightweight base image
)

# Pull each image
for image in "${images[@]}"; do
    echo "Pulling $image..."
    if docker pull "$image"; then
        echo "✓ Successfully pulled $image"
    else
        echo "✗ Failed to pull $image"
    fi
    echo
done

echo "============================================================"
echo "Image pulling completed!"

# List pulled images
echo
echo "Available NetFlux5G images:"
for image in "${images[@]}"; do
    if docker images --format "table {{.Repository}}:{{.Tag}}" | grep -q "$image"; then
        size=$(docker images --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}" | grep "$image" | awk '{print $2}')
        echo "✓ $image - Size: $size"
    else
        echo "✗ $image - Not available"
    fi
done
