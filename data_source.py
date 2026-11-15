"""Daily climate series for the farm.

Real data: NASA POWER (https://power.larc.nasa.gov) daily point API, 1990 -> ~5 days ago.
  PRECTOTCORR = rainfall (mm/day), T2M_MAX / T2M = max / mean air temp (deg C),
  GWETROOT = root-zone soil wetness (0-1, shown as %).
The first successful download is cached in ./cache and refreshed weekly.
If NASA POWER cannot be reached, a clearly flagged synthetic demo series is used instead.
"""
import datetime as dt, json, os, time, urllib.request
import numpy as np, pandas as pd

CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")
# In serverless environments (e.g. Vercel), the project directory is read-only.
# We fallback to /tmp/cache if the project directory is not writable.
if not os.access(os.path.dirname(os.path.abspath(__file__)), os.W_OK):
    CACHE_DIR = os.path.join("/tmp", "agroverse_cache")

START = "19900101"


def _fetch_power(lat, lon):
    end = (dt.date.today() - dt.timedelta(days=5)).strftime("%Y%m%d")
    url = ("https://power.larc.nasa.gov/api/temporal/daily/point"
           "?parameters=PRECTOTCORR,T2M_MAX,T2M,GWETROOT&community=AG"
           f"&longitude={lon}&latitude={lat}&start={START}&end={end}&format=JSON")
    with urllib.request.urlopen(url, timeout=10) as r:
        j = json.load(r)
    return _parse_power(j)


def _parse_power(j):
    p = j["properties"]["parameter"]
    df = pd.DataFrame({"rain": p["PRECTOTCORR"], "tmax": p["T2M_MAX"],
                       "tmean": p["T2M"], "soil": p["GWETROOT"]})
    df.index = pd.to_datetime(df.index, format="%Y%m%d")
    df = df.sort_index().replace(-999, np.nan)
    # Preserve missing values (NaN); do NOT convert missing rainfall to 0.0.
    # Confirmed zero-rain observations (0.0) from the API are preserved as 0.0.
    # For temperature and soil wetness, short gaps (≤5 days) are linearly interpolated.
    df[["tmax", "tmean", "soil"]] = df[["tmax", "tmean", "soil"]].interpolate(limit=5)
    df["soil"] = df["soil"] * 100
    return df


def _synthetic():
    """Offline fallback: plausible Palakkad-like climate with a mild warming trend."""
    rng = np.random.default_rng(42)
    idx = pd.date_range("1990-01-01", dt.date.today() - dt.timedelta(days=5), freq="D")
    monthly = np.array([10, 20, 45, 110, 190, 540, 650, 410, 230, 260, 120, 30], float)
    dim = np.array([31, 28.25, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])
    mean = (monthly / dim)[idx.month - 1]
    yfac = {y: rng.normal(1, 0.15) for y in idx.year.unique()}
    mean = mean * np.array([yfac[y] for y in idx.year])
    rain = rng.gamma(0.4, mean / 0.4)
    doy = idx.dayofyear.values
    tmax = (32.5 + 3.0 * np.cos(2 * np.pi * (doy - 105) / 365) + 0.035 * (idx.year.values - 1990)
            + rng.normal(0, 1.2, len(idx)) - 0.012 * rain)
    df = pd.DataFrame({"rain": rain, "tmax": tmax, "tmean": tmax - 5.5}, index=idx)
    df["soil"] = np.clip(28 + 2.1 * df["rain"].rolling(30, min_periods=1).mean(), 15, 92)
    return df


_MEM = {}


def get_series(lat, lon):
    if (lat, lon) in _MEM:
        return _MEM[(lat, lon)]
    out = _get_series(lat, lon)
    if out[1] == "nasa_power":          # keep retrying the real API while only demo data is available
        _MEM[(lat, lon)] = out
    return out


def _get_series(lat, lon):
    """Returns (DataFrame, source) with source in {'nasa_power', 'demo'}."""
    try:
        os.makedirs(CACHE_DIR, exist_ok=True)
    except Exception:
        pass
    f = os.path.join(CACHE_DIR, f"power_{lat:.3f}_{lon:.3f}.csv")
    if os.path.exists(f) and time.time() - os.path.getmtime(f) < 7 * 86400:
        return pd.read_csv(f, index_col=0, parse_dates=True), "nasa_power"
    try:
        df = _fetch_power(lat, lon)
        try:
            df.to_csv(f)
        except Exception:
            pass
        return df, "nasa_power"
    except Exception as e:                      # offline, blocked, API change ...
        print("NASA POWER unavailable, using demo data:", e)
        if os.path.exists(f):                   # stale cache is better than synthetic
            return pd.read_csv(f, index_col=0, parse_dates=True), "nasa_power"
        return _synthetic(), "demo"
