#!/usr/bin/env python3
"""
NetFlux5G Environment Preparation Script
This script helps prepare the environment for running NetFlux5G by pre-pulling Docker images.
"""

import subprocess
import sys
import time
import signal
import os

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n\n⚠️ Operation interrupted by user")
    print("You can resume by running this script again or manually pull images with:")
    print("  docker pull mongo:4.4")
    print("  docker pull openverso/open5gs:latest")
    print("  docker pull openverso/ueransim:latest")
    sys.exit(0)

def check_docker():
    """Check if Docker is available and running"""
    try:
        result = subprocess.run(['docker', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Docker is installed: {result.stdout.strip()}")
            
            # Check if Docker daemon is running
            result = subprocess.run(['docker', 'info'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print("✅ Docker daemon is running")
                return True
            else:
                print("❌ Docker daemon is not running")
                print("Please start Docker and try again")
                return False
        else:
            print("❌ Docker is not installed or not in PATH")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Docker command timed out")
        return False
    except FileNotFoundError:
        print("❌ Docker is not installed or not in PATH")
        print("Please install Docker Desktop and try again")
        return False

def check_image_exists(image_name):
    """Check if a Docker image exists locally"""
    try:
        result = subprocess.run(['docker', 'images', '-q', image_name], 
                              capture_output=True, text=True, timeout=10)
        return bool(result.stdout.strip())
    except:
        return False

def pull_image(image_name):
    """Pull a Docker image with progress"""
    if check_image_exists(image_name):
        print(f"✅ {image_name} already exists locally")
        return True
    
    print(f"\n📥 Pulling {image_name}...")
    print("This may take several minutes depending on your internet connection.")
    
    try:
        # Use docker pull with no-cache to ensure we get the latest
        process = subprocess.Popen(['docker', 'pull', image_name], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.STDOUT,
                                 universal_newlines=True)
        
        # Show output in real-time
        for line in iter(process.stdout.readline, ''):
            if line.strip():
                print(f"  {line.strip()}")
        
        process.wait()
        
        if process.returncode == 0:
            print(f"✅ Successfully pulled {image_name}")
            return True
        else:
            print(f"❌ Failed to pull {image_name}")
            return False
            
    except KeyboardInterrupt:
        print(f"\n⚠️ Interrupted while pulling {image_name}")
        return False
    except Exception as e:
        print(f"❌ Error pulling {image_name}: {e}")
        return False

def estimate_download_size():
    """Estimate total download size"""
    print("\n📊 Estimated download sizes:")
    print("  - mongo:4.4: ~400 MB")
    print("  - openverso/open5gs:latest: ~200 MB")
    print("  - openverso/ueransim:latest: ~150 MB")
    print("  Total: ~750 MB")
    print("\nNote: Actual sizes may vary based on your system and existing layers.")

def main():
    """Main function"""
    # Set up signal handler for graceful interruption
    signal.signal(signal.SIGINT, signal_handler)
    
    print("🚀 NetFlux5G Environment Preparation")
    print("====================================")
    
    # Check if Docker is available
    if not check_docker():
        sys.exit(1)
    
    # Show estimated download size
    estimate_download_size()
    
    # Ask for confirmation
    print("\n❓ Do you want to proceed with pulling the required Docker images?")
    response = input("Type 'yes' to continue or 'no' to cancel: ").lower().strip()
    
    if response not in ['yes', 'y']:
        print("Operation cancelled.")
        sys.exit(0)
    
    # List of required images
    required_images = [
        "mongo:4.4",
        "openverso/open5gs:latest",
        "openverso/ueransim:latest"
    ]
    
    print(f"\n🐳 Preparing to pull {len(required_images)} Docker images...")
    
    success_count = 0
    total_count = len(required_images)
    
    start_time = time.time()
    
    for i, image in enumerate(required_images, 1):
        print(f"\n[{i}/{total_count}] Processing {image}")
        if pull_image(image):
            success_count += 1
        else:
            print(f"⚠️ Failed to pull {image}, but continuing...")
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\n📈 Summary:")
    print(f"  - Successfully pulled: {success_count}/{total_count} images")
    print(f"  - Total time: {duration:.1f} seconds")
    
    if success_count == total_count:
        print("✅ All images pulled successfully!")
        print("You can now run NetFlux5G with: ./netflux5g.sh")
    else:
        print("⚠️ Some images failed to pull, but NetFlux5G may still work.")
        print("Docker will attempt to pull missing images when needed.")
    
    print("\n💡 Tip: You can run this script again to pull any missing images.")

if __name__ == "__main__":
    main()
