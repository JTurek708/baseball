"""
Shared helpers used across data source modules.
"""
import math


def clean_nan(d: dict) -> dict:
    """Replace NaN/inf with None so JSON serialization doesn't crash.
    JSON spec doesn't support NaN/Infinity; pandas produces them freely
    for missing data. This makes any dict safe to serialize.
    """
    out = {}
    for k, v in d.items():
        if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
            out[k] = None
        else:
            out[k] = v
    return out