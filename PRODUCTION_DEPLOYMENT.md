# NetFlux5G Production Deployment Guide

This guide provides step-by-step instructions for deploying NetFlux5G in a production environment.

## Quick Start

### 1. Prerequisites Check
Run the health check script to verify your system is ready:
```bash
python scripts/health_check.py
```

### 2. Deploy to Production

**Linux/macOS:**
```bash
sudo bash scripts/deploy_production.sh
```

**Windows (Run as Administrator):**
```powershell
.\scripts\deploy_production.ps1
```

### 3. Verify Deployment
```bash
python scripts/health_check.py --json
```

## Production Configuration

### Configuration File
The production configuration is stored in `production.cfg`:

```ini
[logging]
level = INFO
log_to_console = False
log_file = netflux5g_production.log

[security]
debug_mode = False
enable_debug_toolbar = False

[performance]
enable_caching = True
max_containers = 100
container_timeout = 300
```

### Environment Variables
Set these environment variables for production:

```bash
export NETFLUX5G_ENV=production
export NETFLUX5G_LOG_LEVEL=INFO
export NETFLUX5G_CONFIG_PATH=/opt/netflux5g/production.cfg
```

## Production Features

### Security Enhancements
- Debug mode disabled
- Production logging level (INFO instead of DEBUG)
- Secure file permissions
- Non-root user execution
- Debug print statements removed

### Performance Optimizations
- Optimized logging configuration
- Container resource limits
- Caching enabled
- Memory usage monitoring

### Monitoring & Health Checks
- Automated health check script
- System resource monitoring
- Container status tracking
- Log rotation configured

## File Structure (Production)

```
/opt/netflux5g/                 # Linux production directory
├── src/                        # Application source code
├── config/                     # Configuration files
├── logs/                       # Log files
├── data/                       # Persistent data
├── venv/                       # Python virtual environment
├── production.cfg              # Production configuration
└── scripts/                    # Management scripts
    ├── health_check.py         # Health monitoring
    ├── deploy_production.sh    # Linux deployment
    └── deploy_production.ps1   # Windows deployment
```

## Management Commands

### Service Management (Linux with systemd)
```bash
# Start the service
sudo systemctl start netflux5g

# Stop the service
sudo systemctl stop netflux5g

# Check service status
sudo systemctl status netflux5g

# View logs
sudo journalctl -u netflux5g -f
```

### Manual Management
```bash
# Activate virtual environment
source /opt/netflux5g/venv/bin/activate

# Start application
python src/main.py --config production.cfg

# Run health check
python scripts/health_check.py
```

## Monitoring

### Health Checks
Regular health checks ensure system reliability:

```bash
# Basic health check
python scripts/health_check.py

# JSON output for monitoring systems
python scripts/health_check.py --json

# Automated monitoring (add to cron)
*/5 * * * * /opt/netflux5g/venv/bin/python /opt/netflux5g/scripts/health_check.py --json >> /opt/netflux5g/logs/health.log
```

### Log Monitoring
Monitor application logs for issues:

```bash
# View application logs
tail -f /opt/netflux5g/logs/netflux5g_production.log

# View system logs
sudo journalctl -u netflux5g -f

# Search for errors
grep -i error /opt/netflux5g/logs/*.log
```

## Backup & Recovery

### Configuration Backup
```bash
# Backup configuration
tar -czf netflux5g_config_$(date +%Y%m%d).tar.gz config/

# Backup entire installation
tar -czf netflux5g_backup_$(date +%Y%m%d).tar.gz /opt/netflux5g/
```

### Recovery
```bash
# Restore configuration
tar -xzf netflux5g_config_YYYYMMDD.tar.gz

# Restart service after restore
sudo systemctl restart netflux5g
```

## Troubleshooting

### Common Issues

1. **Service won't start**
   ```bash
   # Check logs
   sudo journalctl -u netflux5g -n 50
   
   # Verify configuration
   python -c "import yaml; yaml.safe_load(open('production.cfg'))"
   ```

2. **Docker containers fail to start**
   ```bash
   # Check Docker status
   docker info
   
   # Verify images
   docker images | grep -E "(open5gs|ueransim|mongo)"
   ```

3. **High resource usage**
   ```bash
   # Monitor resources
   htop
   docker stats
   
   # Check container limits
   python scripts/health_check.py
   ```

### Getting Help

1. Check the [Production Checklist](PRODUCTION_CHECKLIST.md)
2. Run the health check script
3. Review application logs
4. Check the main documentation
5. Report issues on GitHub

## Security Considerations

### Network Security
- Configure firewall rules appropriately
- Limit network exposure of Docker containers
- Use secure container images
- Regular security updates

### File Security
- Proper file permissions (644 for files, 755 for directories)
- Non-root user execution
- Secure log file access
- Configuration file protection

### Access Control
- Dedicated service user account
- Limited sudo privileges
- Audit user access
- Regular permission reviews

## Performance Tuning

### System Resources
- Monitor CPU and memory usage
- Adjust container resource limits
- Optimize Docker daemon settings
- Configure swap if needed

### Application Performance
- Tune logging levels
- Optimize container startup time
- Monitor network performance
- Regular cleanup of unused resources

---

For detailed deployment procedures, see [PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md)
