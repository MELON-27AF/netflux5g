# NetFlux5G - 5G Network Simulation Tool

NetFlux5G adalah tools simulasi jaringan 5G yang berjalan menggunakan container Docker, mirip dengan cara kerja MiniEdit dari Containernet. Aplikasi ini memungkinkan Anda mendesain, men-deploy, dan mengelola topologi jaringan 5G dengan interface grafis yang mudah digunakan.

## 🚀 Fitur Utama

- **Desain Topologi Visual**: Drag-and-drop interface untuk membuat topologi jaringan 5G
- **Container-Based Simulation**: Menggunakan Docker container untuk menjalankan komponen 5G nyata
- **YAML Configuration System**: Sistem konfigurasi berbasis YAML untuk setiap komponen 5G
- **Real-time Terminal Access**: Akses terminal langsung ke setiap container yang berjalan
- **5G Core Components**: Support untuk Open5GS (AMF, SMF, UPF, NRF, dll.) menggunakan openverso/open5gs:latest images
- **RAN Simulation**: UERANSIM untuk gNodeB dan UE simulation menggunakan openverso/ueransim:latest images
- **Component Customization**: Kustomisasi mudah untuk setiap komponen 5G dengan properties
- **Network Testing**: Built-in connectivity testing dan monitoring
- **Export Capabilities**: Export ke Docker Compose dan Mininet

## 📋 Persyaratan Sistem

### Software yang Diperlukan:
- **Windows 10/11** dengan WSL2 atau **Linux**
- **Python 3.8+**
- **Docker Desktop** (Windows) atau **Docker Engine** (Linux)
- **Git** untuk cloning repository

### Dependency Python:
- PyQt5 (GUI framework)
- Docker Python SDK
- PyYAML untuk konfigurasi
- Requests untuk HTTP communication

## 🔧 Instalasi

### 1. Clone Repository
```bash
git clone https://github.com/your-repo/netflux5g.git
cd netflux5g
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Pastikan Docker Berjalan
```bash
docker --version
docker info
```

### 4. Jalankan Aplikasi

**Windows:**
```bash
run_netflux5g.bat
```

**Linux/Mac:**
```bash
chmod +x netflux5g.sh
./netflux5g.sh
```

Atau jalankan langsung:
```bash
cd src
python main.py
```

## 🎯 Cara Menggunakan

### 1. Membuat Topologi 5G

1. **Buka NetFlux5G**
2. **Drag komponen** dari panel kiri ke canvas:
   - **5G Core**: AMF, SMF, UPF, NRF, PCF, UDM, AUSF
   - **RAN**: gNodeB, UE (User Equipment)
   - **Infrastructure**: Switch, Router, Host
3. **Hubungkan komponen** dengan drag dari satu komponen ke yang lain
4. **Set properties** komponen dengan klik kanan → Properties

### 2. Menjalankan Simulasi

1. **Klik "Run Simulation" (F5)** atau menu Simulation → Run Simulation
2. **Tunggu deployment container** - aplikasi akan:
   - Membuat Docker network khusus untuk 5G
   - Deploy container untuk setiap komponen
   - Mengkonfigurasi konektivitas antar container
3. **Terminal Dialog otomatis terbuka** menampilkan:
   - Daftar container yang berjalan
   - Status dan IP address masing-masing
   - Interface untuk command execution

### 3. Menggunakan Terminal Container

**Terminal Dialog menyediakan:**
- **Container List**: Daftar semua container dengan status dan IP
- **Command Execution**: Jalankan command di container tertentu
- **Ping Tests**: Test konektivitas antar container
- **Network Analysis**: Show routes, interfaces, dll.

**Quick Actions:**
- **Double-click container** → Buka terminal di Windows Command Prompt
- **Execute Command** → Jalankan command dan lihat output
- **Ping All** → Test konektivitas komprehensif
- **Show Routes/Interfaces** → Network troubleshooting

### 4. Monitoring dan Testing

**Simulation Results Window menampilkan:**
- **Summary**: Statistik jaringan dan deployment
- **Containers**: Status detail semua container
- **Connectivity**: Hasil ping test antar komponen
- **Performance**: Metrics simulasi (latency, throughput, dll.)

## 📄 Sistem Konfigurasi YAML

NetFlux5G menggunakan sistem konfigurasi berbasis YAML yang memungkinkan kustomisasi mudah untuk setiap komponen 5G.

### Struktur Konfigurasi

```
config/
├── open5gs/           # Template konfigurasi Open5GS
│   ├── nrf.yaml       # Network Repository Function
│   ├── amf.yaml       # Access and Mobility Management Function
│   ├── smf.yaml       # Session Management Function
│   ├── upf.yaml       # User Plane Function
│   ├── ausf.yaml      # Authentication Server Function
│   ├── udm.yaml       # Unified Data Management
│   └── pcf.yaml       # Policy Control Function
├── ueransim/          # Template konfigurasi UERANSIM
│   ├── gnb.yaml       # Next Generation NodeB
│   └── ue.yaml        # User Equipment
└── instances/         # Konfigurasi instance yang dihasilkan otomatis
```

### Fitur Konfigurasi

- **Template-Based**: Setiap komponen memiliki template konfigurasi YAML
- **Instance-Specific**: Konfigurasi otomatis disesuaikan per instance
- **Property Customization**: Mudah mengubah parameter seperti MCC/MNC, IP, dll.
- **Validation**: Validasi YAML otomatis untuk mencegah error
- **Auto-Cleanup**: Pembersihan konfigurasi otomatis saat container dihapus

### Testing Konfigurasi

```bash
# Test sistem konfigurasi
python test_config_system.py

# Lihat status implementasi lengkap
python config_implementation_summary.py
```

## 🏗️ Arsitektur Sistem

### Komponen Utama:

1. **GUI Layer** (PyQt5):
   - `MainWindow`: Interface utama aplikasi
   - `NetworkCanvas`: Canvas untuk menggambar topologi
   - `TerminalDialog`: Interface akses container terminal
   - `ComponentPanel`: Panel komponen 5G

2. **Simulation Engine**:
   - `NetworkSimulator`: Orchestrator simulasi
   - `EnhancedContainerManager`: Manager Docker container
   - `ComponentFactory`: Factory untuk membuat komponen

3. **Container Infrastructure**:
   - **Open5GS containers**: Core network functions
   - **UERANSIM containers**: gNB dan UE simulation
   - **Custom Docker network**: Isolated 5G network

### Workflow Simulasi:

```
1. User Design Topology (GUI)
   ↓
2. Parse Components & Connections (Simulator)
   ↓
3. Generate Configurations (ConfigManager)
   ↓
4. Deploy Docker Containers (ContainerManager)
   ↓
5. Setup Network & Connectivity
   ↓
6. Open Terminal Access (TerminalDialog)
   ↓
7. Monitor & Test (ResultsDialog)
```

## 🔍 Troubleshooting

### Container Deployment Issues:
```bash
# Check Docker status
docker info

# Check available images
docker images

# Check networks
docker network ls

# Manual cleanup if needed
docker container prune
docker network prune
```

### Python Dependencies:
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Check PyQt5 installation
python -c "from PyQt5.QtWidgets import QApplication; print('PyQt5 OK')"
```

### Access Issues:
- Pastikan Docker Desktop berjalan (Windows)
- Pastikan user dalam group docker (Linux)
- Check firewall/antivirus blocking Docker

## 🧪 Testing 5G Components

### Testing Open5GS Core:
```bash
# Dalam container AMF
curl -X GET http://nrf:7777/nnrf-nfm/v1/nf-instances

# Test database connection
mongosh mongodb://mongodb:27017/open5gs
```

### Testing UERANSIM:
```bash
# Dalam container gNB
ping amf

# Check gNB status
ps aux | grep nr-gnb

# Dalam container UE
ping google.com  # Test internet via 5G
```

## 📁 Struktur Project

```
netflux5g/
├── src/
│   ├── main.py                 # Entry point aplikasi
│   ├── gui/                    # GUI components
│   │   ├── main_window.py      # Main application window
│   │   ├── canvas.py          # Network topology canvas
│   │   ├── terminal_dialog.py  # Container terminal interface
│   │   └── ...
│   ├── simulation/            # Simulation engine
│   │   ├── simulator.py       # Main simulator
│   │   ├── enhanced_container_manager.py  # Docker management
│   │   └── ...
│   ├── models/               # Data models
│   └── utils/               # Utility functions
├── config/                  # Generated configurations
├── requirements.txt        # Python dependencies
├── run_netflux5g.bat      # Windows startup script
└── README.md              # Documentation
```

## 🤝 Contributing

1. Fork repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## 📄 License

MIT License - lihat file LICENSE untuk detail.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/your-repo/netflux5g/issues)
- **Documentation**: [Wiki](https://github.com/your-repo/netflux5g/wiki)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/netflux5g/discussions)

---

**NetFlux5G** - Bringing 5G Network Simulation to Your Desktop! 🚀📡
