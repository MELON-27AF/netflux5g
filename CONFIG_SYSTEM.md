# NetFlux5G Configuration System

This document describes the new YAML-based configuration system for NetFlux5G 5G components.

## Overview

The NetFlux5G configuration system now uses individual YAML files for each 5G component type, allowing for better customization and maintainability. The system supports both Open5GS core network functions and UERANSIM RAN components.

## Configuration Structure

```
config/
├── open5gs/           # Open5GS 5G Core components
│   ├── nrf.yaml       # Network Repository Function
│   ├── amf.yaml       # Access and Mobility Management Function
│   ├── smf.yaml       # Session Management Function
│   ├── upf.yaml       # User Plane Function
│   ├── ausf.yaml      # Authentication Server Function
│   ├── udm.yaml       # Unified Data Management
│   └── pcf.yaml       # Policy Control Function
├── ueransim/          # UERANSIM RAN components
│   ├── gnb.yaml       # Next Generation NodeB (gNodeB)
│   └── ue.yaml        # User Equipment
└── instances/         # Generated instance-specific configurations
    ├── component-1/
    ├── component-2/
    └── ...
```

## Component Configuration Files

### Open5GS Components

#### NRF (Network Repository Function)
- **File**: `config/open5gs/nrf.yaml`
- **Purpose**: Service discovery and registration for 5G Core
- **Key settings**: SBI interface, database connection, discovery options

#### AMF (Access and Mobility Management Function)
- **File**: `config/open5gs/amf.yaml`
- **Purpose**: Access control, mobility management, and registration
- **Key settings**: NGAP interface, GUAMI, TAI, PLMN support, security

#### SMF (Session Management Function)
- **File**: `config/open5gs/smf.yaml`
- **Purpose**: Session establishment, modification, and release
- **Key settings**: PFCP interface, subnet configuration, DNS servers

#### UPF (User Plane Function)
- **File**: `config/open5gs/upf.yaml`
- **Purpose**: Packet routing and forwarding in user plane
- **Key settings**: PFCP/GTPU interfaces, subnet configuration

#### AUSF (Authentication Server Function)
- **File**: `config/open5gs/ausf.yaml`
- **Purpose**: Authentication services for UE
- **Key settings**: SBI interface, authentication parameters

#### UDM (Unified Data Management)
- **File**: `config/open5gs/udm.yaml`
- **Purpose**: Subscription data management
- **Key settings**: SBI interface, subscription management

#### PCF (Policy Control Function)
- **File**: `config/open5gs/pcf.yaml`
- **Purpose**: Policy control and QoS management
- **Key settings**: SBI interface, policy rules, QoS configuration

### UERANSIM Components

#### gNB (Next Generation NodeB)
- **File**: `config/ueransim/gnb.yaml`
- **Purpose**: 5G base station simulation
- **Key settings**: MCC/MNC, cell configuration, AMF connection, power settings

#### UE (User Equipment)
- **File**: `config/ueransim/ue.yaml`
- **Purpose**: 5G device simulation
- **Key settings**: IMSI, security keys, capabilities, sessions

## Configuration Manager

The `ConfigManager` class provides programmatic access to the configuration system:

### Key Features

1. **Template Loading**: Load base configuration templates
2. **Customization**: Apply component-specific properties
3. **Instance Management**: Create and manage instance-specific configurations
4. **Validation**: Validate YAML configuration files
5. **Cleanup**: Remove instance configurations when no longer needed

### Usage Example

```python
from utils.config_manager import ConfigManager

# Initialize configuration manager
config_mgr = ConfigManager()

# Create customized gNB configuration
gnb_properties = {
    'mcc': '999',
    'mnc': '70',
    'gnb_id': 1,
    'tac': 1,
    'power': 23
}

config_file = config_mgr.create_instance_config('gnb', 'gnb-test', gnb_properties)
config_dir = config_mgr.get_instance_config_dir('gnb-test')

# Use in container deployment
volumes = [f"{config_dir}:/etc/ueransim:ro"]
```

## Customization Options

### AMF Customization
- MCC/MNC configuration
- TAC (Tracking Area Code)
- PLMN support
- Security algorithms

### SMF Customization
- IP subnet configuration
- DNS server settings
- QoS parameters

### UPF Customization
- IP subnet configuration
- Routing settings

### gNB Customization
- MCC/MNC configuration
- gNB ID and TAC
- Transmission power
- Cell configuration

### UE Customization
- IMSI configuration
- Security keys (K, OP/OPC)
- IMEI settings
- Capability parameters

## Integration with Container Manager

The enhanced container manager now uses the configuration system:

1. **Configuration Creation**: Automatically creates instance-specific configs
2. **Volume Mounting**: Mounts config directories into containers
3. **Cleanup**: Removes configurations when containers are destroyed

## Benefits

1. **Maintainability**: Centralized configuration templates
2. **Customization**: Easy per-instance customization
3. **Validation**: YAML validation prevents configuration errors
4. **Documentation**: Self-documenting configuration files
5. **Version Control**: Configuration templates can be version controlled
6. **Debugging**: Easier to debug configuration issues

## Testing

Run the configuration system test:

```bash
python test_config_system.py
```

This will:
- Test template loading
- Create customized configurations
- Validate YAML files
- Test cleanup functionality

## Migration

The system maintains backward compatibility. Existing deployments will continue to work, but new deployments will use the YAML-based configuration system automatically.

## Troubleshooting

### Common Issues

1. **Missing PyYAML**: Install with `pip install PyYAML`
2. **Permission Issues**: Ensure write access to config directory
3. **Invalid YAML**: Use the validation function to check syntax
4. **Missing Templates**: Verify template files exist in config directories

### Debug Commands

```bash
# Test configuration system
python test_config_system.py

# Validate specific configuration
python -c "from src.utils.config_manager import ConfigManager; ConfigManager().validate_config('path/to/config.yaml')"

# List available templates
python -c "from src.utils.config_manager import ConfigManager; print(ConfigManager().list_available_templates())"
```
