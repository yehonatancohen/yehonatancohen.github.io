var map;
var CITIES_JSON = {};
var POLYGONS = {};
var markersAndPolygons = {};
var selectionCitiesIDs = [];
var alertsData = {};

async function loadData() {
    // Assuming cities.json and polygons.json are available locally
    const citiesResponse = await fetch('static/cities.json');
    const polygonsResponse = await fetch('static/polygons.json');
    const alertsResponse = await fetch('static/alerts.json');
    
    CITIES_JSON = await citiesResponse.json();
    POLYGONS = await polygonsResponse.json();
    alertsData = await alertsResponse.json();
    
    console.log('Data loaded successfully');
    await fetchAlerts();
    setInterval(fetchAlerts, 1000);
}

async function fetchAlerts() {
    const proxyUrl = 'https://cors-anywhere.herokuapp.com/';
    const targetUrl = 'https://www.oref.org.il/WarningMessages/alert/alerts.json?v=1';
    
    const response = await fetch(proxyUrl + targetUrl, {
        headers: {
            'Referer': 'https://www.oref.org.il//12481-he/Pakar.aspx',
            'X-Requested-With': 'XMLHttpRequest'
        }
    });

    const newAlerts = await response.json();
    newAlerts.forEach(alert => {
        alertsData[alert.rid] = alert;
    });

    processAlerts();
}

class City {
    constructor(cityValue) {
        var item = CITIES_JSON["cities"][cityValue];
        if (item) {
            this.cityHE = item.he;
            this.lat = item.lat;
            this.lng = item.lng;
            this.id = item.id;
        } else {
            this.cityHE = cityValue;
            this.lat = 0;
            this.lng = 0;
            this.id = -1;
        }
    }

    getLocalizationCityName() {
        return this.cityHE;
    }

    getPolygon() {
        var item = POLYGONS[this.id.toString()];
        return item ? item : [];
    }
}

window.onload = async function() {
    map = L.map("map", {
        zoomControl: true
    }).setView([31.7683, 35.2137], 8); // Center the map at Jerusalem initially
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 18,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
    
    await loadData();
}

function addCityMarker(city) {
    if (markersAndPolygons[city.id]) return;

    const marker = L.marker([city.lat, city.lng], {
        icon: L.icon({
            iconUrl: "https://maps.gstatic.com/mapfiles/api-3/images/spotlight-poi3.png",
            iconAnchor: [14, 36],
        })
    });
    marker.bindPopup('<p style="font-weight: bold; font-size: 15px; margin: auto;">' + city.getLocalizationCityName() + "</p>");
    marker.addTo(map);
    markersAndPolygons[city.id] = marker;

    const polygon = city.getPolygon();
    if (polygon.length > 0) {
        const leafletPolygon = L.polygon(polygon, {
            color: "#FF0000",
            weight: 2,
            opacity: 0.7,
            fillOpacity: 0.3,
            fillColor: "#FF0000",
        }).addTo(map);
        markersAndPolygons[city.id] = {
            marker: marker,
            polygon: leafletPolygon
        };
    }
}

function processAlerts() {
    const cityAlerts = {};

    Object.values(alertsData).forEach(alert => {
        if (!cityAlerts[alert.data]) {
            cityAlerts[alert.data] = [];
        }
        cityAlerts[alert.data].push(alert.date + ' ' + alert.time);
    });

    Object.keys(cityAlerts).forEach(cityName => {
        var city = new City(cityName);
        if (city.lat !== 0 && city.lng !== 0) {
            addCityMarker(city, cityAlerts[cityName]);
        }
    });
}