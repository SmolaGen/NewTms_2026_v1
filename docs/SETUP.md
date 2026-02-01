# Setup Instructions

## Overview

This guide provides comprehensive instructions for setting up and configuring the project for development, testing, and production environments. Follow these steps to get your environment ready for working with the project.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Environment Setup](#environment-setup)
- [Database Setup](#database-setup)
- [Verification](#verification)
- [Development Tools](#development-tools)
- [Deployment Setup](#deployment-setup)
- [Common Issues](#common-issues)
- [Next Steps](#next-steps)

## Prerequisites

Before beginning the setup process, ensure you have the following installed and configured:

### Required Software

- **Operating System**: macOS, Linux, or Windows 10/11 with WSL2
- **Runtime Environment**: [Specify runtime, e.g., Node.js 18+, Python 3.10+, etc.]
- **Package Manager**: [npm, yarn, pip, etc.]
- **Version Control**: Git 2.30 or higher
- **Database**: [Specify database system and version if applicable]

### Optional Tools

- **IDE/Editor**: VS Code, IntelliJ IDEA, or similar (recommended)
- **Container Platform**: Docker 20.10+ and Docker Compose 2.0+ (optional but recommended)
- **API Client**: Postman, Insomnia, or curl for testing API endpoints

### System Requirements

**Minimum:**
- CPU: 2 cores
- RAM: 4 GB
- Disk Space: 1 GB free

**Recommended:**
- CPU: 4+ cores
- RAM: 8+ GB
- Disk Space: 5+ GB free

### Account Requirements

- [Cloud service account if applicable]
- [API keys or service credentials if needed]
- [Database hosting account if using external database]

## Installation

### Step 1: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/your-org/your-project.git

# Navigate to the project directory
cd your-project

# Checkout the appropriate branch (if not main)
git checkout develop
```

### Step 2: Install Dependencies

#### Option A: Using Package Manager

```bash
# Install project dependencies
npm install
# or
yarn install
# or
pip install -r requirements.txt
```

#### Option B: Using Docker (Recommended)

```bash
# Build the Docker image
docker-compose build

# Start the containers
docker-compose up -d
```

### Step 3: Verify Installation

```bash
# Check installed version
npm --version
# or
python --version

# Verify dependencies are installed
npm list
# or
pip list
```

## Configuration

### Environment Variables

Create a `.env` file in the project root directory:

```bash
# Copy the example environment file
cp .env.example .env
```

#### Required Environment Variables

Edit the `.env` file and configure the following variables:

```bash
# Application Configuration
NODE_ENV=development
PORT=3000
APP_NAME=YourProjectName

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=your_database
DATABASE_USER=your_user
DATABASE_PASSWORD=your_password

# Authentication & Security
SECRET_KEY=your-secret-key-here
JWT_SECRET=your-jwt-secret-here
SESSION_SECRET=your-session-secret-here
ENCRYPTION_KEY=your-encryption-key

# API Configuration
API_BASE_URL=http://localhost:3000/api
API_VERSION=v1
API_KEY=your-api-key-here

# External Services
REDIS_URL=redis://localhost:6379
CACHE_TTL=3600

# Email Configuration (if applicable)
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=your-email@example.com
SMTP_PASSWORD=your-email-password
EMAIL_FROM=noreply@example.com

# Logging
LOG_LEVEL=debug
LOG_FILE=logs/app.log

# Feature Flags
ENABLE_FEATURE_X=true
ENABLE_ANALYTICS=false
```

#### Environment-Specific Configuration

**Development:**
```bash
NODE_ENV=development
DEBUG=true
LOG_LEVEL=debug
```

**Staging:**
```bash
NODE_ENV=staging
DEBUG=false
LOG_LEVEL=info
```

**Production:**
```bash
NODE_ENV=production
DEBUG=false
LOG_LEVEL=error
ENABLE_MONITORING=true
```

### Configuration Files

#### Application Configuration

Create or edit `config/default.json`:

```json
{
  "app": {
    "name": "Your Application",
    "version": "1.0.0",
    "port": 3000
  },
  "database": {
    "poolSize": 10,
    "timeout": 30000
  },
  "security": {
    "cors": {
      "enabled": true,
      "origins": ["http://localhost:3000"]
    },
    "rateLimit": {
      "windowMs": 900000,
      "max": 100
    }
  }
}
```

#### Service Configuration

Configure external services (if applicable):

```yaml
# docker-compose.yml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=development
    volumes:
      - .:/app
    depends_on:
      - database
      - redis

  database:
    image: postgres:15
    environment:
      POSTGRES_DB: your_database
      POSTGRES_USER: your_user
      POSTGRES_PASSWORD: your_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

## Environment Setup

### Development Environment

#### Step 1: Setup Development Database

```bash
# Create database
createdb your_database

# Run migrations
npm run db:migrate
# or
python manage.py migrate

# Seed database with sample data
npm run db:seed
# or
python manage.py seed
```

#### Step 2: Install Development Tools

```bash
# Install development dependencies
npm install --save-dev

# Install pre-commit hooks
npm run setup:hooks
# or
pre-commit install
```

#### Step 3: Configure IDE

**VS Code Settings** (`.vscode/settings.json`):

```json
{
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "eslint.validate": ["javascript", "typescript"],
  "[javascript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  }
}
```

**Recommended VS Code Extensions:**
- ESLint
- Prettier
- GitLens
- Docker
- [Language-specific extensions]

### Testing Environment

```bash
# Setup test database
createdb your_database_test

# Run tests to verify setup
npm test
# or
pytest

# Run with coverage
npm run test:coverage
# or
pytest --cov
```

### Production Environment

#### Cloud Deployment Setup

**Environment Variables:**
Set the following in your hosting platform (Heroku, AWS, GCP, Azure, etc.):

```bash
# Production environment variables
NODE_ENV=production
DATABASE_URL=<production-database-url>
SECRET_KEY=<strong-random-secret>
API_KEY=<production-api-key>
```

#### SSL/TLS Configuration

```bash
# Generate SSL certificates (if self-hosting)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout private.key -out certificate.crt
```

#### Process Manager Setup

```bash
# Install PM2 (for Node.js)
npm install -g pm2

# Start application with PM2
pm2 start ecosystem.config.js

# Save PM2 configuration
pm2 save

# Setup PM2 startup script
pm2 startup
```

## Database Setup

### Initial Database Configuration

#### PostgreSQL Setup

```bash
# Install PostgreSQL (if not using Docker)
# macOS
brew install postgresql@15

# Ubuntu/Debian
sudo apt-get install postgresql-15

# Start PostgreSQL service
# macOS
brew services start postgresql@15

# Ubuntu/Debian
sudo systemctl start postgresql

# Create database user
createuser -P your_user

# Create database
createdb -O your_user your_database
```

#### MySQL Setup

```bash
# Install MySQL (if not using Docker)
# macOS
brew install mysql

# Ubuntu/Debian
sudo apt-get install mysql-server

# Secure installation
mysql_secure_installation

# Create database and user
mysql -u root -p
CREATE DATABASE your_database;
CREATE USER 'your_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON your_database.* TO 'your_user'@'localhost';
FLUSH PRIVILEGES;
```

### Database Migrations

```bash
# Create migration
npm run db:migrate:create <migration-name>
# or
python manage.py makemigrations

# Run pending migrations
npm run db:migrate
# or
python manage.py migrate

# Rollback last migration
npm run db:migrate:rollback
# or
python manage.py migrate <app> <previous-migration>

# Reset database (WARNING: destroys all data)
npm run db:reset
# or
python manage.py flush
```

### Database Seeding

```bash
# Run seeders
npm run db:seed
# or
python manage.py loaddata seed_data.json

# Create custom seed data
npm run db:seed:make <seeder-name>
# or
python manage.py dumpdata > seed_data.json
```

## Verification

### Verify Installation

Run the following commands to verify your setup:

```bash
# Check application starts successfully
npm start
# or
python manage.py runserver

# Expected output:
# Server running on http://localhost:3000
# Database connected successfully
# All services initialized
```

### Health Check

```bash
# Test health endpoint
curl http://localhost:3000/health

# Expected response:
# {
#   "status": "ok",
#   "database": "connected",
#   "redis": "connected",
#   "uptime": 123
# }
```

### Run Test Suite

```bash
# Run all tests
npm test
# or
pytest

# Run specific test categories
npm run test:unit
npm run test:integration
npm run test:e2e

# Expected output: All tests passing
```

### Verify Database Connection

```bash
# Test database connectivity
npm run db:ping
# or
python manage.py dbshell

# Expected: Successful connection message
```

## Development Tools

### Code Quality Tools

#### Linting

```bash
# Run linter
npm run lint
# or
flake8 .

# Auto-fix issues
npm run lint:fix
# or
autopep8 --in-place --recursive .
```

#### Code Formatting

```bash
# Format code
npm run format
# or
black .

# Check formatting
npm run format:check
# or
black --check .
```

#### Type Checking (if applicable)

```bash
# Run type checker
npm run type-check
# or
mypy .
```

### Debugging Tools

#### Debug Mode

```bash
# Run in debug mode
DEBUG=* npm start
# or
python -m pdb manage.py runserver
```

#### Logging

```bash
# Enable verbose logging
LOG_LEVEL=debug npm start

# View logs
tail -f logs/app.log
```

### Performance Profiling

```bash
# Profile application
npm run profile
# or
python -m cProfile manage.py runserver
```

## Deployment Setup

### Build for Production

```bash
# Create production build
npm run build
# or
python setup.py build

# Verify build
npm run build:verify
```

### Container Deployment

```bash
# Build production Docker image
docker build -t your-app:latest .

# Run production container
docker run -p 3000:3000 --env-file .env.production your-app:latest

# Push to container registry
docker tag your-app:latest registry.example.com/your-app:latest
docker push registry.example.com/your-app:latest
```

### Platform-Specific Deployment

#### Heroku

```bash
# Login to Heroku
heroku login

# Create application
heroku create your-app-name

# Add database
heroku addons:create heroku-postgresql:hobby-dev

# Set environment variables
heroku config:set NODE_ENV=production
heroku config:set SECRET_KEY=your-secret

# Deploy
git push heroku main

# Run migrations
heroku run npm run db:migrate
```

#### AWS / GCP / Azure

See platform-specific deployment documentation:
- [AWS Deployment Guide](deployment/aws.md)
- [GCP Deployment Guide](deployment/gcp.md)
- [Azure Deployment Guide](deployment/azure.md)

## Common Issues

### Issue: Dependencies Installation Failed

**Problem:** `npm install` or `pip install` fails with errors.

**Solutions:**
```bash
# Clear package cache
npm cache clean --force
# or
pip cache purge

# Delete node_modules/venv and reinstall
rm -rf node_modules
npm install
# or
rm -rf venv
python -m venv venv && source venv/bin/activate && pip install -r requirements.txt
```

### Issue: Database Connection Failed

**Problem:** Application cannot connect to database.

**Solutions:**
1. Verify database is running: `pg_isready` or `systemctl status postgresql`
2. Check connection string in `.env`
3. Verify database user permissions
4. Check firewall rules and network connectivity

### Issue: Port Already in Use

**Problem:** `Error: listen EADDRINUSE: address already in use :::3000`

**Solutions:**
```bash
# Find process using the port
lsof -i :3000
# or
netstat -ano | findstr :3000

# Kill the process
kill -9 <PID>
# or use different port
PORT=3001 npm start
```

### Issue: Environment Variables Not Loading

**Problem:** Application not reading `.env` file.

**Solutions:**
1. Verify `.env` file exists in project root
2. Check `.env` file syntax (no quotes needed for most values)
3. Restart application after changing `.env`
4. Ensure `dotenv` package is installed

### Issue: Migration Errors

**Problem:** Database migrations fail to run.

**Solutions:**
```bash
# Reset migrations (WARNING: destroys data)
npm run db:migrate:reset

# Run migrations one at a time
npm run db:migrate:step

# Check migration status
npm run db:migrate:status
```

For more troubleshooting help, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

## Next Steps

Now that your environment is set up:

1. **Read the Documentation**
   - [README.md](../README.md) - Project overview
   - [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
   - [API.md](API.md) - API documentation
   - [CONTRIBUTING.md](../CONTRIBUTING.md) - Contribution guidelines

2. **Start Development**
   - Create a feature branch: `git checkout -b feature/your-feature`
   - Write code following project conventions
   - Run tests: `npm test`
   - Submit a pull request

3. **Join the Community**
   - [Community Forum](https://community.example.com)
   - [Slack/Discord Channel](https://chat.example.com)
   - [Stack Overflow Tag](https://stackoverflow.com/questions/tagged/your-project)

4. **Stay Updated**
   - Watch the repository for updates
   - Subscribe to release notifications
   - Follow the changelog

## Additional Resources

### Documentation

- [Setup Video Tutorial](https://example.com/setup-video)
- [Quick Start Guide](../README.md#quick-start)
- [Configuration Reference](docs/configuration.md)
- [Deployment Guide](docs/deployment.md)

### Support

- **Issues**: Report bugs or request features on [GitHub Issues](https://github.com/your-org/your-project/issues)
- **Discussions**: Ask questions on [GitHub Discussions](https://github.com/your-org/your-project/discussions)
- **Email**: support@example.com
- **Community**: [Community forum](https://community.example.com)

### Learning Resources

- [Official Documentation](https://docs.example.com)
- [API Reference](API.md)
- [Video Tutorials](https://example.com/tutorials)
- [Example Projects](https://github.com/your-org/examples)

---

**Note**: This setup guide should be updated as the project evolves. If you encounter issues not covered here, please contribute improvements to this documentation.

**Last Updated**: [Date]
**Maintained By**: [Team/Person responsible]
**Feedback**: Submit documentation improvements via pull request

For general contribution guidelines, see [CONTRIBUTING.md](../CONTRIBUTING.md).
