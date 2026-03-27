import requests
import json
import time

# API base URL and headers for the request
base_url = "https://api.tzevaadom.co.il/alerts-history/id/"
headers = {
    'authority': 'api.tzevaadom.co.il',
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9,he;q=0.8',
    'cache-control': 'no-cache',
    'origin': 'https://www.tzevaadom.co.il',
    'pragma': 'no-cache',
    'referer': 'https://www.tzevaadom.co.il/',
    'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
}

# Function to fetch alert data for a specific ID
def fetch_alert_data(alert_id):
    url = f"{base_url}{alert_id}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data for ID {alert_id}. Status code: {response.status_code}")
        return None

# Fetch and combine data for IDs from 4966 to 4967
start_id = 1
end_id = 4967
all_alerts = []

for alert_id in range(start_id, end_id + 1):
    data = fetch_alert_data(alert_id)
    if data and "alerts" in data:
        all_alerts.extend(data["alerts"])
        with open('combined_alerts.json', 'w', encoding='utf-8') as f:
            json.dump(all_alerts, f, ensure_ascii=False, indent=4)
        print(f"Fetched data for ID {alert_id}. Total alerts: {len(all_alerts)}")


print("All alerts have been saved to 'combined_alerts.json'")
