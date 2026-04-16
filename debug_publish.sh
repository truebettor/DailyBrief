#!/bin/bash

# Ensure ALPHA_VANTAGE_API_KEY is set in the cron environment variables.
# If running manually for debug, remember to export it first.

echo "$(date) - debug_publish.sh started." > /home/jim-rauch/daymark/cron_publisher_debug.log
echo "$(date) - Current PATH: $PATH" >> /home/jim-rauch/daymark/cron_publisher_debug.log
echo "$(date) - Attempting to execute publish_brief_script.py" >> /home/jim-rauch/daymark/cron_publisher_debug.log

cd /home/jim-rauch/daymark/scripts/ || {
    echo "$(date) - ERROR: Failed to change directory to /home/jim-rauch/daymark/scripts/" >> /home/jim-rauch/daymark/cron_publisher_debug.log
    exit 1
}

# Execute the Python script, redirecting its stdout/stderr to the log file
python3 publish_brief_script.py >> /home/jim-rauch/daymark/cron_publisher_debug.log 2>&1

if [ $? -ne 0 ]; then
    echo "$(date) - ERROR: publish_brief_script.py exited with non-zero status." >> /home/jim-rauch/daymark/cron_publisher_debug.log
else
    echo "$(date) - publish_brief_script.py completed successfully." >> /home/jim-rauch/daymark/cron_publisher_debug.log
fi

# Also explicitly try to list /tmp contents after script runs, for debugging file creation
echo "$(date) - /tmp/ contents after script run:" >> /home/jim-rauch/daymark/cron_publisher_debug.log
ls -la /tmp/ >> /home/jim-rauch/daymark/cron_publisher_debug.log 2>&1

echo "$(date) - debug_publish.sh finished."