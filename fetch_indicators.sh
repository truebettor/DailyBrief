#!/bin/bash

# Ensure ALPHA_VANTAGE_API_KEY environment variable is set
if [ -z "$ALPHA_VANTAGE_API_KEY" ]; then
  echo "Error: ALPHA_VANTAGE_API_KEY environment variable is not set. Please set it to proceed." >&2
  echo "{\"brent\": 0.0, \"gold\": 0.0, \"nzdusd\": 0.0}" > /tmp/hermes_indicators.json
  exit 1
fi

API_KEY="$ALPHA_VANTAGE_API_KEY"

# --- Fetch Brent Crude ---
BRENT_JSON=$(curl -s "https://www.alphavantage.co/query?function=BRENT&interval=daily&apikey=$API_KEY")
BRENT=$(echo "$BRENT_JSON" | python3 -c "import sys,json; data=json.load(sys.stdin); print(data['data'][0]['value'])" 2>/dev/null || echo "0.0")
sleep 1 # Respect API rate limits

# --- Fetch Gold (XAUUSD) ---
# Alpha Vantage free tier limitations make real-time gold difficult to fetch reliably.
# Defaulting to 0.0 for now. A different API or premium access would be needed.
GOLD="0.0"
sleep 1 # Respect API rate limits

# --- Fetch NZD/USD Exchange Rate ---
NZDUSD_JSON=$(curl -s "https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=NZD&to_currency=USD&apikey=$API_KEY")
NZDUSD=$(echo "$NZDUSD_JSON" | python3 -c "import sys,json; data=json.load(sys.stdin); print(data['Realtime Currency Exchange Rate']['5. Exchange Rate'])" 2>/dev/null || echo "0.0")

# --- Output to JSON file ---
echo "{\"brent\": $BRENT, \"gold\": $GOLD, \"nzdusd\": $NZDUSD}" > /tmp/hermes_indicators.json