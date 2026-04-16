#!/bin/bash
API_KEY="${ALPHA_VANTAGE_API_KEY:-HWR8A1LVSYO4C2GX}" # Read from env or use default

# Function to safely curl and check for API errors
# Returns raw JSON or an empty string if error/rate limit
safe_curl() {
  local url="$1"
  raw_json=$(curl -s "$url")

  if [ -z "$raw_json" ] || [[ "$raw_json" == *"Error Message"* ]] || [[ "$raw_json" == *"rate limit"* ]]; then
    echo "" # Return empty string on error
  else
    echo "$raw_json"
  fi
}

# Python parsing function for use in bash
# Arguments: raw_json, default_value, key1, key2, ..., keyN
parse_json_value() {
  local raw_json="$1"
  local default_value="$2"
  shift 2 # Remove raw_json and default_value from arguments, remaining are keys

  if [ -z "$raw_json" ]; then
    echo "$default_value"
    return
  }

  # Robust single-line Python parsing: prints value or default on error
  # Passes keys as separate sys.argv arguments
  value=$(echo "$raw_json" | python3 -c "
import sys,json
try:
    data = json.load(sys.stdin)
    keys = sys.argv[1:]
    current_value = data
    for k in keys:
        if k.isdigit():
            current_value = current_value[int(k)]
        else:
            current_value = current_value[k]
    print(current_value)
except (json.decoder.JSONDecodeError, KeyError, IndexError, TypeError) as e:
    sys.stderr.write('JSON parsing error [' + ' '.join(keys) + ']: ' + str(e) + '\n')
    print('$default_value') # Print default immediately if error
" "$@" || echo "$default_value")
  
  # Final check, though Python now prints default on error
  if [ -z "$value" ]; then
    echo "$default_value"
  else
    echo "$value"
  fi
}

# --- Fetch Indicators ---

# Fetch Brent Crude
BRENT_JSON=$(safe_curl "https://www.alphavantage.co/query?function=BRENT&interval=daily&apikey=$API_KEY")
sleep 1 # Respect API rate limits
BRENT=$(parse_json_value "$BRENT_JSON" "0.0" "data" "0" "value")

# Gold (XAUUSD) - Alpha Vantage free tier limitations make real-time gold difficult to fetch reliably.
# Defaulting to 0.0 for now. A different API or premium access would be needed.
GOLD_VALUE="0.0" # Defaulting for now
sleep 1 # Respect API rate limits

# Fetch NZD/USD Exchange Rate
NZDUSD_JSON=$(safe_curl "https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=NZD&to_currency=USD&apikey=$API_KEY")
NZDUSD=$(parse_json_value "$NZDUSD_JSON" "0.0" "Realtime Currency Exchange Rate" "5. Exchange Rate")

# --- Output to JSON file ---
echo "{\"brent\": $BRENT, \"gold\": $GOLD_VALUE, \"nzdusd\": $NZDUSD}" > /tmp/hermes_indicators.json
