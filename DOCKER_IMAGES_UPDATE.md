# NetFlux5G Docker Image Update Summary

## Problem
The NetFlux5G application was failing to start simulations because it was trying to pull Docker images from restricted repositories:
- **Open5GS Components**: Using `registry.gitlab.com/oai/cn5g/open5gs-*:latest` (access denied)
- **UERANSIM Components**: Using `ueransim/ueransim:latest` (repository doesn't exist)

## Solution
Updated all Docker image references to use publicly available Gradiant images with specific versions:

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
image_map = {    'nrf': 'gradiant/open5gs:2.7.5',
    'amf': 'gradiant/open5gs:2.7.5', 
    'smf': 'gradiant/open5gs:2.7.5',
    'upf': 'gradiant/open5gs:2.7.5',
    'pcf': 'gradiant/open5gs:2.7.5',
    'udm': 'gradiant/open5gs:2.7.5',
    'ausf': 'gradiant/open5gs:2.7.5'
}
```

- Changed UERANSIM images from `ueransim/ueransim:latest` to `gradiant/ueransim:3.2.7`
- Updated default fallback image to `gradiant/open5gs:2.7.5`

#### 2. Updated `src/simulation/enhanced_container_manager.py`
- Updated all Open5GS component images to use `gradiant/open5gs:2.7.5`
- Updated UERANSIM images to use `gradiant/ueransim:3.2.7`

#### 3. Created Helper Scripts
- **`pull_images.py`**: Python script to pre-pull all required Docker images
- **`pull_images.sh`**: Bash script to pre-pull all required Docker images

### Required Docker Images
The application now uses these publicly available images:
- `gradiant/open5gs:2.7.5` - for all 5G Core components (NRF, AMF, SMF, UPF, PCF, UDM, AUSF)
- `gradiant/ueransim:3.2.7` - for gNB and UE components
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
- Version `2.7.5` provides a stable version of the Open5GS components
- Version `3.2.7` provides a stable version of UERANSIM components
- All functionality should remain the same, only the underlying Docker images have changed
