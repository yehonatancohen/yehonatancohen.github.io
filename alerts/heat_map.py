import json
import folium
from folium.plugins import HeatMap
from sklearn.cluster import DBSCAN
from haversine import haversine, Unit
import numpy as np
from datetime import datetime
from collections import defaultdict

# Load alerts and coordinates
with open('alerts.json', 'r', encoding='utf-8') as f:
    alerts = json.load(f)

with open('coordinates.json', 'r', encoding='utf-8') as f:
    coordinates = json.load(f)

# Define Israel's approximate border limit (adjust coordinates as needed)
border_limit_latitude = 31.75  # Adjust as needed
border_limit_longitude = 34.2  # Adjust as needed

# Filter UAV alerts and exclude those near the border
uav_alerts = []
for alert in alerts:
    if alert["category"] == 2:  # Only include UAV alerts
        location_name = alert["data"]
        try:
            # Check if location coordinates exist and are within border limits
            location_coords = coordinates[location_name]
            if (location_coords["latitude"] > border_limit_latitude and 
                location_coords["longitude"] > border_limit_longitude):
                uav_alerts.append(alert)
        except KeyError:
            print(f"Coordinates for '{location_name}' not found. Skipping this alert.")
            continue

# Prepare data for clustering
def parse_time(alert):
    return datetime.fromisoformat(alert["alertDate"])

reference_time = datetime.fromisoformat("2024-10-07T00:00:00")
alert_locations = []
alert_data = []

for alert in uav_alerts:
    location_name = alert["data"]
    try:
        lat = coordinates[location_name]["latitude"]
        lon = coordinates[location_name]["longitude"]
        time_seconds = (parse_time(alert) - reference_time).total_seconds()
        alert_locations.append([lat, lon, time_seconds])
        alert_data.append(alert)
    except KeyError:
        print(f"Coordinates for '{location_name}' not found in final filtering. Skipping this alert.")
        continue

alert_locations = np.array(alert_locations)

# Define spatiotemporal distance function
def spatiotemporal_distance(x, y):
    spatial_distance = haversine((x[0], x[1]), (y[0], y[1]), unit=Unit.KILOMETERS)
    time_distance = abs(x[2] - y[2]) / 60  # Convert seconds to minutes
    return spatial_distance + (time_distance / 5)

# DBSCAN clustering
db = DBSCAN(eps=5, min_samples=2, metric=spatiotemporal_distance).fit(alert_locations)
labels = db.labels_

# Collect clusters that penetrate inside borders
clusters = defaultdict(list)
for label, location in zip(labels, alert_locations):
    if label != -1:
        clusters[label].append(location)

# Prepare inward paths for heatmap and connecting lines
heatmap_data = []
m = folium.Map(location=[31.5, 34.5], zoom_start=8)

for cluster, locations in clusters.items():
    # Sort by time to get paths moving inward
    locations.sort(key=lambda x: x[2])  # Sort by timestamp
    
    # Add sorted locations to heatmap
    heatmap_data.extend([[loc[0], loc[1], 1] for loc in locations])

    # Draw lines connecting alerts within each cluster
    if len(locations) > 1:
        # Extract latitude and longitude for PolyLine
        path_coordinates = [[loc[0], loc[1]] for loc in locations]
        folium.PolyLine(path_coordinates, color="blue", weight=2.5, opacity=0.7).add_to(m)

# Add heatmap layer
HeatMap(heatmap_data, radius=10, max_zoom=13).add_to(m)

# Save the map
m.save("uav_alert_connected_paths.html")
print("Heatmap with connected UAV paths saved as 'uav_alert_connected_paths.html'")
