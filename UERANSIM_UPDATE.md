# NetFlux5G UERANSIM Image Update

## Changes Made

This document summarizes the updates made to NetFlux5G to use the new UERANSIM images from towards5gs instead of openverso.

### Updated Docker Images

**Previous Images:**
- `openverso/ueransim:latest` (used for both gNB and UE)

**New Images:**
- `towards5gs/ueransim-gnb:v3.2.3` (for gNB simulation)
- `towards5gs/ueransim-ue:v3.2.3` (for UE simulation)

### Files Updated

1. **Core Container Management:**
   - `src/simulation/enhanced_container_manager.py`
     - Updated UERANSIM configuration
     - Updated required images list
     - Updated fallback image references

2. **Legacy Container Management:**
   - `src/simulation/container_manager.py`
     - Updated gNB and UE container deployment

3. **Docker Export:**
   - `src/export/docker_exporter.py`
     - Updated exported Docker Compose files

4. **Configuration Templates:**
   - `config/templates/docker-compose-5g-basic.yml`
     - Updated gNB and UE service definitions

5. **Image Pulling Scripts:**
   - `pull_images.py`
   - `pull_images.sh`
   - `pull_images.ps1`
   - `prepare_environment.py`

6. **Launcher Scripts:**
   - `netflux5g_safe.sh` (updated download size estimate)

### Benefits of the Change

1. **Specialized Images**: Using separate images for gNB and UE allows for:
   - Smaller image sizes
   - More focused functionality
   - Better optimization for specific roles

2. **Version Pinning**: Using specific version tags (v3.2.3) provides:
   - Reproducible deployments
   - Better stability
   - Clear version tracking

3. **Community Support**: The towards5gs images are:
   - Well-maintained
   - Actively updated
   - Widely used in 5G research

### Total Download Size Update

- **Previous**: ~750 MB total
- **New**: ~800 MB total (due to separate gNB and UE images)

### Compatibility

The new images maintain compatibility with the existing NetFlux5G configuration system:
- Same command-line interfaces (`nr-gnb`, `nr-ue`)
- Same configuration file paths (`/etc/ueransim/gnb.yaml`, `/etc/ueransim/ue.yaml`)
- Same networking requirements (NET_ADMIN capability, privileged mode)

### Testing Recommendations

Before deploying in production:

1. **Pull New Images:**
   ```bash
   python3 prepare_environment.py
   ```

2. **Test Basic Functionality:**
   ```bash
   ./netflux5g_safe.sh
   ```

3. **Verify Container Creation:**
   - Check that gNB and UE containers start successfully
   - Verify network connectivity between components
   - Test simulation execution

### Rollback Plan

If issues occur, you can rollback by:

1. **Revert to Previous Images:**
   ```bash
   # Find and replace in all files:
   # towards5gs/ueransim-gnb:v3.2.3 → openverso/ueransim:latest
   # towards5gs/ueransim-ue:v3.2.3 → openverso/ueransim:latest
   ```

2. **Update Image Lists:**
   - Remove separate gNB/UE entries
   - Add back single `openverso/ueransim:latest` entry

### Next Steps

1. Test the updated configuration with a simple 5G network topology
2. Monitor container startup times and resource usage
3. Validate that all UERANSIM features work as expected
4. Update documentation and user guides as needed

---

*Updated: June 25, 2025*
*NetFlux5G Version: Latest*
