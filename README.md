# Blue/Green Deployment with Nginx Failover

This repository implements a zero-downtime Blue/Green deployment strategy for Node.js services using Nginx as a reverse proxy with automatic failover capabilities.

## Architecture Overview

```
┌─────────┐
│ Client  │
└────┬────┘
     │ :8080
     ▼
┌─────────────┐
│   Nginx     │ (Reverse Proxy and Load Balancer)
│  Failover   │
└──────┬──────┘
       │
       ├──► app_blue:3000  (Primary/Backup)   :8081
       │
       └──► app_green:3000 (Primary/Backup)   :8082
```

## Features

- **Automatic Failover**: Nginx detects failures and switches to backup within 2-3 seconds
- **Zero Failed Requests**: Retries failed requests to backup server in same client request
- **Health-Based Routing**: Uses tight timeouts and max_fails for quick failure detection
- **Header Forwarding**: Preserves application headers (`X-App-Pool`, `X-Release-Id`)
- **Parameterized Configuration**: Fully configurable via `.env` file


## Manual Setup

- Clone the repository
- Configure .env file
- run


## Test

```bash
# Test normal operation (Blue active)
curl -i http://localhost:8080/version

# Expected response headers:
#200 OK
# X-App-Pool: blue
# X-Release-Id: blue-v1.0.0
```

## Failover Testing

```bash
# 1. Induce chaos on Blue (simulate failure)
curl -X POST http://localhost:8081/chaos/start?mode=error

# 2. Verify automatic switch to Green
  curl http://localhost:8080/version

# Should see all responses from Green with no 500 errors

# 3. Stop chaos
curl -X POST http://localhost:8081/chaos/stop
```


## Nginx Configuration Details

### Failover Settings

- **Timeouts**: 2-3 second timeouts for fast failure detection
- **Max Fails**: 1 failed request marks server as down
- **Fail Timeout**: 2 seconds before retry
- **Retry Policy**: Retries on error, timeout, and HTTP 5xx
- **Max Retries**: Up to 3 attempts across upstreams

### Header Forwarding

All application headers are forwarded to clients:
- `X-App-Pool`: Identifies which pool served the request
- `X-Release-Id`: Identifies the application release version


## Endpoints

### Public Endpoint (via Nginx)
- **http://localhost:8080/version** - Get version info with headers
- **http://localhost:8080/*** - All other application routes

### Direct Access (for chaos testing)
- **http://localhost:8081/** - Blue instance (direct)
- **http://localhost:8082/** - Green instance (direct)

### Chaos Endpoints
- **POST /chaos/start?mode=error** - Return HTTP 500 errors
- **POST /chaos/start?mode=timeout** - Simulate slow responses
- **POST /chaos/stop** - End chaos mode


### Workflow Inputs

```yaml
blue_image: Container image for Blue
green_image: Container image for Green
```
 
