"""Turns a daily series + a user-chosen date window into everything the dashboard shows.
Focused strictly on the 2020–2025 operational monitoring period with a 1991–2020 historical baseline.
"""
import numpy as np, pandas as pd
from scipy_free_stats import percentile_of_score

HEAT_C = 35.0          # a "heat stress day" = daily max temperature >= 35 deg C
HIST_BASE = (1991, 2020) # 30-year WMO climate-normal period used as historical reference
TARGET_YEARS = list(range(2020, 2026)) # [2020, 2021, 2022, 2023, 2024, 2025]
DATASET_END = pd.Timestamp("2025-12-31")


def _window_stats(df, s, e):
    w = df.loc[s:e]
    if len(w) == 0:
        return None
    # If the window is a single week/month, require at least 80% coverage
    req_len = max(1, int((e - s).days * 0.8))
    valid_rain = w.rain.dropna()
    valid_tmax = w.tmax.dropna()
    if len(valid_rain) < req_len or len(valid_tmax) < req_len:
        return None
    return dict(
        rain=float(valid_rain.sum()),
        tmax=float(valid_tmax.mean()),
        heat=int((valid_tmax >= HEAT_C).sum()),
        soil=float(w.soil.dropna().mean()) if len(w.soil.dropna()) > 0 else np.nan,
        maxday=float(valid_rain.max()) if len(valid_rain) > 0 else 0.0,
        rain_obs=len(valid_rain),
        total_days=len(w)
    )


def analyze(df, start, end):
    start, end = pd.Timestamp(start), pd.Timestamp(end)
    single = start == end
    if single:
        start, end = start - pd.Timedelta(days=3), end + pd.Timedelta(days=3)

    # Actual observations available (capped at 2025-12-31 per handover dataset)
    last_obs = min(df.index[-1], DATASET_END)
    first_obs = df.index[0]
    obs_start = max(start, pd.Timestamp("2020-01-01"))
    obs_end = min(end, last_obs)

    # Primary analysis window
    w = df.loc[obs_start:obs_end]
    if len(w) == 0:
        # Fallback to nearest window if completely out of bounds
        w = df.loc[pd.Timestamp("2020-01-01"):last_obs]
        obs_start, obs_end = w.index[0], w.index[-1]

    span = (obs_end - obs_start).days + 1
    valid_rain = w.rain.dropna()
    valid_tmax = w.tmax.dropna()
    valid_soil = w.soil.dropna()

    sel_rain = float(valid_rain.sum()) if len(valid_rain) > 0 else 0.0
    sel_tmax = float(valid_tmax.mean()) if len(valid_tmax) > 0 else 0.0
    sel_heat = int((valid_tmax >= HEAT_C).sum()) if len(valid_tmax) > 0 else 0
    sel_soil = float(valid_soil.mean()) if len(valid_soil) > 0 else 0.0
    sel_maxday = float(valid_rain.max()) if len(valid_rain) > 0 else 0.0
    rain_obs_count = len(valid_rain)

    is_multi_year = (end - start).days > 366
    sel_year = end.year if end.year in TARGET_YEARS else 2025

    # -------------------------------------------------------------------
    # 1. Lower Historical Charts (Focused strictly on 2020–2026)
    # -------------------------------------------------------------------
    years = []
    rains = []
    tmaxs = []
    heats = []

    if is_multi_year:
        # Compare full calendar years within 2020–2026
        for y in TARGET_YEARS:
            y_start = pd.Timestamp(f"{y}-01-01")
            y_end = pd.Timestamp(f"{y}-12-31")
            if y_start > last_obs:
                continue
            y_w = df.loc[y_start:min(y_end, last_obs)]
            if len(y_w) >= 15: # At least partial coverage
                st = _window_stats(df, y_start, min(y_end, last_obs))
                if st:
                    years.append(y)
                    rains.append(round(st["rain"], 1))
                    tmaxs.append(round(st["tmax"], 2))
                    heats.append(st["heat"])
    else:
        # Compare the same calendar window across 2020–2026
        for y in TARGET_YEARS:
            try:
                # Handle leap year Feb 29 gracefully
                s_y = start.replace(year=y)
            except ValueError:
                s_y = start.replace(year=y, day=28)
            try:
                e_y = end.replace(year=y)
            except ValueError:
                e_y = end.replace(year=y, day=28)

            if s_y > last_obs:
                continue
            e_y = min(e_y, last_obs)
            st = _window_stats(df, s_y, e_y)
            if st:
                years.append(y)
                rains.append(round(st["rain"], 1))
                tmaxs.append(round(st["tmax"], 2))
                heats.append(st["heat"])

    # If no data is available for target years, do not substitute hardcoded arrays.
    climate_warning = None
    if not years:
        climate_warning = "Observational data is unavailable for the requested years."

    # -------------------------------------------------------------------
    # 2. Historical Baseline (1991–2020 Climatological Reference)
    # -------------------------------------------------------------------
    hist_rains = []
    hist_tmaxs = []
    hist_heats = []

    if is_multi_year:
        # Scaled annual 1991–2020 normal
        for y in range(HIST_BASE[0], HIST_BASE[1] + 1):
            y_w = df.loc[f"{y}-01-01":f"{y}-12-31"]
            if len(y_w) >= 300:
                st = _window_stats(df, pd.Timestamp(f"{y}-01-01"), pd.Timestamp(f"{y}-12-31"))
                if st:
                    hist_rains.append(st["rain"])
                    hist_tmaxs.append(st["tmax"])
                    hist_heats.append(st["heat"])
    else:
        # Same calendar dates across 1991–2020
        for y in range(HIST_BASE[0], HIST_BASE[1] + 1):
            try:
                s_y = start.replace(year=y)
            except ValueError:
                s_y = start.replace(year=y, day=28)
            try:
                e_y = end.replace(year=y)
            except ValueError:
                e_y = end.replace(year=y, day=28)
            st = _window_stats(df, s_y, e_y)
            if st:
                hist_rains.append(st["rain"])
                hist_tmaxs.append(st["tmax"])
                hist_heats.append(st["heat"])

    # Baseline averages: do not substitute hardcoded defaults if historical data is unavailable
    base_rain = float(np.mean(hist_rains)) if hist_rains else None
    base_tmax = float(np.mean(hist_tmaxs)) if hist_tmaxs else None
    base_heat = float(np.mean(hist_heats)) if hist_heats else None

    # If user selected a multi-year range, compare average annual rate
    n_sel_years = max(1.0, span / 365.25)
    sel_rain_annualized = sel_rain / n_sel_years if is_multi_year else sel_rain
    sel_heat_annualized = sel_heat / n_sel_years if is_multi_year else sel_heat

    rain_diff_pct = round((sel_rain_annualized - base_rain) / (base_rain or 1.0) * 100.0, 1) if base_rain is not None else 0.0
    tmax_diff = round(sel_tmax - base_tmax, 2) if base_tmax is not None else 0.0
    heat_diff = round(sel_heat_annualized - base_heat, 1) if base_heat is not None else 0.0

    # Soil Percentile against 2020–2026 range
    soil_all = df.loc["2020-01-01":last_obs]["soil"].dropna().values
    soil_pct = percentile_of_score(soil_all, sel_soil) if len(soil_all) > 0 else 50.0
    soil_label = "Low" if soil_pct < 33 else "Moderate" if soil_pct < 67 else "High"

    # -------------------------------------------------------------------
    # 3. Environmental Observational Indicators
    # -------------------------------------------------------------------
    # High rainfall threshold is an observational indicator of heavy rain; it does NOT infer or prove field-level flooding.
    # Days >= 35°C is an observational indicator of hot days; it is NOT a universal crop physiological stress prediction.
    ws = 100 - soil_pct
    ws_lvl = ("High", "red") if ws >= 67 else ("Moderate", "amber") if ws >= 33 else ("Low", "green")
    fl_lvl = ("High", "red") if sel_maxday >= 115 else ("Moderate", "amber") if sel_maxday >= 64.5 else ("Low", "green")
    heat_frac = sel_heat / max(1, span)
    ht_lvl = ("High", "red") if heat_frac >= .30 else ("Moderate", "amber") if heat_frac >= .10 else ("Low", "green")

    risks = [
        {"name": "Low soil moisture indicator", "level": ws_lvl[0], "cls": ws_lvl[1], "pct": int(np.clip(ws, 8, 96))},
        {"name": "Heavy rainfall exposure indicator", "level": fl_lvl[0], "cls": fl_lvl[1], "pct": int(np.clip(sel_maxday / 150 * 100, 8, 96))},
        {"name": "High temperature indicator (≥35 °C)", "level": ht_lvl[0], "cls": ht_lvl[1], "pct": int(np.clip(heat_frac / .5 * 100, 8, 96))},
    ]

    # -------------------------------------------------------------------
    # 4. Environmental Trend Chart Series
    # -------------------------------------------------------------------
    if span <= 62:
        labels = [d.strftime("%d %b") for d in w.index]
        rain_s, soil_s, mode = w.rain.tolist(), w.soil.tolist(), "daily"
    else:
        m = w.resample("MS").agg({"rain": "sum", "soil": "mean"})
        if span >= 300:
            g = m.groupby(m.index.month).mean()
            labels = [pd.Timestamp(2000, i, 1).strftime("%b") for i in g.index]
            rain_s, soil_s, mode = g.rain.tolist(), g.soil.tolist(), "climatology"
        else:
            labels = [d.strftime("%b %y") for d in m.index]
            rain_s, soil_s, mode = m.rain.tolist(), m.soil.tolist(), "monthly"

    # Sparkline series: yearly records in 2020–2026
    rain_sparks = [r for r in rains]
    soil_sparks = [float(df.loc[f"{y}"].soil.mean()) for y in years if len(df.loc[f"{y}"]) > 0]
    heat_sparks = [h for h in heats]

    change = dict(
        years=years,
        tmax=tmaxs,
        rain=rains,
        heat=heats,
        sel_year=sel_year if sel_year in years else (years[-1] if years else None),
        sel_tmax=sel_tmax,
        sel_rain=sel_rain if not is_multi_year else sel_rain_annualized,
        sel_heat=sel_heat if not is_multi_year else int(round(sel_heat_annualized)),
        base_tmax=base_tmax,
        base_rain=base_rain,
        base_heat=base_heat,
        tmax_diff=tmax_diff,
        rain_diff=round(sel_rain_annualized - base_rain, 1) if (base_rain is not None and sel_rain_annualized is not None) else 0.0,
        rain_diff_pct=rain_diff_pct,
        heat_diff=heat_diff,
        n_years=len(years),
        first=years[0] if years else None,
        last=years[-1] if years else None,
        is_multi_year=is_multi_year,
        warning=climate_warning
    )

    return dict(
        start=obs_start,
        end=obs_end,
        span=span,
        single=single,
        kpi=dict(
            rain=sel_rain,
            rain_delta=rain_diff_pct,
            rain_spark=rain_sparks,
            soil=sel_soil,
            soil_pct=soil_pct,
            soil_label=soil_label,
            soil_spark=soil_sparks,
            heat=sel_heat,
            heat_spark=heat_sparks,
            tmax=sel_tmax
        ),
        risks=risks,
        trend=dict(labels=labels, rain=rain_s, soil=soil_s, mode=mode),
        change=change
    )
