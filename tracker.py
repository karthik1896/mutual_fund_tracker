import os
import requests
import time
import schedule

# Discord Webhook Configuration
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

# Mutual Funds & Their IDs to Track
MUTUAL_FUNDS = {
    "Nippon India Small Cap Fund": "120828",
    "Quant Small Cap Fund": "125497",
    "Tata Small Cap Fund": "122639",
    "UTI Nifty Index Fund": "119364",
    "Motilal Oswal SmallCap Fund": "124963",
    "PGIM India Small Cap Fund": "121773",
    "Aditya Birla Sun Life Multi-Index Fund of Funds": "126196",
    "HDFC Nifty Index Fund": "118550",
    "SBI Nifty Index Fund": "118834"
}

THRESHOLDS = {
    "Nippon India Small Cap Fund": {"low": 100.0, "high": 150.0},
    "Quant Small Cap Fund": {"low": 120.0, "high": 180.0},
    "Tata Small Cap Fund": {"low": 90.0, "high": 140.0},
    "UTI Nifty Index Fund": {"low": 80.0, "high": 130.0},
    "Motilal Oswal SmallCap Fund": {"low": 110.0, "high": 160.0},
    "PGIM India Small Cap Fund": {"low": 100.0, "high": 140.0},
    "Aditya Birla Sun Life Multi-Index Fund of Funds": {"low": 70.0, "high": 120.0},
    "HDFC Nifty Index Fund": {"low": 85.0, "high": 135.0},
    "SBI Nifty Index Fund": {"low": 90.0, "high": 140.0}
}

# Fetch Mutual Fund NAVs (Today's NAV)
def fetch_mutual_fund_nav():
    url = "https://api.mfapi.in/mf/"
    results = {}

    for fund, fund_id in MUTUAL_FUNDS.items():
        try:
            response = requests.get(url + fund_id, timeout=5)
            response.raise_for_status()
            nav = float(response.json()["data"][0]["nav"])  # Fetch today's NAV
            results[fund] = nav
        except Exception as e:
            print(f"⚠️ Error fetching {fund}: {e}")
    
    return results

# Send Discord Alert with Aggregated Information in a Table Structure
def send_discord_alert(message):
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json={"content": message}, timeout=5)
        response.raise_for_status()
    except Exception as e:
        print(f"⚠️ Error sending Discord alert: {e}")

# Track Assets & Aggregate Alerts
def track_assets():
    assets = fetch_mutual_fund_nav()
    alerts = []  # Collect all alerts
    table_rows = []  # Collect rows for tabular display

    # Prepare the table header with proper alignment for Discord
    table_header = f"{'Fund Name':<45} {'Price (₹)':<15} {'Alert'}"
    table_rows.append(table_header)

    for name, price in assets.items():
        if name in THRESHOLDS:
            low, high = THRESHOLDS[name]["low"], THRESHOLDS[name]["high"]

            # Add price row to table
            price_alert = ""
            if price < low:
                price_alert = "📉 (Buy Opportunity)"
            elif price > high:
                price_alert = "📈 (Consider Selling)"
            table_rows.append(f"{name:<45} {price:<15} {price_alert}")

            # Collect alert message
            if price_alert:
                alerts.append(f"🚨 {name}: {price_alert} at {price}!")

    # Prepare the structured message with both market alerts and table
    if alerts:
        structured_message = "🚨 **Market Alerts** 🚨\n"
        structured_message += "\n".join(alerts) + "\n\n"
        structured_message += "📊 **Today's Prices** 📊\n"
        
        # Add the table, wrapped in a code block
        structured_message += "```" + "\n".join(table_rows) + "```"

        send_discord_alert(structured_message)
    else:
        print("No alerts triggered today.")

# Run every day at 9 AM & 3 PM
schedule.every().day.at("09:00").do(track_assets)
schedule.every().day.at("15:00").do(track_assets)

if __name__ == "__main__":
    # track_assets()
    while True:
        schedule.run_pending()  # Keep checking for pending scheduled tasks
        time.sleep(60)  # Check every minute
