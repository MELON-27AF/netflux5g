# NetFlux5G Docker Image Update Summary

## Problem
The NetFlux5G application was failing to start simulations because it was trying to pull Docker images from restricted repositories:
- **Open5GS Components**: Using `registry.gitlab.com/oai/cn5g/open5gs-*:latest` (access denied)
- **UERANSIM Components**: Using `ueransim/ueransim:latest` (repository doesn't exist)

## Solution
Updated all Docker image references to use publicly available OpenVerso images with latest versions:

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
    'nrf': 'openverso/open5gs:latest',
    'amf': 'openverso/open5gs:latest', 
    'smf': 'openverso/open5gs:latest',
    'upf': 'openverso/open5gs:latest',
    'pcf': 'openverso/open5gs:latest',
    'udm': 'openverso/open5gs:latest',
    'ausf': 'openverso/open5gs:latest'
}
```

- Changed UERANSIM images from `ueransim/ueransim:latest` to `openverso/ueransim:latest`
- Updated default fallback image to `openverso/open5gs:latest`

#### 2. Updated `src/simulation/enhanced_container_manager.py`
- Updated all Open5GS component images to use `openverso/open5gs:latest`
- Updated UERANSIM images to use `openverso/ueransim:latest`

#### 3. Created Helper Scripts
- **`pull_images.py`**: Python script to pre-pull all required Docker images
- **`pull_images.sh`**: Bash script to pre-pull all required Docker images

### Required Docker Images
The application now uses these publicly available images:
- `openverso/open5gs:latest` - for all 5G Core components (NRF, AMF, SMF, UPF, PCF, UDM, AUSF)
- `openverso/ueransim:latest` - for gNB and UE components
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
- The OpenVerso images are publicly available and don't require authentication
- Using `:latest` ensures you get the most up-to-date version of the components
- All functionality should remain the same, only the underlying Docker images have changed
