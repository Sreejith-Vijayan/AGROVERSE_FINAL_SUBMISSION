# AGROVERSE API Integration Guide

## Overview
This document specifies the REST API endpoints and JSON schemas implemented by the AGROVERSE backend to serve NASA POWER climate indicators, NASA SMAP soil moisture estimates, and provisional soil properties.

### Base URL
`http://127.0.0.1:5000/api`

### Endpoints

#### 1. Monthly Climate & SMAP
- **Route**: `GET /api/monthly`
- **Query Parameters**:
  - `from` (optional): Format `YYYY-MM` (e.g. `2020-01`)
  - `to` (optional): Format `YYYY-MM` (e.g. `2025-12`)
- **Response Shape**:
```json
{
  "meta": {
    "location": "Palakkad Town, Kerala, India",
    "latitude": 10.7867,
    "longitude": 76.6548,
    "dataset": "monthly_climate_smap",
    "records": 72,
    "smap_note": "~36 km grid cell, not farm-level"
  },
  "data": [
    {
      "date": "2020-01-01",
      "year_month": "2020-01",
      "year": 2020,
      "month": 1,
      "rainfall_total_mm": 4.38,
      "temperature_avg_c": 23.17,
      "temperature_min_c": 19.8,
      "temperature_max_c": 26.4,
      "relative_humidity_pct": 68.2,
      "solar_radiation_mj_m2_day": 21.4,
      "wind_speed_m_s": 3.1,
      "smap_am_soil_moisture_m3m3": 0.2828,
      "smap_pm_soil_moisture_m3m3": 0.2696,
      "smap_combined_am_pm_m3m3": 0.2762,
      "smap_am_valid_obs": 11,
      "smap_pm_valid_obs": 11,
      "smap_low_coverage_flag": 0
    }
  ]
}
```

#### 2. Static Soil Properties
- **Route**: `GET /api/soil`
- **Response Shape**:
```json
{
  "meta": {
    "location": "Palakkad Demo Farm, Kerala, India",
    "coordinates": [10.708, 76.639],
    "status": "PROVISIONAL",
    "notice": "Values are provisional regional estimates and require ground verification. Not confirmed farm-level core measurements."
  },
  "properties": [
    {
      "name": "Clay content",
      "key": "clay_content_pct",
      "value": 28.4,
      "unit": "%",
      "status": "PROVISIONAL"
    },
    {
      "name": "Soil pH",
      "key": "soil_ph",
      "value": 6.35,
      "unit": "pH scale (0-14)",
      "status": "PROVISIONAL"
    },
    {
      "name": "Soil organic carbon (SOC)",
      "key": "soil_organic_carbon_pct",
      "value": 0.78,
      "unit": "%",
      "status": "PROVISIONAL"
    }
  ]
}
```

#### 3. Yearly Climate Summary
- **Route**: `GET /api/yearly`
- **Response Shape**:
```json
{
  "meta": { "location": "Palakkad Town, Kerala, India", "records": 6, "verified": true },
  "data": [
    {
      "year": 2020,
      "rainfall_total_mm": 2145.6,
      "temperature_avg_c": 27.8,
      "rainy_days_count": 112,
      "dry_days_count": 254,
      "heavy_rain_days_count": 14
    }
  ]
}
```

#### 4. Seasonal Climate Summary
- **Route**: `GET /api/seasonal`
- **Response Shape**:
```json
{
  "meta": { "location": "Palakkad Town, Kerala, India", "records": 24, "verified": true },
  "data": [
    {
      "year": 2020,
      "season": "Southwest Monsoon",
      "rainfall_total_mm": 1340.5,
      "temperature_avg_c": 26.4,
      "relative_humidity_pct": 84.2,
      "rainy_days_count": 68,
      "heavy_rain_days_count": 9
    }
  ]
}
```
