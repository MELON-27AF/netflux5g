# NetFlux5G - 5G Core End-to-End Connectivity Fixes

This document describes the fixes implemented to enable end-to-end ping connectivity from UE through the 5G core network.

## 🔧 Issues Fixed

### 1. UPF (User Plane Function) Configuration
- **Issue**: UPF was not properly setting up tunnel interfaces for user data plane
- **Fix**: Added automatic creation and configuration of `ogstun` tunnel interface in UPF container
- **Changes**: Modified UPF startup command to create tunnel interface with proper IP addressing and NAT rules

### 2. Network Routing Configuration
- **Issue**: UE could not route traffic to external networks
- **Fix**: Added internet gateway container and proper routing setup
- **Changes**: 
  - Created `internet-gw` container for external connectivity
  - Configured NAT and IP forwarding in gateway
  - Set up default routes in UE containers through tunnel interface

### 3. UERANSIM Configuration
- **Issue**: gNB and UE were bound to localhost instead of container network
- **Fix**: Updated configuration files to use proper network interfaces
- **Changes**:
  - Modified `gnb.yaml` to bind to `0.0.0.0` instead of `127.0.0.1`
  - Updated `ue.yaml` to search for gNB on all network interfaces
  - Added proper PDU session configuration

### 4. Container Deployment Order
- **Issue**: Dependencies were not properly handled causing startup failures
- **Fix**: Implemented proper dependency waiting and startup sequencing
- **Changes**:
  - Added dependency checks for MongoDB, NRF, AMF before starting dependent services
  - Implemented proper waiting mechanisms using netcat (nc) checks

### 5. Post-Deployment Networking
- **Issue**: Network configuration was not set up after container deployment
- **Fix**: Added post-deployment networking setup phase
- **Changes**:
  - Wait for UE registration and PDU session establishment
  - Configure routing in UE containers after tunnel interface creation
  - Set up DNS resolution for external connectivity

### 6. End-to-End Connectivity Testing
- **Issue**: No proper testing for UE to external network connectivity
- **Fix**: Enhanced connectivity testing with specific UE end-to-end tests
- **Changes**:
  - Added tunnel interface existence checks
  - Implemented ping tests from UE through tunnel interface
  - Added external DNS connectivity tests (8.8.8.8)

## 🚀 Usage

### Running the Application
1. Ensure Docker Desktop is running
2. Run the application: `python src/main.py`
3. Create a 5G network topology with components: NRF, AMF, SMF, UPF, gNB, UE
4. Click "Run Simulation" to deploy the network
5. Wait for all containers to start and register
6. Test connectivity using the terminal dialog

### Testing End-to-End Connectivity
1. Run the connectivity test script: `powershell -ExecutionPolicy Bypass -File test_5g_connectivity.ps1`
2. The script will:
   - Deploy a complete 5G core network
   - Wait for UE registration
   - Test end-to-end connectivity
   - Report success/failure with detailed results

### Manual Testing
After deployment, you can manually test connectivity:

1. **Access UE container**:
   ```bash
   docker exec -it ue-test sh
   ```

2. **Check tunnel interface**:
   ```bash
   ip addr show uesimtun0
   ```

3. **Test internet connectivity**:
   ```bash
   ping -c 4 -I uesimtun0 8.8.8.8
   ```

4. **Test DNS resolution**:
   ```bash
   nslookup google.com
   ```

## 📊 Expected Results

When working correctly, you should see:
- ✅ UE registers with the 5G core network
- ✅ PDU session established with tunnel interface (uesimtun0)
- ✅ UE can ping internet gateway through tunnel
- ✅ UE can ping external DNS servers (8.8.8.8)
- ✅ End-to-end connectivity test passes

## 🔍 Troubleshooting

### Common Issues

1. **Docker not running**
   - Start Docker Desktop and wait for it to be ready

2. **Insufficient memory**
   - Ensure at least 4GB RAM available
   - Close other applications to free memory

3. **Container startup failures**
   - Check Docker logs: `docker logs <container-name>`
   - Verify all required images are available

4. **UE registration fails**
   - Check AMF and gNB connectivity
   - Verify configuration files are properly mounted

5. **No tunnel interface**
   - Check UPF startup logs
   - Verify SMF-UPF communication
   - Ensure proper PFCP connectivity

## 📝 Configuration Files Modified

- `config/open5gs/upf.yaml` - Added dual subnet configuration
- `config/ueransim/gnb.yaml` - Changed IP binding from localhost to 0.0.0.0
- `config/ueransim/ue.yaml` - Updated gNB search list for container networking
- `src/simulation/enhanced_container_manager.py` - Major networking fixes

## 🎯 Next Steps

1. Test with multiple UEs
2. Add support for different slice configurations
3. Implement QoS testing
4. Add network performance monitoring
5. Create automated CI/CD testing pipeline

---

**Note**: These fixes ensure that the NetFlux5G simulator can properly establish end-to-end connectivity from UE devices through the 5G core network to external internet services, enabling realistic 5G network testing and validation.
