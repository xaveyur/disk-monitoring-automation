import json
import os
import shutil
import sys
import socket
from datetime import datetime

def load_config(config_path: str) -> dict:
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

def ensure_log_dir(log_file: str) -> None:
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

def log_line(log_file: str, message: str) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"{ts} {message}\n"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(line)
    print(line, end="")

def disk_usage_percent(path: str) -> float:
    total, used, free = shutil.disk_usage(path)
    return (used / total) * 100.0

def main():
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.json"

    if not os.path.exists(config_path):
        print(f"Config not found: {config_path}")
        sys.exit(1)

    config = load_config(config_path)
    threshold = float(config.get("threshold_percent", 80))
    paths = config.get("paths", ["/"])
    log_file = config.get("log_file", "logs/disk_monitor.log")

    ensure_log_dir(log_file)

    for p in paths:
        try:
            hostname = socket.gethostname()

            total, used, free = shutil.disk_usage(p)
            pct = (used / total) * 100

            status = "OK"
            if pct >= threshold:
                status = "ALERT"

            log_line(
                log_file,
                f"[{status}] host={hostname} path={p} "
                f"used={pct:.2f}% total={total//(2**30)}GB "
                f"free={free//(2**30)}GB threshold={threshold:.2f}%"
            )

        except Exception as e:
            log_line(log_file, f"[ERROR] path={p} err={repr(e)}")

if __name__ == "__main__":
    main()