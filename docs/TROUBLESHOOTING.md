# Troubleshooting Guide

## Overview

This comprehensive troubleshooting guide helps you diagnose and resolve common issues encountered during development, deployment, and operation of the project. Use this guide to quickly identify solutions to known problems and learn how to debug new issues.

## Table of Contents

- [Overview](#overview)
- [Quick Diagnostics](#quick-diagnostics)
- [Installation Issues](#installation-issues)
- [Configuration Problems](#configuration-problems)
- [Database Issues](#database-issues)
- [Runtime Errors](#runtime-errors)
- [Performance Problems](#performance-problems)
- [Build and Deployment Issues](#build-and-deployment-issues)
- [Network and Connectivity](#network-and-connectivity)
- [Platform-Specific Issues](#platform-specific-issues)
- [Debugging Tips](#debugging-tips)
- [Getting Help](#getting-help)

## Quick Diagnostics

Before diving into specific issues, run these quick diagnostic checks:

### Health Check Script

```bash
# Check system health
npm run health-check
# or
python manage.py check

# Verify all services are running
npm run verify
# or
python manage.py verify-services
```

### Common Quick Fixes

Try these steps first for most issues:

1. **Restart the application**
   ```bash
   # Stop and restart
   npm restart
   # or
   python manage.py runserver
   ```

2. **Clear caches**
   ```bash
   # Clear application cache
   npm run cache:clear
   # or
   rm -rf __pycache__ .pytest_cache
   ```

3. **Verify environment variables**
   ```bash
   # Check .env file exists
   test -f .env && echo "Found" || echo "Missing"

   # Print environment (sanitized)
   npm run env:check
   ```

4. **Update dependencies**
   ```bash
   # Update all dependencies
   npm update
   # or
   pip install --upgrade -r requirements.txt
   ```

## Installation Issues

### Issue: Package Installation Fails

**Symptoms**: `npm install` or `pip install` terminates with errors

**Common Causes**:
- Network connectivity issues
- Permission problems
- Corrupted package cache
- Incompatible package versions

**Solutions**:

```bash
# Solution 1: Clear cache and retry
npm cache clean --force
rm -rf node_modules package-lock.json
npm install

# For Python
pip cache purge
rm -rf venv
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Solution 2: Use verbose mode to see detailed errors
npm install --verbose
# or
pip install -v -r requirements.txt

# Solution 3: Fix permissions (Unix/Linux/macOS)
sudo chown -R $USER:$GROUP ~/.npm
sudo chown -R $USER:$GROUP node_modules

# Solution 4: Try alternative registry
npm install --registry https://registry.npmjs.org/
# or
pip install --index-url https://pypi.org/simple -r requirements.txt
```

### Issue: Native Module Compilation Fails

**Symptoms**: Errors during installation of packages with native dependencies

**Solutions**:

```bash
# macOS: Install Xcode Command Line Tools
xcode-select --install

# Ubuntu/Debian: Install build essentials
sudo apt-get update
sudo apt-get install build-essential python3-dev

# Windows: Install Windows Build Tools
npm install --global windows-build-tools

# Alternative: Use pre-built binaries
npm install --ignore-scripts
```

### Issue: Version Conflicts

**Symptoms**: `ERESOLVE` errors or dependency version conflicts

**Solutions**:

```bash
# Solution 1: Force resolution (npm 7+)
npm install --legacy-peer-deps

# Solution 2: Update package-lock.json
rm package-lock.json
npm install

# Solution 3: Check for specific version requirements
npm ls <package-name>
# or
pip show <package-name>
```

## Configuration Problems

### Issue: Environment Variables Not Loading

**Symptoms**: Application behaves as if `.env` file doesn't exist

**Diagnosis**:
```bash
# Check if .env file exists
ls -la .env

# Verify .env file format
cat .env | grep -v '^#' | grep -v '^$'
```

**Solutions**:

1. **Verify .env file location**
   ```bash
   # .env should be in project root
   pwd
   ls -la .env
   ```

2. **Check .env file format**
   ```bash
   # Each line should be KEY=value (no spaces around =)
   # Incorrect: KEY = value
   # Correct: KEY=value
   ```

3. **Restart application after changes**
   ```bash
   # Changes to .env require restart
   npm restart
   ```

4. **Verify dotenv package is installed**
   ```bash
   npm list dotenv
   # or
   pip show python-dotenv
   ```

### Issue: Configuration Values Override Not Working

**Symptoms**: Custom configuration values are ignored

**Solutions**:

```bash
# Check configuration precedence order
# Typically: CLI args > Environment vars > .env file > defaults

# Explicitly set environment variable
export NODE_ENV=development
npm start

# Or inline
NODE_ENV=production npm start

# Windows CMD
set NODE_ENV=production && npm start

# Windows PowerShell
$env:NODE_ENV="production"; npm start
```

### Issue: Missing Required Configuration

**Symptoms**: Application crashes with "missing required configuration" error

**Solutions**:

1. **Copy from example file**
   ```bash
   cp .env.example .env
   ```

2. **Verify all required variables are set**
   ```bash
   # Check for required variables
   grep -v '^#' .env | grep -v '^$'
   ```

3. **Use configuration validator**
   ```bash
   npm run config:validate
   # or
   python manage.py check-config
   ```

## Database Issues

### Issue: Cannot Connect to Database

**Symptoms**: `ECONNREFUSED`, `Connection refused`, or timeout errors

**Diagnosis**:
```bash
# Check if database is running
# PostgreSQL
pg_isready -h localhost -p 5432

# MySQL
mysqladmin ping -h localhost

# Check database service status
# macOS
brew services list

# Linux
sudo systemctl status postgresql
sudo systemctl status mysql

# Docker
docker ps | grep postgres
docker ps | grep mysql
```

**Solutions**:

1. **Start database service**
   ```bash
   # PostgreSQL (macOS)
   brew services start postgresql@15

   # PostgreSQL (Linux)
   sudo systemctl start postgresql

   # MySQL (macOS)
   brew services start mysql

   # MySQL (Linux)
   sudo systemctl start mysql

   # Docker
   docker-compose up -d database
   ```

2. **Verify connection string**
   ```bash
   # Check DATABASE_URL format
   # PostgreSQL: postgresql://user:password@host:port/database
   # MySQL: mysql://user:password@host:port/database

   echo $DATABASE_URL
   ```

3. **Test connection manually**
   ```bash
   # PostgreSQL
   psql -h localhost -U your_user -d your_database

   # MySQL
   mysql -h localhost -u your_user -p your_database
   ```

### Issue: Migration Failures

**Symptoms**: Database migrations fail to run or throw errors

**Solutions**:

```bash
# Solution 1: Check migration status
npm run db:migrate:status
# or
python manage.py showmigrations

# Solution 2: Run migrations one at a time
npm run db:migrate:step
# or
python manage.py migrate --plan

# Solution 3: Rollback and retry
npm run db:migrate:rollback
npm run db:migrate
# or
python manage.py migrate <app> <previous_migration>
python manage.py migrate

# Solution 4: Reset migrations (WARNING: destroys data)
npm run db:migrate:reset
# or
python manage.py migrate --fake <app> zero
python manage.py migrate
```

### Issue: Database Locked

**Symptoms**: `database is locked` error (SQLite)

**Solutions**:

```bash
# Close all connections to the database
# Find processes using the database
lsof | grep database.db

# Kill processes if needed
kill -9 <PID>

# Increase timeout in configuration
# SQLite: increase busy_timeout
```

### Issue: Permission Denied on Database Operations

**Symptoms**: `permission denied` errors when accessing database

**Solutions**:

```bash
# PostgreSQL: Grant permissions
psql -U postgres
GRANT ALL PRIVILEGES ON DATABASE your_database TO your_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_user;

# MySQL: Grant permissions
mysql -u root -p
GRANT ALL PRIVILEGES ON your_database.* TO 'your_user'@'localhost';
FLUSH PRIVILEGES;

# Check current user permissions
# PostgreSQL
\du

# MySQL
SHOW GRANTS FOR 'your_user'@'localhost';
```

## Runtime Errors

### Issue: Port Already in Use

**Symptoms**: `EADDRINUSE: address already in use :::3000`

**Solutions**:

```bash
# Find process using the port
# macOS/Linux
lsof -i :3000
netstat -anv | grep 3000

# Kill the process
kill -9 <PID>

# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Alternative: Use different port
PORT=3001 npm start
# or
python manage.py runserver 3001
```

### Issue: Module Not Found

**Symptoms**: `Cannot find module` or `ModuleNotFoundError`

**Solutions**:

```bash
# Solution 1: Reinstall dependencies
rm -rf node_modules
npm install
# or
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Solution 2: Clear module cache
# Node.js
rm -rf node_modules/.cache

# Python
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# Solution 3: Verify module is in dependencies
npm list <module-name>
# or
pip show <module-name>

# Solution 4: Fix import paths
# Check for case sensitivity issues
# Verify relative import paths are correct
```

### Issue: Out of Memory Errors

**Symptoms**: `JavaScript heap out of memory` or `MemoryError`

**Solutions**:

```bash
# Node.js: Increase heap size
export NODE_OPTIONS="--max-old-space-size=4096"
npm start

# Alternative: Set in package.json script
"scripts": {
  "start": "node --max-old-space-size=4096 index.js"
}

# Python: Use memory profiling
pip install memory_profiler
python -m memory_profiler script.py

# General: Monitor memory usage
# macOS/Linux
top
htop

# Windows
taskmgr
```

### Issue: Unhandled Promise Rejections

**Symptoms**: `UnhandledPromiseRejectionWarning` errors

**Solutions**:

```javascript
// Add global error handlers
process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
  // Application specific logging, throwing an error, or other logic
});

// Always add .catch() to promises
fetch(url)
  .then(response => response.json())
  .catch(error => console.error('Fetch error:', error));

// Or use async/await with try/catch
async function fetchData() {
  try {
    const response = await fetch(url);
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Fetch error:', error);
  }
}
```

## Performance Problems

### Issue: Slow Application Startup

**Symptoms**: Application takes excessive time to start

**Diagnosis**:
```bash
# Profile startup time
time npm start

# Enable debug logging
DEBUG=* npm start

# Node.js: Use profiler
node --prof index.js
node --prof-process isolate-*.log
```

**Solutions**:

1. **Optimize imports**
   ```javascript
   // Instead of importing entire library
   import _ from 'lodash';

   // Import only what you need
   import { debounce } from 'lodash';
   ```

2. **Use lazy loading**
   ```javascript
   // Load modules when needed, not at startup
   const module = await import('./heavy-module');
   ```

3. **Check for blocking operations at startup**
   - Move database connections to background
   - Defer non-critical initialization
   - Use connection pooling

### Issue: High Memory Usage

**Symptoms**: Application consumes excessive memory

**Solutions**:

```bash
# Monitor memory usage
# Node.js
node --inspect index.js
# Open chrome://inspect in Chrome

# Python
pip install memory_profiler
python -m memory_profiler script.py

# Check for memory leaks
# Look for growing heap size over time
# Profile with appropriate tools

# Common fixes:
# 1. Clear caches periodically
# 2. Close database connections
# 3. Remove event listeners when done
# 4. Avoid global state accumulation
```

### Issue: Slow Database Queries

**Symptoms**: Application responds slowly, database queries take too long

**Solutions**:

```bash
# Enable query logging
# PostgreSQL: edit postgresql.conf
log_statement = 'all'
log_duration = on

# MySQL: edit my.cnf
general_log = 1
general_log_file = /var/log/mysql/query.log

# Analyze slow queries
# PostgreSQL
EXPLAIN ANALYZE SELECT * FROM table WHERE condition;

# MySQL
EXPLAIN SELECT * FROM table WHERE condition;

# Add indexes
CREATE INDEX idx_column_name ON table_name(column_name);

# Use connection pooling
# Configure pool size in database connection settings
```

## Build and Deployment Issues

### Issue: Build Fails

**Symptoms**: `npm run build` or build process fails

**Solutions**:

```bash
# Clean build artifacts
npm run clean
rm -rf dist build
npm run build

# Increase Node memory for build
export NODE_OPTIONS="--max-old-space-size=8192"
npm run build

# Build with verbose output
npm run build -- --verbose

# Check for TypeScript errors (if applicable)
npm run type-check

# Verify all dependencies are installed
npm ci
```

### Issue: Docker Build Fails

**Symptoms**: `docker build` command fails

**Solutions**:

```bash
# Clean Docker cache
docker builder prune

# Build without cache
docker build --no-cache -t your-app .

# Check Dockerfile syntax
docker build --check -t your-app .

# Build with verbose output
docker build --progress=plain -t your-app .

# Check for .dockerignore issues
cat .dockerignore
```

### Issue: Deployment Fails

**Symptoms**: Application fails to deploy or start in production

**Solutions**:

```bash
# Verify environment variables in production
# Check all required variables are set

# Test production build locally
NODE_ENV=production npm start

# Check logs for errors
# Heroku
heroku logs --tail

# AWS
aws logs tail /aws/lambda/function-name --follow

# Docker
docker logs container-name

# Verify build artifacts
ls -la dist/
# or
ls -la build/
```

## Network and Connectivity

### Issue: API Requests Failing

**Symptoms**: `CORS errors`, `Network error`, or `ERR_CONNECTION_REFUSED`

**Solutions**:

1. **CORS Configuration**
   ```javascript
   // Express.js
   const cors = require('cors');
   app.use(cors({
     origin: 'http://localhost:3000',
     credentials: true
   }));
   ```

2. **Check API endpoint**
   ```bash
   # Test with curl
   curl -v http://localhost:3000/api/endpoint

   # Check if server is running
   netstat -an | grep 3000
   ```

3. **Verify proxy configuration**
   ```json
   // package.json (React)
   {
     "proxy": "http://localhost:3001"
   }
   ```

### Issue: SSL/TLS Certificate Errors

**Symptoms**: `CERT_HAS_EXPIRED`, `SELF_SIGNED_CERT_IN_CHAIN`

**Solutions**:

```bash
# Development: Disable SSL verification (NOT for production)
# Node.js
export NODE_TLS_REJECT_UNAUTHORIZED=0

# Python
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# Production: Update certificates
# Let's Encrypt renewal
sudo certbot renew

# Check certificate expiration
openssl x509 -in certificate.crt -noout -enddate
```

## Platform-Specific Issues

### macOS Issues

**Issue: Command not found after installation**
```bash
# Add to PATH
export PATH="/usr/local/bin:$PATH"

# Reload shell
source ~/.zshrc
# or
source ~/.bash_profile
```

**Issue: Permission denied on /usr/local**
```bash
# Fix Homebrew permissions
sudo chown -R $(whoami) /usr/local
```

### Windows Issues

**Issue: Scripts disabled**
```powershell
# Enable script execution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Issue: Line ending issues**
```bash
# Configure Git to handle line endings
git config --global core.autocrlf true
```

### Linux Issues

**Issue: Permission denied on Docker**
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Logout and login again, or
newgrp docker
```

**Issue: Port below 1024 requires root**
```bash
# Use port >= 1024, or
# Grant capability to bind to privileged ports
sudo setcap 'cap_net_bind_service=+ep' /path/to/binary
```

## Debugging Tips

### Enable Debug Mode

```bash
# Node.js
DEBUG=* npm start

# Python
export DEBUG=True
python manage.py runserver

# Application-specific debug flag
export LOG_LEVEL=debug
npm start
```

### Use Interactive Debugger

```bash
# Node.js
node --inspect index.js
# Open chrome://inspect

# Python
python -m pdb script.py

# Or add breakpoint in code
import pdb; pdb.set_trace()  # Python
debugger;  // JavaScript
```

### Check Logs

```bash
# Application logs
tail -f logs/app.log

# System logs
# macOS
log show --predicate 'process == "node"' --info

# Linux
journalctl -u your-service -f

# Docker
docker logs -f container-name
```

### Network Debugging

```bash
# Check network connectivity
ping example.com

# Test DNS resolution
nslookup example.com
dig example.com

# Trace route
traceroute example.com

# Check open ports
netstat -tuln

# Monitor network traffic
tcpdump -i any port 3000
```

## Getting Help

### Before Asking for Help

1. **Search existing issues**
   - Check [GitHub Issues](https://github.com/your-org/your-project/issues)
   - Search [Stack Overflow](https://stackoverflow.com/questions/tagged/your-project)

2. **Gather diagnostic information**
   ```bash
   # Collect system information
   node --version
   npm --version
   # or
   python --version
   pip --version

   # OS information
   uname -a  # Unix/Linux/macOS
   systeminfo  # Windows

   # Environment details
   env | grep NODE
   env | grep PYTHON
   ```

3. **Create minimal reproduction**
   - Isolate the issue
   - Remove unnecessary code
   - Test in clean environment

### How to Report Issues

When reporting issues, include:

1. **Environment details**
   - OS and version
   - Runtime version (Node.js, Python, etc.)
   - Package versions

2. **Steps to reproduce**
   - Exact commands run
   - Configuration used
   - Sample code or data

3. **Expected vs actual behavior**
   - What should happen
   - What actually happens
   - Error messages (full stack trace)

4. **What you've tried**
   - Solutions attempted
   - Relevant logs
   - Screenshots if applicable

### Support Channels

- **GitHub Issues**: [Report bugs and request features](https://github.com/your-org/your-project/issues)
- **GitHub Discussions**: [Ask questions and discuss](https://github.com/your-org/your-project/discussions)
- **Stack Overflow**: Tag questions with `your-project`
- **Community Chat**: [Discord/Slack](https://chat.example.com)
- **Email Support**: support@example.com

## Additional Resources

### Documentation

- [README.md](../README.md) - Project overview and quick start
- [SETUP.md](SETUP.md) - Detailed setup instructions
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [API.md](API.md) - API documentation
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Contribution guidelines

### External Resources

- [Official Documentation](https://docs.example.com)
- [Knowledge Base](https://kb.example.com)
- [Video Tutorials](https://example.com/tutorials)
- [Community Forum](https://community.example.com)

---

**Note**: This troubleshooting guide is continuously updated. If you encounter an issue not covered here, please contribute a solution via pull request.

**Last Updated**: [Date]
**Maintained By**: [Team/Person responsible]
**Contributions**: Submit improvements via [GitHub](https://github.com/your-org/your-project)

For general contribution guidelines, see [CONTRIBUTING.md](../CONTRIBUTING.md).
