# NetFlux5G - 5G Network Simulation Tool

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-required-blue.svg)](https://www.docker.com/)

NetFlux5G is a comprehensive 5G network simulation tool that runs on Docker containers, similar to MiniEdit from Containernet. It provides a graphical interface for designing, deploying, and managing 5G network topologies with real network functions.

## ✨ Key Features

- **Visual Topology Design**: Drag-and-drop interface for creating 5G network topologies
- **Container-Based Simulation**: Uses Docker containers to run real 5G network components
- **YAML Configuration System**: Flexible configuration management for all 5G components
- **Real-time Terminal Access**: Direct terminal access to running containers
- **5G Core Components**: Support for Open5GS (AMF, SMF, UPF, NRF, etc.) using openverso/open5gs:latest images
- **RAN Simulation**: UERANSIM for gNodeB and UE simulation using openverso/ueransim:latest images
- **Component Customization**: Easy customization of 5G components with properties
- **Network Testing**: Built-in connectivity testing and monitoring
- **Export Capabilities**: Export to Docker Compose and Mininet

## 📋 Requirements

### System Requirements
- **Operating System**: Windows 10/11 with WSL2, Linux, or macOS
- **Python**: 3.8 or higher
- **Docker**: Docker Desktop (Windows/macOS) or Docker Engine (Linux)
- **Git**: For cloning the repository

### Python Dependencies
- PyQt5 (GUI framework)
- Docker Python SDK
- PyYAML for configuration
- Requests for HTTP communication

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/netflux5g/netflux5g.git
cd netflux5g
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Pull Docker Images
```bash
# Windows
.\scripts\pull_images.ps1

# Linux/macOS
chmod +x scripts/pull_images.sh
./scripts/pull_images.sh
```

### 4. Run Application
```bash
# Windows
.\scripts\run_netflux5g.bat

# Linux/macOS
chmod +x scripts/netflux5g.sh
./scripts/netflux5g.sh

# Or run directly
cd src
python main.py
```

## 📖 Usage Guide

### Creating a 5G Network Topology

1. **Launch NetFlux5G**
2. **Drag components** from the left panel to the canvas:
   - **5G Core Components**: AMF, SMF, UPF, NRF, PCF, UDM, AUSF
   - **RAN Components**: gNodeB, UE (User Equipment)
   - **Infrastructure**: Switch, Router, Host
3. **Connect components** by dragging from one component to another
4. **Configure properties** by right-clicking components → Properties

### Running Simulations

1. **Click "Run Simulation" (F5)** or menu Simulation → Run Simulation
2. **Wait for container deployment** - the application will:
   - Create a dedicated Docker network for 5G
   - Deploy containers for each component
   - Configure inter-container connectivity
3. **Terminal Dialog opens automatically** showing:
   - List of running containers
   - Status and IP addresses
   - Interface for command execution

### Testing 5G Connectivity

**Basic connectivity test:**

1. Deploy a complete 5G topology (Core + gNB + UE)
2. Use terminal to check UE registration:
   ```bash
   # In UE container
   cat /proc/net/dev
   
   # Check if TUN interface is created
   ifconfig uesimtun0
   ```

3. **Test internet connectivity through 5G:**
   ```bash
   # In UE container, ping through TUN interface
   ping -I uesimtun0 8.8.8.8
   ```

## 🏗️ Project Structure

```
netflux5g/
├── src/                    # Main application source code
│   ├── main.py            # Application entry point
│   ├── gui/               # GUI components
│   ├── models/            # Data models and network components
│   ├── simulation/        # Container management and simulation logic
│   ├── export/            # Export functionality
│   ├── utils/             # Utility functions
│   └── assets/            # Icons and images
├── config/                # Configuration templates
│   └── templates/         # Docker Compose and component templates
├── scripts/               # Utility scripts
├── docs/                  # Documentation
├── examples/              # Example topologies and tutorials
├── requirements.txt       # Python dependencies
├── setup.py              # Package setup configuration
└── README.md             # This file
```

## 🔧 Configuration System

NetFlux5G uses a YAML-based configuration system for flexible component customization:

### Configuration Structure
```
config/
├── templates/
│   ├── open5gs/          # Open5GS configuration templates
│   └── ueransim/         # UERANSIM configuration templates
└── instances/            # Generated instance configurations
```

### Features
- **Template-Based**: Each component has YAML configuration templates
- **Instance-Specific**: Automatic configuration customization per instance
- **Property Customization**: Easy parameter modification (MCC/MNC, IP, etc.)
- **Validation**: Automatic YAML validation to prevent errors
- **Auto-Cleanup**: Automatic configuration cleanup when containers are removed

## 🔍 Troubleshooting

### Docker Issues
```bash
# Check Docker status
docker info

# Check available images
docker images

# Manual cleanup if needed
docker container prune
docker network prune
```

### Python Dependencies
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Check PyQt5 installation
python -c "from PyQt5.QtWidgets import QApplication; print('PyQt5 OK')"
```

### Common Issues
- Ensure Docker Desktop is running (Windows)
- Ensure user is in docker group (Linux)
- Check firewall/antivirus blocking Docker

## 🧪 Testing

### Run Tests
```bash
# Run all tests
python -m pytest

# Run specific test modules
python -m pytest tests/test_simulation.py
```

### Manual Testing
```bash
# Test Docker connectivity
docker run hello-world

# Test 5G image availability
docker pull openverso/open5gs:latest
docker pull openverso/ueransim:latest
```

## 📚 Documentation

- [User Guide](docs/user-guide.md)
- [API Reference](docs/api-reference.md)
- [Configuration Guide](docs/configuration.md)
- [Examples](examples/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Open5GS](https://open5gs.org/) for the 5G Core Network implementation
- [UERANSIM](https://github.com/aligungr/UERANSIM) for the 5G RAN simulator
- [OpenVerso](https://openverso.org/) for providing Docker images
- PyQt5 for the GUI framework

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/netflux5g/netflux5g/issues)
- **Discussions**: [GitHub Discussions](https://github.com/netflux5g/netflux5g/discussions)
- **Email**: contact@netflux5g.dev

---

**Made with ❤️ for the 5G research community**
