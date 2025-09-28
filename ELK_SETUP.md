# ELK Stack Integration for User Management API

This document provides comprehensive instructions for setting up and using the ELK (Elasticsearch, Logstash, Kibana) stack with the User Management API.

## 🏗️ Architecture Overview

The ELK stack integration provides:
- **Elasticsearch**: Centralized log storage and search
- **Logstash**: Log processing and transformation
- **Kibana**: Data visualization and dashboarding
- **Filebeat**: Log file monitoring (optional)

## 📋 Prerequisites

- Docker and Docker Compose
- Python 3.8+
- At least 4GB RAM available for Docker containers

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Or if using virtual environment
source dev/bin/activate
pip install -r requirements.txt
```

### 2. Start ELK Stack

```bash
# Start all ELK services
docker-compose up -d

# Check service status
docker-compose ps
```

### 3. Verify Services

- **Elasticsearch**: http://localhost:9200
- **Kibana**: http://localhost:5601
- **Logstash**: http://localhost:9600

### 4. Run the Application

```bash
# Start the User Management API
python run.py
```

## 📊 Logging Features

### Structured Logging
The application now uses structured JSON logging with the following fields:
- `timestamp`: ISO 8601 timestamp
- `level`: Log level (DEBUG, INFO, WARNING, ERROR)
- `service`: Service name (user-mgt-api)
- `environment`: Environment (development/production)
- `message`: Log message
- Additional context fields based on log type

### Log Types

#### 1. Application Logs
- **File**: `app_events.log`
- **Format**: JSON
- **Content**: General application events, errors, info

#### 2. API Request Logs
- **Index**: `user-mgt-api-requests-YYYY.MM.DD`
- **Content**: HTTP requests, response codes, duration, IP addresses

#### 3. User Action Logs
- **Index**: `user-mgt-user-actions-YYYY.MM.DD`
- **Content**: User CRUD operations with details

#### 4. Error Logs
- **Index**: `user-mgt-errors-YYYY.MM.DD`
- **Content**: Application errors with stack traces

## 🔧 Configuration

### Elasticsearch Configuration
- **Host**: localhost:9200
- **Index Pattern**: `user-mgt-*`
- **Security**: Disabled for development

### Logstash Configuration
- **Inputs**: TCP (5000), UDP (5000), File monitoring
- **Output**: Elasticsearch with daily indices
- **Processing**: JSON parsing, field enrichment

### Kibana Configuration
- **URL**: http://localhost:5601
- **Index Patterns**: Auto-created for `user-mgt-*`
- **Dashboards**: Pre-configured for monitoring

## 📈 Monitoring Dashboards

### 1. API Requests Over Time
- Shows request volume trends
- Identifies peak usage periods
- Monitors API health

### 2. Response Codes Distribution
- HTTP status code breakdown
- Error rate monitoring
- Success/failure ratios

### 3. User Actions Timeline
- User CRUD operation tracking
- Activity patterns
- User engagement metrics

## 🛠️ Advanced Configuration

### Custom Log Processing

To add custom log processing in Logstash, edit:
```bash
elk/logstash/pipeline/logstash.conf
```

### Elasticsearch Index Management

Create custom indices:
```python
from app.elasticsearch.client import es_client

# Create custom index
mapping = {
    "properties": {
        "field_name": {"type": "text"},
        "timestamp": {"type": "date"}
    }
}
es_client.create_index("custom-index", mapping)
```

### Custom Dashboards

Import dashboard configuration:
1. Go to Kibana → Management → Saved Objects
2. Import `elk/kibana/dashboard.json`
3. Configure index patterns

## 🔍 Troubleshooting

### Common Issues

#### 1. Elasticsearch Connection Failed
```bash
# Check Elasticsearch status
curl http://localhost:9200/_cluster/health

# Check logs
docker-compose logs elasticsearch
```

#### 2. Logstash Not Processing Logs
```bash
# Check Logstash status
curl http://localhost:9600/_node/stats

# Check configuration
docker-compose logs logstash
```

#### 3. Kibana Not Loading Data
- Verify index patterns are created
- Check Elasticsearch connectivity
- Ensure data is being indexed

### Health Checks

#### Application Health
```bash
curl http://localhost:8000/health
```

#### Elasticsearch Health
```bash
curl http://localhost:9200/_cluster/health?pretty
```

## 📝 Log Examples

### API Request Log
```json
{
  "timestamp": "2024-01-15T10:30:00.000Z",
  "method": "POST",
  "endpoint": "/api/v1/users/",
  "status_code": 201,
  "duration_ms": 45.2,
  "user_id": 123,
  "ip_address": "192.168.1.100",
  "service": "user-mgt-api",
  "environment": "development"
}
```

### User Action Log
```json
{
  "timestamp": "2024-01-15T10:30:00.000Z",
  "user_id": 123,
  "action": "user_created",
  "service": "user-mgt-api",
  "environment": "development",
  "details": {
    "username": "john_doe",
    "email": "john@example.com",
    "full_name": "John Doe",
    "is_active": true
  }
}
```

## 🚀 Production Considerations

### Security
- Enable Elasticsearch security
- Use authentication for Kibana
- Secure Logstash inputs

### Performance
- Increase Elasticsearch heap size
- Configure index lifecycle management
- Set up log rotation

### Monitoring
- Set up alerts for critical errors
- Monitor disk space usage
- Configure log retention policies

## 📚 Additional Resources

- [Elasticsearch Documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html)
- [Logstash Documentation](https://www.elastic.co/guide/en/logstash/current/index.html)
- [Kibana Documentation](https://www.elastic.co/guide/en/kibana/current/index.html)
- [Filebeat Documentation](https://www.elastic.co/guide/en/beats/filebeat/current/index.html)

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section
2. Review Docker container logs
3. Verify configuration files
4. Check Elasticsearch cluster health
