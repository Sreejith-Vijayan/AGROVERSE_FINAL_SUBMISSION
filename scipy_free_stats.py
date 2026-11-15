import numpy as np

def percentile_of_score(a, score):
    """Percentage of values in `a` that are <= score (no SciPy needed)."""
    a = np.asarray(a, float)
    return float((a <= score).mean() * 100)
