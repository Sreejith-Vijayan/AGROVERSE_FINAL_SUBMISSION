"""Farm profile and metadata for Palakkad Demo Farm."""

FARM = {
    "name": "Palakkad Demo Farm",
    "place": "Palakkad, Kerala, India",
    "lat": 10.7080, "lon": 76.6390,          # Chittur-Kollengode paddy belt, Palakkad district
    "center": [10.7080, 76.6390],
    "polygon": [                              # farm boundary (lat, lon)
        [10.7125, 76.6330], [10.7138, 76.6395], [10.7122, 76.6440],
        [10.7078, 76.6452], [10.7045, 76.6415], [10.7040, 76.6350],
        [10.7075, 76.6320],
    ],
    "zoom": 14,
}

# Uncalibrated NDVI: marked as No Data / Pending per scientific accuracy standards
NDVI = {
    "label": "No Data",
    "value": "Pending Feed",
    "status": "UNAVAILABLE",
    "isAvailable": False,
    "description": "Sentinel-2 / Landsat NDVI raster feed pending ground calibration",
    "line": []
}

ROTATIONS = [
    {"title": "Current practice", "star": False, "hl": False,
     "rows": [("Water demand", "High", "red"), ("Soil improvement", "Low", "red"),
              ("Drought resilience", "Moderate", "amber")]},
    {"title": "Rotation A – Investigate", "star": True, "hl": True,
     "rows": [("Water demand", "Moderate", "dark"), ("Soil improvement", "High", "dark"),
              ("Drought resilience", "High", "dark")]},
    {"title": "Rotation B", "star": False, "hl": False,
     "rows": [("Water demand", "Low", "dark"), ("Soil improvement", "Moderate", "dark"),
              ("Drought resilience", "Moderate", "dark")]},
]
