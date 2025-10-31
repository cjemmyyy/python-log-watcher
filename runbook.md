# Runbook 

This runbook provides operational guidance for managing, testing, and troubleshooting the **Python Log Launcher** blue-green monitoring system.

---

## 1. System Overview

**Purpose:**  
Monitor Nginx access logs, detect failover or abnormal upstream error rates, and send alerts to Slack.

**Core Components:**
| Component | Description |
|------------|--------------|
| `nginx` | Reverse proxy routing between blue and green pools |
| `app_blue` | Active deployment pool |
| `app_green` | Standby/backup deployment pool |
| `alert_watcher` | Python service tailing Nginx logs and posting alerts to Slack |

**Alert Trigger Conditions:**
- Error rate exceeds defined `THRESHOLD` (e.g. 2.0%)
- Active pool changes (failover event detected)

---

## 2. Deployment & Startup

### a. Environment Setup
Ensure `.env` exists in the project root:

### b. Build and Run Containers
```bash
docker-compose up -d --build
```

Expected containers:
```
nginx
app_blue
app_green
alert_watcher
```

### c. Verify Service Health
```bash
docker ps
docker-compose logs -f nginx
docker-compose logs -f alert_watcher
```

---

## 3. Chaos Testing & Failover Simulation

Simulate traffic or upstream errors to validate system behavior.

### a. Trigger Chaos
Inject failure into the active pool:
```bash
docker exec nginx curl -sS http://app_blue:8080/fail
```

### b. Observe Logs
Monitor logs for error spikes or pool flips:
```bash
docker-compose logs -f alert_watcher
```

Expected output (simplified):
```
Detected pool flip: blue → green
Error rate = 2.8% (Threshold = 2.0)
```

### c. Confirm Slack Notification
Open the Slack channel configured in `SLACK_WEBHOOK_URL` and confirm alert message appears:
```
⚠️ Failover Detected: BLUE → GREEN
Error Rate: 2.8% (Threshold: 2.0)
```

---

## 4. Detection & Diagnosis

### Symptom A: No Slack Alerts
**Checkpoints:**
1. Verify watcher is running:
   ```bash
   docker ps | grep alert_watcher
   ```
2. Ensure `SLACK_WEBHOOK_URL` is valid.
3. Check logs:
   ```bash
   docker-compose logs -f alert_watcher
   ```
4. Confirm Nginx is writing to `/var/log/nginx/access.log`.

---

### Symptom B: Watcher Exits Unexpectedly
**Checkpoints:**
1. View container logs for Python errors.
2. If `io.UnsupportedOperation` appears:
   - Ensure Nginx writes logs to a real file, not `/dev/stdout`.
3. Restart container:
   ```bash
   docker-compose restart alert_watcher
   ```

---

### Symptom C: Nginx Not Routing Traffic
**Checkpoints:**
1. Validate upstream configuration:
   ```bash
   docker exec -it nginx cat /etc/nginx/nginx.conf
   ```
2. Test endpoints:
   ```bash
   curl -v http://localhost:8080
   ```

---

## 5. Recovery & Failback

If a failover event occurs and you want to revert manually:

```bash
docker-compose restart nginx
```

or reassign the active pool in `.env`:
```
ACTIVE_POOL=blue
```
Then rebuild:
```bash
docker-compose up -d --build
```

---

## 6. Verification Checklist

| Step | Check |
|------|--------|
| 1 | All containers running |
| 2 | Nginx serving traffic on port 8080 |
| 3 | Watcher logs show active monitoring |
| 4 | Chaos test triggers Slack notification |
| 5 | Failback restores original active pool |

---

## 7. Observability Notes

- Logs are tailed live from `/var/log/nginx/access.log`.  
- Rolling window size and thresholds can be tuned via env vars:
  ```
  WINDOW_SIZE=200
  THRESH=2.0
  ```
- To adjust frequency or sensitivity, modify `watcher.py` parameters.

---

## 8. Cleanup

To stop and remove all services:
```bash
docker-compose down
```

To remove all volumes and networks:
```bash
docker system prune -af
```

---
