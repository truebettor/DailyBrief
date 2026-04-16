#!/bin/bash

# Ensure ALPHA_VANTAGE_API_KEY is set in the cron environment variables.
# If running manually for debug, remember to export it first.

echo "$(date) - debug_publish.sh started." > /tmp/cron_publisher_debug.log
echo "$(date) - Current PATH: $PATH" >> /tmp/cron_publisher_debug.log
echo "$(date) - Attempting to execute publish_brief_script.py" >> /tmp/cron_publisher_debug.log

cd /home/jim-rauch/daymark/scripts/ || {
        echo "$(date) - ERROR: Failed to change directory to /home/jim-rauch/daymark/scripts/" >> /tmp/cron_publisher_debug.log
    exit 1
}

# Remove old JSON files to force regeneration with the current date
rm -f /tmp/hermes_brief.json >> /tmp/cron_publisher_debug.log 2>&1
rm -f /tmp/hermes_forecast.json >> /tmp/cron_publisher_debug.log 2>&1
echo "$(date) - Removed old /tmp/hermes_brief.json and /tmp/hermes_forecast.json" >> /tmp/cron_publisher_debug.log


# Execute the Python script, redirecting its stdout/stderr to the log file
python3 publish_brief_script.py >> /tmp/cron_publisher_debug.log 2>&1

if [ $? -ne 0 ]; then
    echo "$(date) - ERROR: publish_brief_script.py exited with non-zero status." >> /tmp/cron_publisher_debug.log
else
    echo "$(date) - publish_brief_script.py completed successfully." >> /tmp/cron_publisher_debug.log
fi

# Also explicitly try to list /tmp contents after script runs, for debugging file creation
echo "$(date) - /tmp/ contents after script run:" >> /tmp/cron_publisher_debug.log
ls -la /tmp/ >> /tmp/cron_publisher_debug.log 2>&1

echo "$(date) - debug_publish.sh finished." >> /tmp/cron_publisher_debug.log