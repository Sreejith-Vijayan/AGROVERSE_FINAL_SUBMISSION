"""Pure-Python SVG chart builders (no JS chart library needed)."""
import math


def sparkbars(vals, color, w=70, h=34):
    if not vals:
        return ''
    m = max(vals) or 1; n = len(vals); bw = w / n
    out = [f'<svg viewBox="0 0 {w} {h}" width="{w}" height="{h}">']
    for i, v in enumerate(vals):
        bh = v / m * (h - 2)
        out.append(f'<rect x="{i*bw+1:.1f}" y="{h-bh:.1f}" width="{bw-2:.1f}" height="{bh:.1f}" rx="1" fill="{color}"/>')
    out.append('</svg>')
    return "".join(out)


def sparkline(vals, color, w=80, h=34):
    if not vals or len(vals) < 2:
        return ''
    lo, hi = min(vals), max(vals); n = len(vals)
    pts = [(i * (w - 2) / (n - 1) + 1, h - 3 - (v - lo) / (hi - lo or 1) * (h - 8)) for i, v in enumerate(vals)]
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    area = d + f" L{pts[-1][0]:.1f},{h} L{pts[0][0]:.1f},{h} Z"
    return (f'<svg viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
            f'<path d="{area}" fill="{color}" opacity=".12"/>'
            f'<path d="{d}" fill="none" stroke="{color}" stroke-width="1.6"/></svg>')



def _nice(v):
    if v <= 0: return 1
    p = 10 ** math.floor(math.log10(v)); f = v / p
    return (1 if f <= 1 else 2 if f <= 2 else 2.5 if f <= 2.5 else 5 if f <= 5 else 10) * p


def trends_chart(labels, rain, soil, w=520, h=185):
    L, R, T, B = 42, 40, 12, 24
    pw, ph = w - L - R, h - T - B
    n = max(len(labels), 2)
    rmax, smax = _nice(max(rain + [1])), 100 if max(soil + [0]) > 75 else 75
    x = lambda i: L + pw * (i / (n - 1))
    yr = lambda v: T + ph * (1 - v / rmax)
    ym = lambda v: T + ph * (1 - v / smax)
    s = [f'<svg viewBox="0 0 {w} {h}" width="100%" preserveAspectRatio="xMidYMid meet">']
    for k in range(4):
        g = rmax * k / 3; y = yr(g); gl = f"{g:.0f}" if rmax >= 6 else f"{g:.1f}"
        s.append(f'<line x1="{L}" y1="{y:.1f}" x2="{w-R}" y2="{y:.1f}" stroke="#e5e9ec"/>')
        s.append(f'<text x="{L-6}" y="{y+3:.1f}" text-anchor="end" font-size="8.5" fill="#667">{gl}</text>')
        gs = smax * k / 3
        s.append(f'<text x="{w-R+6}" y="{ym(gs)+3:.1f}" font-size="8.5" fill="#667">{gs:.0f}</text>')
    step = max(1, len(labels) // 12)
    for i, lab in enumerate(labels):
        if i % step == 0:
            s.append(f'<text x="{x(i):.1f}" y="{h-8}" text-anchor="middle" font-size="8.5" fill="#667">{lab}</text>')
    soil_p = " ".join(f"{x(i):.1f},{ym(v):.1f}" for i, v in enumerate(soil))
    rain_p = " ".join(f"{x(i):.1f},{yr(v):.1f}" for i, v in enumerate(rain))
    s.append(f'<polyline points="{soil_p}" fill="none" stroke="#3f9b5b" stroke-width="2"/>')
    s.append(f'<polyline points="{rain_p}" fill="none" stroke="#3a86c8" stroke-width="2"/>')
    if len(labels) <= 14:
        for i, v in enumerate(rain):
            s.append(f'<circle cx="{x(i):.1f}" cy="{yr(v):.1f}" r="2.6" fill="#fff" stroke="#3a86c8" stroke-width="1.5"/>')
        for i, v in enumerate(soil):
            s.append(f'<circle cx="{x(i):.1f}" cy="{ym(v):.1f}" r="2.6" fill="#fff" stroke="#3f9b5b" stroke-width="1.5"/>')
    s.append(f'<text transform="translate(9,{T+ph/2}) rotate(-90)" text-anchor="middle" font-size="8.5" fill="#667">Rainfall (mm)</text>')
    s.append(f'<text transform="translate({w-6},{T+ph/2}) rotate(90)" text-anchor="middle" font-size="8.5" fill="#667">Soil Moisture (%)</text>')
    s.append('</svg>')
    return "".join(s)


def year_chart(years, vals, color, unit, sel_year, w=330, h=165):
    """Values per year + straight-line trend; the selected year is highlighted."""
    if not years or not vals or len(years) == 0 or len(vals) == 0:
        return f'<svg viewBox="0 0 {w} {h}" width="100%"><text x="{w/2}" y="{h/2}" text-anchor="middle" font-size="11" fill="#889">No Data Available</text></svg>'
    L, R, T, B = 40, 10, 12, 24
    pw, ph = w - L - R, h - T - B
    lo, hi = min(vals), max(vals); pad = (hi - lo) * .15 or 1
    lo, hi = lo - pad, hi + pad
    x = lambda yv: L + pw * (yv - years[0]) / max(1, years[-1] - years[0])
    y = lambda v: T + ph * (1 - (v - lo) / (hi - lo))
    s = [f'<svg viewBox="0 0 {w} {h}" width="100%" preserveAspectRatio="xMidYMid meet">']
    for k in range(4):
        g = lo + (hi - lo) * k / 3
        gl = f"{g:.0f}" if hi - lo >= 12 else f"{g:.1f}"
        s.append(f'<line x1="{L}" y1="{y(g):.1f}" x2="{w-R}" y2="{y(g):.1f}" stroke="#e5e9ec"/>')
        s.append(f'<text x="{L-5}" y="{y(g)+3:.1f}" text-anchor="end" font-size="8.5" fill="#667">{gl}</text>')
    for yv in range(years[0], years[-1] + 1, max(1, (years[-1] - years[0]) // 6)):
        s.append(f'<text x="{x(yv):.1f}" y="{h-8}" text-anchor="middle" font-size="8.5" fill="#667">{yv}</text>')
    for yv, v in zip(years, vals):
        s.append(f'<rect x="{x(yv)-3:.1f}" y="{y(v):.1f}" width="6" height="{max(0, T+ph-y(v)):.1f}" fill="{color}" opacity=".28"/>')
    n = len(years); mx = sum(years) / n; my = sum(vals) / n
    den = sum((a - mx) ** 2 for a in years) or 1
    m = sum((a - mx) * (b - my) for a, b in zip(years, vals)) / den
    y0, y1 = my + m * (years[0] - mx), my + m * (years[-1] - mx)
    s.append(f'<line x1="{x(years[0]):.1f}" y1="{y(y0):.1f}" x2="{x(years[-1]):.1f}" y2="{y(y1):.1f}" stroke="{color}" stroke-width="2" stroke-dasharray="5 3"/>')
    if sel_year in years:
        v = vals[years.index(sel_year)]
        s.append(f'<circle cx="{x(sel_year):.1f}" cy="{y(v):.1f}" r="5" fill="#fff" stroke="{color}" stroke-width="2.2"/>')
    s.append(f'<text transform="translate(9,{T+ph/2}) rotate(-90)" text-anchor="middle" font-size="8.5" fill="#667">{unit}</text>')
    s.append('</svg>')
    return "".join(s)
