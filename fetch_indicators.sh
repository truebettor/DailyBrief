#!/bin/bash

if [ -z "$ALPHA_VANTAGE_API_KEY" ]; then
  echo "Error: ALPHA_VANTAGE_API_KEY not set." >&2
  echo '{"brent": "N/A", "nzdusd": "N/A", "nzdcny": "N/A"}' > /tmp/hermes_indicators.json
  exit 1
fi

API_KEY="${ALPHA_VANTAGE_API_KEY}"

# --- Brent Crude ---
BRENT_JSON=$(curl -s "https://www.alphavantage.co/query?function=BRENT&interval=daily&apikey=$API_KEY")
BRENT=$(echo "$BRENT_JSON" | python3 -c "import sys,json; data=json.load(sys.stdin); print(data['data'][0]['value'])" 2>/dev/null || echo "N/A")
sleep 1

# --- NZD/USD ---
NZDUSD_JSON=$(curl -s "https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=NZD&to_currency=USD&apikey=$API_KEY")
NZDUSD=$(echo "$NZDUSD_JSON" | python3 -c "import sys,json; data=json.load(sys.stdin); print(data['Realtime Currency Exchange Rate']['5. Exchange Rate'])" 2>/dev/null || echo "N/A")
sleep 1

# --- NZD/CNY ---
NZDCNY_JSON=$(curl -s "https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=NZD&to_currency=CNY&apikey=$API_KEY")
NZDCNY=$(echo "$NZDCNY_JSON" | python3 -c "import sys,json; data=json.load(sys.stdin); print(data['Realtime Currency Exchange Rate']['5. Exchange Rate'])" 2>/dev/null || echo "N/A")

# --- Write output ---
echo '{"brent": "'$BRENT'", "nzdusd": "'$NZDUSD'", "nzdcny": "'$NZDCNY'"}' > /tmp/hermes_indicators.json

echo "Indicators fetched: Brent=$BRENT NZD/USD=$NZDUSD NZD/CNY=$NZDCNY"
