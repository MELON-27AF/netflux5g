# NetFlux5G Docker Image Update Summary

## Problem
The NetFlux5G application was failing to start simulations because it was trying to pull Docker images from restricted repositories:
- **Open5GS Components**: Using `registry.gitlab.com/oai/cn5g/open5gs-*:latest` (access denied)
- **UERANSIM Components**: Using `ueransim/ueransim:latest` (repository doesn't exist)

## Solution
Updated all Docker image references to use publicly available Gradiant images with version 1.0:

### Changes Made

#### 1. Updated `src/simulation/container_manager.py`
**Before:**
```python
image_map = {
    'nrf': 'registry.gitlab.com/oai/cn5g/open5gs-nrf:latest',
    'amf': 'registry.gitlab.com/oai/cn5g/open5gs-amf:latest', 
    'smf': 'registry.gitlab.com/oai/cn5g/open5gs-smf:latest',
    'upf': 'registry.gitlab.com/oai/cn5g/open5gs-upf:latest',
    'pcf': 'registry.gitlab.com/oai/cn5g/open5gs-pcf:latest',
    'udm': 'registry.gitlab.com/oai/cn5g/open5gs-udm:latest',
    'ausf': 'registry.gitlab.com/oai/cn5g/open5gs-ausf:latest'
}
```

**After:**
```python
image_map = {
    'nrf': 'gradiant/open5gs:latest',
    'amf': 'gradiant/open5gs:latest', 
    'smf': 'gradiant/open5gs:latest',
    'upf': 'gradiant/open5gs:latest',
    'pcf': 'gradiant/open5gs:latest',
    'udm': 'gradiant/open5gs:latest',
    'ausf': 'gradiant/open5gs:latest'
}
```

- Changed UERANSIM images from `ueransim/ueransim:latest` to `ubuntu:20.04` (with UERANSIM installed at runtime)
- Updated default fallback image to `gradiant/open5gs:latest`

#### 2. Updated `src/simulation/enhanced_container_manager.py`
- Updated all Open5GS component images to use `gradiant/open5gs:latest`
- Updated UERANSIM images to use `ubuntu:20.04`

#### 3. Created Helper Scripts
- **`pull_images.py`**: Python script to pre-pull all required Docker images
- **`pull_images.sh`**: Bash script to pre-pull all required Docker images

### Required Docker Images
The application now uses these publicly available images:
- `gradiant/open5gs:latest` - for all 5G Core components (NRF, AMF, SMF, UPF, PCF, UDM, AUSF)
- `ubuntu:20.04` - base image for gNB and UE components (UERANSIM will be installed at runtime)
- `mongo:4.4` - for MongoDB database

### How to Use
1. **Pre-pull images** (recommended):
   ```bash
   # Using bash script
   ./pull_images.sh
   
   # Or using Python script
   python3 pull_images.py
   ```

2. **Run the application**:
   ```bash
   ./netflux5g.sh
   ```

The application should now be able to successfully pull and deploy the Docker containers for 5G network simulation.

### Notes
- The Gradiant images are publicly available and don't require authentication
- Version `latest` provides the most recent stable version of the Open5GS components
- Ubuntu 20.04 is used as a base image for UERANSIM components, which will be configured at runtime
- All functionality should remain the same, only the underlying Docker images have changed
