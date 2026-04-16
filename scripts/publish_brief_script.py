import os
import subprocess
import datetime
import json

print("DEBUG: Script started.") # Added debug print

brief_json_path = "/tmp/hermes_brief.json"
forecast_json_path = "/tmp/hermes_forecast.json"
publish_script_path = "/home/jim-rauch/daymark/hermes_publish.py"
log_file = "/tmp/daymark_publish_automation.log"

def log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a") as f:
        f.write(f"{timestamp} - {message}\n")
    print(f"LOG: {timestamp} - {message}") # Changed to LOG: for easier identification

print(f"DEBUG: Log file set to {log_file}") # Added debug print

def default_brief_content():
    return {
        "date": datetime.date.today().strftime("%Y-%m-%d"),
        "alert": None,
        "dashboard": [],
        "indicators": [],
        "sections": []
    }

def default_forecast_content():
    return {
        "date": datetime.date.today().strftime("%Y-%m-%d"),
        "landscape": "No forecast available.",
        "scenarios": [],
        "items": [],
        "week": "No forecast available for the next 7 days.",
        "month": "No forecast available for the next 30 days.",
        "sixmonth": "No forecast available for the next 180 days.",
        "practical_prep": "No practical preparation advice available."
    }

def ensure_dummy_json(file_path, content_type):
    print(f"DEBUG: ensure_dummy_json called for {file_path}") # Added debug print
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        log(f"Warning: {file_path} not found or empty. Creating dummy content.")
        dummy_content = {}
        if content_type == "brief":
            dummy_content = default_brief_content()
        elif content_type == "forecast":
            dummy_content = default_forecast_content()
        
        with open(file_path, "w") as f:
            json.dump(dummy_content, f, indent=4)
            log(f"Dummy {content_type} content written to {file_path}.")
    else:
        print(f"DEBUG: {file_path} already exists and is not empty.") # Added debug print

def publish_content(content_type, input_path):
    print(f"DEBUG: publish_content called for {content_type} with input {input_path}") # Added debug print
    ensure_dummy_json(input_path, content_type)
    log(f"Attempting to publish {content_type} from {input_path}.")
    try:
        result = subprocess.run(
            ["python3", publish_script_path, "--type", content_type, "--input", input_path],
            capture_output=True, text=True, check=True
        )
        log(f"Publish {content_type} successful: stdout={result.stdout.strip()}, stderr={result.stderr.strip()}")
        if content_type == "brief":
            open('/tmp/hermes_last_publish', 'w').close()
            log("Updated hermes_last_publish timestamp.")
    except subprocess.CalledProcessError as e:
        log(f"Publish {content_type} failed: {e}. stdout={e.stdout.strip()}, stderr={e.stderr.strip()}")
    except Exception as e:
        log(f"An unexpected error occurred during {content_type} publishing: {e}")

if __name__ == "__main__":
    print("DEBUG: Entering main execution block.") # Added debug print
    publish_content("brief", brief_json_path)
    publish_content("forecast", forecast_json_path)
    print("DEBUG: Script finished.") # Added debug print
