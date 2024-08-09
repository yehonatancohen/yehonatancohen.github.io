import requests
import json
from datetime import datetime, timedelta

# Define initial parameters
url = 'https://alerts-history.oref.org.il//Shared/Ajax/GetAlarmsHistory.aspx'
from_date = '07.10.2023 00:00:00'
to_date = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
mode = '0'

# Headers required for the request
headers = {
    'Accept': 'application/json',
    'Accept-Language': 'en-US,en;q=0.9,he;q=0.8',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Cookie': 'UsId=VMLAO9NK-6UC9-3WXU-RERH-8R43ALXBCDVG; mp_cff7389ad1aba4a6b7f9631edf8f6234_mixpanel=%7B%22distinct_id%22%3A%20%22%24device%3A1900783b2f269d-068b3d3f6c2d8f-26001b51-384000-1900783b2f269d%22%2C%22%24device_id%22%3A%20%221900783b2f269d-068b3d3f6c2d8f-26001b51-384000-1900783b2f269d%22%2C%22%24initial_referrer%22%3A%20%22https%3A%2F%2Fwww.google.com%2F%22%2C%22%24initial_referring_domain%22%3A%20%22www.google.com%22%2C%22__mps%22%3A%20%7B%22%24os%22%3A%20%22Windows%22%2C%22%24browser%22%3A%20%22Chrome%22%2C%22%24browser_version%22%3A%20122%2C%22Random%20UID%22%3A%20%22VMLAO9NK-6UC9-3WXU-RERH-8R43ALXBCDVG%22%7D%2C%22__mpso%22%3A%20%7B%22%24initial_referrer%22%3A%20%22https%3A%2F%2Fwww.google.com%2F%22%2C%22%24initial_referring_domain%22%3A%20%22www.google.com%22%7D%2C%22__mpus%22%3A%20%7B%7D%2C%22__mpa%22%3A%20%7B%7D%2C%22__mpu%22%3A%20%7B%7D%2C%22__mpr%22%3A%20%5B%5D%2C%22__mpap%22%3A%20%5B%5D%2C%22%24search_engine%22%3A%20%22google%22%7D; Lastalerts=; AlertSoundNewFeature=1; _hjSessionUser_2052890=eyJpZCI6IjZiYjBkZDhiLWQzNGEtNTc0Zi05MjVmLWUxMGRlNzUxMzZhNyIsImNyZWF0ZWQiOjE3MTgxMTI5OTAwOTksImV4aXN0aW5nIjpmYWxzZX0=; _hjSession_2052890=eyJpZCI6IjJmZTRlNWNjLTg1MTgtNDk3Ny1iMzAyLWEyYjkwZGJhZmVhNiIsImMiOjE3MTgxMTI5OTAxMDAsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjoxLCJzcCI6MH0=; _ga=GA1.1.549740074.1718112990; _clck=1ooth9n%7C2%7Cfmj%7C0%7C1623; _clsk=jasfjg%7C1718112991045%7C1%7C0%7Co.clarity.ms%2Fcollect; _ga_V2BQHCDHZP=GS1.1.1718112990.1.0.1718112999.51.0.0; ASP.NET_SessionId=fmf522gk2ymq2zhsk0erxns5; TS013a1194=01feb52f0a4d0966c6c5cc9d86e186582b04fc482b80ee95c65c89e2eda1292693b841a1f10ac1141111bd1e8e62b6d3adcdf813ac48f21ca297c6404af4d56aec1d97b3f1',
    'Pragma': 'no-cache',
    'Referer': 'https://www.oref.org.il/12481-he/Pakar.aspx?hash=12482',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

all_alerts = []

def fetch_alerts(from_date, to_date):
    params = {
        'fromDate': from_date,
        'toDate': to_date,
        'mode': mode
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    if response.status_code == 200:
        try:
            r = response.json()
        except requests.exceptions.RequestException as e:
            print(e)
            return
        return r
    else:
        print(f"Error fetching data: {response.status_code}")
        return []

last = False
while True:
    alerts = fetch_alerts(from_date, to_date)
    if not alerts:
        break
    
    all_alerts.extend(alerts)
    
    # Get the date and time of the last alert and set it as the new to_date
    last_alert_datetime = alerts[-1]['alertDate']  # Adjust based on the actual structure of the response
    last_alert_datetime = datetime.strptime(last_alert_datetime, '%Y-%m-%dT%H:%M:%S')
    to_date = (last_alert_datetime - timedelta(seconds=1)).strftime('%d.%m.%Y %H:%M:%S')
    print(f"Fetched {len(alerts)} alerts, last alert at {to_date}")
    
    # Break if the number of alerts is less than 2000, indicating there are no more alerts
    if last or to_date.split(" ")[0] == '07.10.2023':
        break
    if len(alerts) < 2000:
        last = True

# Save all alerts to a file
with open('alerts/static/alerts.json', 'w', encoding='utf-8') as f:
    json.dump(all_alerts, f, ensure_ascii=False, indent=4)

print(f"Fetched {len(all_alerts)} alerts")
