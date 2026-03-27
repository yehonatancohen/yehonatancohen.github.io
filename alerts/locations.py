import json
from geopy.geocoders import Nominatim
import time

# Load the alerts data from your JSON file
with open('alerts/static/alerts.json', 'r', encoding='utf-8') as f:
    alerts = json.load(f)

# Initialize the geocoder
geolocator = Nominatim(user_agent="alert_locator")

# Dictionary to store coordinates
# Load existing coordinates from file if it exists
try:
    with open('coordinates.json', 'r', encoding='utf-8') as f:
        coordinates = json.load(f)
except FileNotFoundError:
    coordinates = {}

# Loop through the alerts to find coordinates for each unique location
for alert in alerts:
    location_name = alert["data"]
    # Check if location already has coordinates
    if location_name not in coordinates:
        try:
            location = geolocator.geocode(location_name)
            if location:
                coordinates[location_name] = {"latitude": location.latitude, "longitude": location.longitude}
                with open('coordinates.json', 'w', encoding='utf-8') as f:
                    json.dump(coordinates, f, ensure_ascii=False, indent=4)
                print(f"Coordinates for {location_name} found: {location.latitude}, {location.longitude}")
            else:
                location = geolocator.geocode(location_name.split(" ")[0])
                if location:
                    coordinates[location_name] = {"latitude": location.latitude, "longitude": location.longitude}
                    with open('coordinates.json', 'w', encoding='utf-8') as f:
                        json.dump(coordinates, f, ensure_ascii=False, indent=4)
                    print(f"Coordinates for {location_name} found: {location.latitude}, {location.longitude}")
                else:
                    print(f"Coordinates for {location_name} not found.")
            time.sleep(1)  # To avoid overloading the server with requests
        except Exception as e:
            print(f"Error finding coordinates for {location_name}: {e}")

print("Coordinates saved to 'coordinates.json'")
