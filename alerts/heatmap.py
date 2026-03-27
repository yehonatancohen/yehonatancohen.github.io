import json
import time, requests
import geopandas as gpd
from shapely.geometry import Point
from geopy.distance import geodesic
import pandas as pd
import folium
from folium.plugins import HeatMap
from shapely.geometry import shape, Point
from shapely.ops import nearest_points
from geopy.distance import geodesic

def load_geojson_boundaries(filepath):
    """
    Loads country borders from a local GeoJSON file.
    """
    with open(filepath, 'r', encoding='utf-8') as file:
        geojson_data = json.load(file)
    return shape(geojson_data['features'][0]['geometry'])


def is_close_to_border(lat, lon, threshold_km=10):
    """
    Determines if a point (lat, lon) is within threshold_km of any country border.
    """
    point = Point(lon, lat)
    border = load_geojson_boundaries('israel.geojson')
    
    if border.contains(point):
        # Point is inside the country; check distance to the border
        nearest_geom = nearest_points(point, border.boundary)[1]
        distance = geodesic((lat, lon), (nearest_geom.y, nearest_geom.x)).kilometers
        return distance <= threshold_km
    else:
        # Point is outside, check distance to the nearest border point
        distance = border.boundary.distance(point) * 111  # Roughly converting degrees to km
        return distance <= threshold_km

# רשימת ישובים עם קואורדינטות שכבר נשלפו
try:
    with open('known_locations.json', 'r', encoding='utf-8') as loc_file:
        known_locations = json.load(loc_file)
except FileNotFoundError:
    known_locations = {}

# פונקציה לשליפת קואורדינטות מ-Nominatim API אם היישוב לא קיים במאגר המקומי
def get_coordinates(settlement):
    global last_api_call_time
    
    # בדיקה אם המיקום כבר ידוע
    if settlement in known_locations:
        return known_locations[settlement]
    return None, None

# שלב 1: טעינת קובץ JSON של ההתראות
with open('alerts/static/alerts.json', 'r', encoding='utf-8') as file:
    alerts_data = json.load(file)

# שלב 2: סינון התראות כתב"מים והוספת קואורדינטות
filtered_alerts = []
for alert in alerts_data:
    #if alert.get("category_desc") == "חדירת כלי טיס עוין":
    if alert.get("category_desc") == "ירי רקטות וטילים":
        settlement = alert.get("data")  # שם הישוב בהתראה
        lat, lon = get_coordinates(settlement)
        if (lat, lon) == (None, None): continue
        print(f"Alert in {settlement}: {lat}, {lon}, {not is_close_to_border(lat, lon, threshold_km=50)}")
        if (not (pd.isna(lat) or pd.isna(lon)) and lon and lat) and (not is_close_to_border(lat, lon, threshold_km=2.5)):
            filtered_alerts.append({
            "settlement": settlement,
            "latitude": lat,
            "longitude": lon,
            "alertDate": alert.get("alertDate")
            })

# המרת התראות עם קואורדינטות למסגרת נתונים
df = pd.DataFrame(filtered_alerts)

# שלב 3: יצירת מפת חום
if not df.empty:
    # Use the same initial map settings
    heatmap_map = folium.Map(location=[32.5, 35.0], zoom_start=8)  # Northern Israel region

    # Prepare heatmap data (latitude and longitude)
    heat_data = [[row['latitude'], row['longitude']] for index, row in df.iterrows()]

    # Customize the HeatMap appearance with adjustments
    HeatMap(
        heat_data,
        radius=10,        # Slightly larger radius for better coverage
        blur=12,          # Increase blur for smoother gradients
        min_opacity=0.5,  # Increase minimum opacity to enhance visibility
        max_val=1.0,      # Adjusts the maximum intensity
        gradient={0.2: 'purple', 0.5: 'blue', 0.7: 'lime', 1: 'orange'}  # Custom gradient for enhanced color contrast
    ).add_to(heatmap_map)

    # Save the map as an HTML file
    heatmap_map.save("heatmap_alerts.html")
    print("Heatmap saved successfully as heatmap_alerts.html")
else:
    print("Not enough data to create a heatmap")
