#!/bin/bash
# NetFlux5G Production Deployment Script

set -e  # Exit on any error

echo "🚀 Starting NetFlux5G Production Deployment..."

# Check if running as root (not recommended for production)
if [ "$EUID" -eq 0 ]; then
    echo "⚠️  Warning: Running as root is not recommended for production"
    read -p "Continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check Docker installation
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check Docker Compose installation
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Verify Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Create production directory structure
echo "📁 Creating production directory structure..."
mkdir -p /opt/netflux5g/{config,logs,data}
mkdir -p /opt/netflux5g/config/{open5gs,ueransim,templates}

# Copy application files
echo "📋 Copying application files..."
cp -r src/ /opt/netflux5g/
cp -r config/ /opt/netflux5g/
cp requirements.txt /opt/netflux5g/
cp production.cfg /opt/netflux5g/

# Set proper permissions
echo "🔒 Setting proper permissions..."
chown -R 1000:1000 /opt/netflux5g
chmod -R 755 /opt/netflux5g
chmod -R 644 /opt/netflux5g/config/*

# Install Python dependencies in virtual environment
echo "🐍 Setting up Python environment..."
python3 -m venv /opt/netflux5g/venv
source /opt/netflux5g/venv/bin/activate
pip install --upgrade pip
pip install -r /opt/netflux5g/requirements.txt

# Pull required Docker images
echo "🐳 Pulling Docker images..."
docker pull openverso/open5gs:latest
docker pull openverso/ueransim:latest
docker pull mongo:4.4

# Create systemd service file
echo "⚙️  Creating systemd service..."
cat > /etc/systemd/system/netflux5g.service << EOF
[Unit]
Description=NetFlux5G 5G Network Simulation Service
After=docker.service
Requires=docker.service

[Service]
Type=simple
User=netflux5g
Group=netflux5g
WorkingDirectory=/opt/netflux5g
Environment=PYTHONPATH=/opt/netflux5g/src
ExecStart=/opt/netflux5g/venv/bin/python src/main.py --config production.cfg
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create netflux5g user
if ! id "netflux5g" &>/dev/null; then
    echo "👤 Creating netflux5g user..."
    useradd -r -s /bin/false -d /opt/netflux5g netflux5g
    chown -R netflux5g:netflux5g /opt/netflux5g
fi

# Add netflux5g user to docker group
usermod -aG docker netflux5g

# Enable and start the service
echo "🔄 Enabling NetFlux5G service..."
systemctl daemon-reload
systemctl enable netflux5g

# Create log rotation configuration
echo "📝 Setting up log rotation..."
cat > /etc/logrotate.d/netflux5g << EOF
/opt/netflux5g/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 netflux5g netflux5g
    postrotate
        systemctl reload netflux5g
    endscript
}
EOF

echo "✅ NetFlux5G has been deployed successfully!"
echo ""
echo "🔧 Management commands:"
echo "  Start service:    systemctl start netflux5g"
echo "  Stop service:     systemctl stop netflux5g"
echo "  Check status:     systemctl status netflux5g"
echo "  View logs:        journalctl -u netflux5g -f"
echo ""
echo "📂 Installation directory: /opt/netflux5g"
echo "📋 Configuration file: /opt/netflux5g/production.cfg"
echo "📝 Log directory: /opt/netflux5g/logs"
echo ""
echo "⚠️  Don't forget to:"
echo "  1. Configure firewall rules if needed"
echo "  2. Set up backup procedures"
echo "  3. Monitor system resources"
echo "  4. Update configuration as needed"
