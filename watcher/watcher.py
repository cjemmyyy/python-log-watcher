#!/usr/bin/env python3
import os, time, re, json
from collections import deque
import requests

LOG_PATH = '/var/log/nginx/access.log'
SLACK_WEBHOOK = os.getenv('SLACK_WEBHOOK_URL')
ERROR_RATE_THRESHOLD = float(os.getenv('ERROR_RATE_THRESHOLD') or 2.0)
WINDOW_SIZE = int(os.getenv('WINDOW_SIZE') or 200)
ALERT_COOLDOWN = int(os.getenv('ALERT_COOLDOWN_SEC') or 300)
MAINTENANCE_MODE = os.getenv('MAINTENANCE_MODE', 'false').lower() == 'true'

# regex to capture fields (matches the 'detailed' format)
LOG_RE = re.compile(r'pool="(?P<pool>[^"]*)" release="(?P<release>[^"]*)" upstream_status="(?P<upstream_status>[^"]*)" upstream_addr="(?P<upstream_addr>[^"]*)" request_time="(?P<request_time>[^"]*)" upstream_response_time="(?P<upstream_response_time>[^"]*)"')

window = deque(maxlen=WINDOW_SIZE)
last_pool = None
last_alert_ts = {'failover': 0, 'error_rate': 0}

def send_slack(text):
    if not SLACK_WEBHOOK:
        print("No SLACK_WEBHOOK_URL configured; skipping alert:", text)
        return
    payload = {"text": text}
    try:
        resp = requests.post(SLACK_WEBHOOK, json=payload, timeout=5)
        resp.raise_for_status()
        print(f"Slack alert sent: {text}", flush=True)
    except Exception as e:
        print("Error sending Slack alert:", e)

def should_alert(kind):
    return (time.time() - last_alert_ts.get(kind, 0)) >= ALERT_COOLDOWN

def record_alert(kind):
    last_alert_ts[kind] = time.time()

def process_line(line):
    global last_pool
    m = LOG_RE.search(line)
    if not m:
        return
    pool = m.group('pool') or None
    release = m.group('release') or None
    upstream_status = m.group('upstream_status') or ''
    upstream_addr = m.group('upstream_addr') or ''
    status_code = None
    try:
        status_code = int(upstream_status.split(',')[0]) if upstream_status else None
    except:
        status_code = None

    is_error = status_code is not None and 500 <= status_code <= 599
    window.append(1 if is_error else 0)

    # failover detection: if pool header present, use it; else try to infer from upstream_addr (simple heuristic)
    current_pool = pool if pool else ( 'blue' if 'app_blue' in upstream_addr or '8081' in upstream_addr else ('green' if 'app_green' in upstream_addr or '8082' in upstream_addr else None) )

    if current_pool and last_pool and current_pool != last_pool:
        if MAINTENANCE_MODE:
            print("Maintenance mode ON — suppressing failover alert")
        else:
            if should_alert('failover'):
                send_slack(f":rotating_light: *Failover detected* — traffic switched from *{last_pool}* → *{current_pool}* (upstream: {upstream_addr}, release: {release})")
                record_alert('failover')
    last_pool = current_pool or last_pool

    # error-rate check
    if len(window) >= 1:
        rate = (sum(window) / len(window)) * 100.0
        if rate >= ERROR_RATE_THRESHOLD:
            if MAINTENANCE_MODE:
                print("Maintenance mode ON — suppressing error-rate alert")
            else:
                if should_alert('error_rate'):
                    send_slack(f":warning: *High upstream error rate* — {rate:.2f}% 5xx over last {len(window)} requests (threshold {ERROR_RATE_THRESHOLD}%).")
                    record_alert('error_rate')

def tail_file(path):
    # basic tail -F implementation
    try:
        with open(path, 'r') as f:
            if f.seekable():
                f.seek(0, 2)
            while True:
                line = f.readline()
                if not line:
                    time.sleep(0.1)
                    continue
                yield line
    except FileNotFoundError:
        print(f"{path} not found; waiting for file to appear...")
        while not os.path.exists(path):
            time.sleep(0.5)
        yield from tail_file(path)

def main():
    print("Watcher starting. WINDOW_SIZE=", WINDOW_SIZE, "THRESHOLD=", ERROR_RATE_THRESHOLD)
    for line in tail_file(LOG_PATH):
        try:
            process_line(line)
        except Exception as e:
            print("Error processing line:", e, flush=True)

if __name__ == '__main__':
    main()
