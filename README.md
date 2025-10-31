````{"id":"94710","variant":"standard","title":"README for Python Log Launcher"}

A lightweight blue-green deployment monitoring system that tracks **Nginx access logs** and automatically sends **Slack notifications** when upstream error rates breach thresholds or failover events occur.

---

## Overview

- **Nginx reverse proxy** for blue-green traffic routing  
- **Alert Watcher (Python service)** to monitor log activity  
- **Slack notifications** for real-time visibility into pool flips and error surges

This project helps developers simulate and monitor **chaos events**, ensuring resilient deployments and observability across backend pools.

---

---

## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/python-log-watcher.git
cd python-log-watcher
```

### 2. Create your `.env` file

### 3. Start the stack
```bash
docker-compose up -d --build
```

You should see 4 running containers:
- `nginx`
- `app_blue`
- `app_green`
- `alert_watcher`

---

##  Chaos Testing & Failover Simulation

You can simulate failovers or upstream instability using these steps:

### Trigger Chaos on Blue Pool
```bash
docker exec nginx curl -sS http://app_blue:8080/fail
```

This should:
- Trigger errors in Nginx access logs  
- Be detected by `alert_watcher`  
- Send a Slack alert indicating **pool switch or high error rate**

### Verify Logs
View live logs for each service:
```bash
docker-compose logs -f nginx
docker-compose logs -f alert_watcher
```

### Confirm Slack Alerts
Check your Slack channel for notifications similar to:
```
⚠️ Failover Detected: Pool switched from BLUE → GREEN
Error Rate: 2.4% (Threshold: 2.0)
```

---

##  Verification Steps

1. Run `docker ps` — ensure all services are up.  
2. Open `http://localhost:8080` — verify app responds.  
3. Inject chaos (fail `app_blue`) and observe Slack alert.  
4. Revert by restarting services:  
   ```bash
   docker-compose restart nginx
   ```

---

## 🧰 Useful Commands

| Action | Command |
|--------|----------|
| Stop all containers | `docker-compose down` |
| Rebuild everything | `docker-compose up -d --build` |
| Tail logs | `docker-compose logs -f` |
| Access Nginx shell | `docker exec -it <nginx_container> sh` |

---
