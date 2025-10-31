---
````
# Python Log Watcher  
**Lightweight Blue-Green Deployment Monitoring System**

Monitors **Nginx access logs** and automatically sends **Slack notifications** when upstream error rates breach thresholds or failover events occur.

---

## Overview

- **Nginx reverse proxy** for blue-green traffic routing  
- **Alert Watcher (Python service)** to monitor live log activity  
- **Slack alerts** for real-time visibility into pool flips and error surges  

This project helps developers simulate and monitor chaos events, ensuring resilient deployments and observability across backend pools.

---

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/python-log-watcher.git
cd python-log-watcher
```

### 2. Create Your `.env` File
Add your Slack webhook and other environment variables as needed.

### 3. Start the Stack
```bash
docker-compose up -d --build
```

You should see 4 running containers:
- `nginx`
- `app_blue`
- `app_green`
- `alert_watcher`

---

## Chaos Testing & Failover Simulation

You can simulate failovers or upstream instability using these steps.

### Trigger Chaos on the Blue Pool
```bash
docker exec nginx curl -sS http://app_blue:8080/fail
```

This will:
- Trigger upstream errors in Nginx access logs  
- Be detected by `alert_watcher`  
- Send a Slack alert indicating a pool switch or high error rate

### View Logs in Real Time
```bash
docker-compose logs -f nginx
docker-compose logs -f alert_watcher
```

### Confirm Slack Alerts
Expected notification format:
```
⚠️ Failover Detected: Pool switched from BLUE → GREEN
Error Rate: 2.4% (Threshold: 2.0)
```

---

## Verification Steps

1. Run `docker ps` — ensure all services are up.  
2. Open `http://localhost:8080` — verify that the app responds.  
3. Inject chaos (`app_blue` fail) and confirm Slack alert delivery.  
4. Revert the system by restarting services:  
   ```bash
   docker-compose restart nginx
   ```

---

## Useful Commands

| Action | Command |
|--------|----------|
| Stop all containers | `docker-compose down` |
| Rebuild everything | `docker-compose up -d --build` |
| Tail logs | `docker-compose logs -f` |
| Access Nginx shell | `docker exec -it <nginx_container> sh` |
````



