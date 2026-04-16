
import os
import subprocess
import datetime

brief_json_path = "/tmp/hermes_brief.json"
publish_script_path = "/home/jim-rauch/daymark/hermes_publish.py"
log_file = "/tmp/daymark_publish_automation.log"

def log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a") as f:
        f.write(f"{timestamp} - {message}\n")
    print(f"{timestamp} - {message}") # Also print to stdout for cron job log

if os.path.exists(brief_json_path):
    log(f"Found {brief_json_path}. Attempting to publish.")
    try:
        result = subprocess.run(
            ["python3", publish_script_path, "--type", "brief", "--input", brief_json_path],
            capture_output=True, text=True, check=True
        )
        log(f"Publish successful: stdout={result.stdout.strip()}, stderr={result.stderr.strip()}")
        open('/tmp/hermes_last_publish', 'w').close()
        log("Updated hermes_last_publish timestamp.")
        # Optionally, remove the /tmp/hermes_brief.json after successful publishing
        # os.remove(brief_json_path)
        # log(f"Removed {brief_json_path}")
    except subprocess.CalledProcessError as e:
        log(f"Publish failed: {e}. stdout={e.stdout.strip()}, stderr={e.stderr.strip()}")
    except Exception as e:
        log(f"An unexpected error occurred during publishing: {e}")
else:
    log(f"{brief_json_path} not found. Skipping publish.")

