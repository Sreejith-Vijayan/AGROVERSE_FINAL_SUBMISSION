"""
decision_support.config
Configuration constants, spatial metadata, and dataset definitions.

COORDINATE PROVENANCE NOTE
---------------------------------------------------------------------------
Two coordinate pairs appear across M5 datasets:

  10.7080° N, 76.6390° E — "Palakkad Demo Farm"
      Used as the NASA POWER / SMAP API extraction point in data_source.py
      and the M5 cache file (power_10.708_76.639.csv).
      This is the primary verified observational study location.

  10.7867° N, 76.6548° E — "Palakkad Town / District Reference"
      Used as the district-level reference centroid in 07_UI_HANDOVER JSON
      metadata and the build_handover_data.py script.
      This is a secondary regional reference, not the farm-level API point.

Do NOT overwrite or unify these coordinates without verifying which grid
cell was actually used for each dataset. They serve different purposes and
come from different team members.
---------------------------------------------------------------------------
"""
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
MEMBER_3_DIR = os.path.join(DATA_DIR, "member_3")
MEMBER_4_DIR = os.path.join(DATA_DIR, "member_4")
HANDOVER_DIR = os.path.join(BASE_DIR, "07_UI_HANDOVER")
HANDOVER_CSV_DIR = os.path.join(HANDOVER_DIR, "csv")
HANDOVER_JSON_DIR = os.path.join(HANDOVER_DIR, "json")

# Verified coverage dates
DATASET_START = "2020-01-01"
DATASET_END = "2025-12-31"

# Location metadata registry
LOCATIONS = {
    "palakkad_demo_farm": {
        "name": "Palakkad Demo Farm",
        "corridor": "Chittur-Kollengode Agricultural Corridor, Kerala, India",
        "lat": 10.708,
        "lon": 76.639,
        "role": "Primary verified observational study location",
        "description": "Empirical ground point for NASA POWER and SMAP grid extraction used in core AGROVERSE modules.",
        "coordinate_note": (
            "Coordinates 10.7080° N, 76.6390° E were used as the NASA POWER API extraction "
            "point (cache file: power_10.708_76.639.csv). This is the farm-level observational "
            "point and must not be replaced by the Palakkad Town district centroid."
        )
    },
    "palakkad_town_district": {
        "name": "Palakkad Town / District Reference",
        "corridor": "Palakkad District, Kerala, India",
        "lat": 10.7867,
        "lon": 76.6548,
        "role": "Regional meteorological reference centroid",
        "description": "District-level reference point used in secondary handover climate aggregates.",
        "coordinate_note": (
            "Coordinates 10.7867° N, 76.6548° E are the district-level centroid used in "
            "07_UI_HANDOVER JSON metadata. This is NOT the NASA POWER extraction point and "
            "must not replace the farm-level coordinates in crop suitability assessments."
        )
    }
}

# Source Registry definitions (ensuring no silent replacement of sources)
SOURCE_REGISTRY_METADATA = [
    {
        "dataset_name": "NASA POWER Agro-Climatology",
        "source": "NASA Langley Research Center POWER Project",
        "location": "Palakkad Demo Farm (10.708° N, 76.639° E)",
        "coordinates": {"lat": 10.708, "lon": 76.639},
        "time_period": "2020-01-01 to 2025-12-31",
        "resolution": "0.5° x 0.625° native satellite assimilation (~50 km)",
        "units": "Precipitation (mm/day), Temperature 2m (°C), RH 2m (%), Solar Radiation (MJ/m²/day)",
        "verification_status": "Verified Empirical",
        "data_quality": "High - continuous daily physical parameters without model interpolation gaps",
        "intended_use": "Primary baseline meteorological analysis for baseline precipitation, temperature, and heat trends"
    },
    {
        "dataset_name": "NASA SMAP Soil Moisture (Member 3 Aggregated)",
        "source": "NASA SMAP L3 Radiometer (~36 km grid) via Member 3 Handover Analysis",
        "location": "Palakkad District / Station Grid Context (10.7867° N, 76.6548° E)",
        "coordinates": {"lat": 10.7867, "lon": 76.6548},
        "time_period": "2020-01 to 2025-12",
        "resolution": "~36 km coarse grid cell",
        "units": "Volumetric soil moisture (cm³/cm³ or m³/m³)",
        "verification_status": "Verified Empirical Satellite Dataset (Regional Context)",
        "data_quality": "Monthly AM/PM averages and pass counts from Member 3; invalid values (-9999) filtered; regional satellite context only, not farm-level in-situ probe",
        "intended_use": "Landscape-level soil moisture seasonal patterns and drydown context (secondary daily handover series are modeled proxies)"
    },
    {
        "dataset_name": "Member 3 Climate and Risk Assessment",
        "source": "Member 3 Handover Analysis (Aggregated daily observations & statistical thresholds)",
        "location": "Palakkad District / Station Grid Context",
        "coordinates": {"lat": 10.708, "lon": 76.639},
        "time_period": "2020-01 to 2025-12",
        "resolution": "Monthly / Daily Event Summaries",
        "units": "Rainfall (mm), Temperature (°C), Soil Moisture (cm³/cm³), Event counts (days)",
        "verification_status": "Verified Handover Dataset",
        "data_quality": "Structured statistical aggregations, relative percentile thresholds (q25, 7+ day dry spells)",
        "intended_use": "Integrated risk flags, extreme event logs (high rainfall, dry periods), and soil moisture comparison"
    },
    {
        "dataset_name": "Palakkad Agriculture Knowledge Base (Member 4)",
        "source": "Kerala Agricultural University (KAU PoP 2016), ICAR-CPCRI, ICAR-CTCRI, TNAU, IMD",
        "location": "Palakkad Agro-Ecological Units (AEUs), Kerala",
        "coordinates": None,
        "time_period": "Standard agronomic calendars and verified requirements",
        "resolution": "Crop-level specific rules and empirical ranges",
        "units": "Water requirement (mm/crop cycle), qualitative sensitivity classes",
        "verification_status": "Verified Institutional Knowledge Base",
        "data_quality": "Peer-reviewed agronomic literature and official university packages of practice",
        "intended_use": "Crop profiles, seasonal sowing/harvest windows, water requirements, sensitivity matrices, advisory rules"
    }
]

# The 6 mandated crops
CROPS_CATALOG = [
    {"crop_id": "rice", "name": "Rice", "priority": "Core"},
    {"crop_id": "groundnut", "name": "Groundnut", "priority": "Core"},
    {"crop_id": "banana", "name": "Banana", "priority": "Core"},
    {"crop_id": "coconut", "name": "Coconut", "priority": "Core"},
    {"crop_id": "tapioca", "name": "Tapioca / Cassava", "priority": "Core"},
    {"crop_id": "sugarcane", "name": "Sugarcane", "priority": "Optional"}
]
