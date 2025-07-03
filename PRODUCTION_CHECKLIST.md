# NetFlux5G Production Deployment Checklist

## Pre-Deployment Checklist

### System Requirements
- [ ] Operating System: Ubuntu 20.04+ / CentOS 8+ / Windows 10+ with WSL2
- [ ] RAM: Minimum 8GB, Recommended 16GB+
- [ ] Storage: Minimum 50GB free space
- [ ] CPU: Minimum 4 cores, Recommended 8+ cores
- [ ] Network: Internet connectivity for Docker image downloads

### Software Dependencies
- [ ] Docker Engine 20.10+ installed and running
- [ ] Docker Compose 1.29+ installed
- [ ] Python 3.8+ installed
- [ ] Git installed (for version control)

### Security Preparation
- [ ] Create dedicated user account for NetFlux5G service
- [ ] Configure firewall rules (if needed)
- [ ] Review and update default passwords
- [ ] Ensure proper file permissions are set
- [ ] Backup existing configurations

## Deployment Steps

### 1. Environment Setup
- [ ] Download/clone NetFlux5G source code
- [ ] Run health check script: `python scripts/health_check.py`
- [ ] Verify all dependencies are installed
- [ ] Create production configuration file

### 2. Docker Preparation
- [ ] Pull required Docker images:
  - [ ] `openverso/open5gs:latest`
  - [ ] `openverso/ueransim:latest` 
  - [ ] `mongo:4.4`
- [ ] Create Docker networks (if custom networking needed)
- [ ] Verify Docker daemon configuration

### 3. Application Deployment
- [ ] Run deployment script:
  - Linux: `sudo bash scripts/deploy_production.sh`
  - Windows: `scripts/deploy_production.ps1` (as Administrator)
- [ ] Verify installation directory structure
- [ ] Check file permissions and ownership
- [ ] Validate configuration files

### 4. Service Configuration
- [ ] Configure systemd service (Linux) or Windows Service
- [ ] Set up log rotation
- [ ] Configure monitoring (optional)
- [ ] Set up backup procedures

## Post-Deployment Validation

### Functional Testing
- [ ] Run health check: `python scripts/health_check.py`
- [ ] Start NetFlux5G service
- [ ] Verify GUI launches successfully
- [ ] Test basic network topology creation
- [ ] Verify Docker container deployment
- [ ] Test container connectivity

### Performance Testing
- [ ] Monitor CPU usage during operation
- [ ] Monitor memory consumption
- [ ] Check disk I/O performance
- [ ] Verify network performance

### Security Validation
- [ ] Verify service runs with non-root privileges
- [ ] Check firewall configuration
- [ ] Validate file permissions
- [ ] Review log file access

## Production Operations

### Monitoring
- [ ] Set up log monitoring
- [ ] Configure alerts for system resources
- [ ] Monitor Docker container health
- [ ] Track application performance metrics

### Backup Strategy
- [ ] Configuration files backup
- [ ] User data backup
- [ ] Docker image backup (optional)
- [ ] Database backup (if using persistent storage)

### Maintenance
- [ ] Regular Docker image updates
- [ ] System security updates
- [ ] Log rotation and cleanup
- [ ] Performance optimization

## Troubleshooting

### Common Issues
- [ ] Docker daemon not running
- [ ] Insufficient system resources
- [ ] Network connectivity problems
- [ ] Permission issues
- [ ] Configuration file errors

### Support Resources
- [ ] Documentation: `/docs/README.md`
- [ ] Health check script: `scripts/health_check.py`
- [ ] Log files: Check application and system logs
- [ ] GitHub Issues: Report problems and get help

## Production Best Practices

### Security
- [ ] Regular security updates
- [ ] Monitor access logs
- [ ] Use strong authentication
- [ ] Limit network exposure
- [ ] Regular security audits

### Performance
- [ ] Monitor resource usage
- [ ] Optimize container limits
- [ ] Regular cleanup of unused resources
- [ ] Performance tuning based on usage patterns

### Reliability
- [ ] Implement health checks
- [ ] Set up automated restarts
- [ ] Monitor service availability
- [ ] Plan for disaster recovery

## Sign-off

- [ ] System Administrator: _________________ Date: _________
- [ ] Network Administrator: ______________ Date: _________  
- [ ] Security Officer: ___________________ Date: _________
- [ ] Operations Team: ____________________ Date: _________

---

**Note**: This checklist should be customized based on your specific production environment and organizational requirements.
