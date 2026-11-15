# AGROVERSE UI Data Dictionary

## 1. Monthly Climate & SMAP (`monthly_climate_smap.json` / `.csv`)
- **Coverage**: 2020-01 through 2025-12 (72 records)
- **Target Location**: Palakkad Town / Palakkad Demo Farm, Kerala (`10.7867° N, 76.6548° E`)

| Field | Type | Unit | Description | Status / Note |
|---|---|---|---|---|
| `date` | string | YYYY-MM-DD | First day of observation month | Verified |
| `year_month` | string | YYYY-MM | Year and month identifier | Verified |
| `year` | integer | - | Year (2020–2025) | Verified |
| `month` | integer | 1–12 | Calendar month index | Verified |
| `rainfall_total_mm` | float | mm/month | Total monthly precipitation (NASA POWER PRECTOTCORR) | Verified |
| `temperature_avg_c` | float | °C | Monthly average mean daily temperature | Verified |
| `temperature_min_c` | float | °C | Monthly minimum of daily mean temperatures | Verified |
| `temperature_max_c` | float | °C | Monthly maximum of daily mean temperatures | Verified |
| `relative_humidity_pct` | float | % | Monthly mean relative humidity at 2m (RH2M) | Verified |
| `solar_radiation_mj_m2_day` | float | MJ/m²/day | All-sky surface shortwave downward irradiance | Verified |
| `wind_speed_m_s` | float | m/s | Monthly average wind speed at 10m | Verified |
| `smap_am_soil_moisture_m3m3` | float | m³/m³ | NASA SMAP descending (06:00 AM) volumetric soil moisture | PROVISIONAL (~36 km grid cell) |
| `smap_pm_soil_moisture_m3m3` | float | m³/m³ | NASA SMAP ascending (06:00 PM) volumetric soil moisture | PROVISIONAL (~36 km grid cell) |
| `smap_combined_am_pm_m3m3` | float | m³/m³ | Average of valid AM and PM soil moisture observations | PROVISIONAL (~36 km grid cell) |
| `smap_am_valid_obs` | integer | count | Count of valid AM satellite passes in the month | Operational |
| `smap_pm_valid_obs` | integer | count | Count of valid PM satellite passes in the month | Operational |
| `smap_low_coverage_flag` | integer | 0 or 1 | Flag indicating fewer than optimal satellite observations | When 1: "Few valid satellite observations" |

## 2. Yearly Climate Summary (`yearly_climate_summary.json` / `.csv`)
- **Coverage**: 2020 through 2025 (6 records)

| Field | Type | Unit | Description |
|---|---|---|---|
| `year` | integer | - | Calendar Year |
| `rainfall_total_mm` | float | mm/year | Total cumulative annual precipitation |
| `temperature_avg_c` | float | °C | Mean annual temperature |
| `rainy_days_count` | integer | days | Days with precipitation ≥ 2.5 mm |
| `dry_days_count` | integer | days | Days with precipitation < 2.5 mm |
| `heavy_rain_days_count` | integer | days | Days with precipitation ≥ 64.5 mm (IMD Threshold) |

## 3. Seasonal Climate Summary (`seasonal_climate_summary.json` / `.csv`)
- **Coverage**: 2020 through 2025 across 4 standard meteorological seasons (24 records)
  - **Winter**: January – February
  - **Summer / Pre-monsoon**: March – May
  - **Southwest Monsoon**: June – September
  - **Post-Monsoon**: October – December

| Field | Type | Unit | Description |
|---|---|---|---|
| `year` | integer | - | Calendar Year |
| `season` | string | - | Season name |
| `rainfall_total_mm` | float | mm/season | Total cumulative rainfall in season |
| `temperature_avg_c` | float | °C | Seasonal mean temperature |
| `relative_humidity_pct` | float | % | Seasonal mean relative humidity |
| `rainy_days_count` | integer | days | Days with precipitation ≥ 2.5 mm |
| `heavy_rain_days_count` | integer | days | Days with precipitation ≥ 64.5 mm |

## 4. Static Soil Properties (`static_soil_properties.json` / `.csv`)
- **Status**: PROVISIONAL
- **Notice**: "Values are provisional regional estimates and require ground verification. Not confirmed farm-level core measurements."
- **Permitted Properties**:
  - `clay_content_pct`: Sub-surface clay content estimate (`%`)
  - `soil_ph`: Soil acidity index (`pH scale 0-14`)
  - `soil_organic_carbon_pct`: Topsoil organic carbon fraction (`%`)
- **Strict Constraint**: Nitrogen, sand, and silt must not be displayed in the UI.
