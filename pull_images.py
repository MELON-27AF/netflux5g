#!/usr/bin/env python3
"""
Script to pull required Docker images for NetFlux5G
This ensures all necessary images are available before running the simulation
"""

import docker
import sys

def pull_images():
    """Pull all required Docker images"""      # List of required images
    images = [
        "open5gs/open5gs-nrf",      # NRF (Network Repository Function)
        "open5gs/open5gs-amf",      # AMF (Access and Mobility Management Function)
        "open5gs/open5gs-smf",      # SMF (Session Management Function)
        "open5gs/open5gs-upf",      # UPF (User Plane Function)
        "open5gs/open5gs-pcf",      # PCF (Policy Control Function)
        "open5gs/open5gs-udm",      # UDM (Unified Data Management)
        "open5gs/open5gs-ausf",     # AUSF (Authentication Server Function)
        "open5gs/ueransim-gnb",     # UERANSIM gNB
        "open5gs/ueransim-ue",      # UERANSIM UE
        "mongo:4.4"                 # MongoDB for Open5GS
    ]
    
    try:
        # Initialize Docker client
        client = docker.from_env()
        
        print("Pulling required Docker images for NetFlux5G...")
        print("=" * 60)
        
        for image in images:
            print(f"Pulling {image}...")
            try:
                client.images.pull(image)
                print(f"✓ Successfully pulled {image}")
            except docker.errors.ImageNotFound:
                print(f"✗ Image {image} not found")
            except docker.errors.APIError as e:
                print(f"✗ Error pulling {image}: {e}")
            except Exception as e:
                print(f"✗ Unexpected error pulling {image}: {e}")
        
        print("=" * 60)
        print("Image pulling completed!")
        
        # List pulled images
        print("\nAvailable NetFlux5G images:")
        for image in images:
            try:
                img = client.images.get(image)
                print(f"✓ {image} - Size: {img.attrs['Size'] // 1024 // 1024} MB")
            except:
                print(f"✗ {image} - Not available")
                
    except docker.errors.DockerException as e:
        print(f"Docker error: {e}")
        print("Make sure Docker is running and accessible.")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    pull_images()
