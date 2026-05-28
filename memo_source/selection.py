"""
selection.py — shared selection state plumbing.
Any chart that originates a selection writes to the same dcc.Store using these helpers.
Any chart that responds to a selection reads from the store and calls compute_mask().
"""
import pandas as pd

EMPTY_SELECTION = {"source": None, "filters": []}

def has_selection(selection):
    return bool(selection and selection.get("filters"))

def compute_mask(df, selection):
    """Translate the selection dict into a boolean Series aligned to df.index."""
    if not has_selection(selection):
        return pd.Series(True, index=df.index)
    mask = pd.Series(True, index=df.index)
    for f in selection["filters"]:
        col = f["col"]
        if col not in df.columns:
            continue
        col_mask = pd.Series(False, index=df.index)
        for lo, hi in f["ranges"]:
            col_mask |= df[col].between(lo, hi)
        mask &= col_mask
    return mask

def selection_from_pcp_figure(figure):
    """Read constraintranges from a PCP figure into a selection dict."""
    filters = []
    if figure and figure.get("data"):
        for dim in figure["data"][0].get("dimensions", []):
            cr, label = dim.get("constraintrange"), dim.get("label")
            if cr and label:
                col = label.replace(" ", "_")
                ranges = cr if isinstance(cr[0], (list, tuple)) else [cr]
                filters.append({"col": col, "ranges": list(ranges)})
    return {"source": "pcp", "filters": filters}

def selection_from_scatter_brush(selected_data, x_col, y_col):
    """Read selectedData from a 2D scatter into a selection dict."""
    if not selected_data:
        return EMPTY_SELECTION
    rng = selected_data.get("range") or {}
    if "x" not in rng or "y" not in rng:
        return EMPTY_SELECTION
    return {
        "source": "scatter",
        "filters": [
            {"col": x_col, "ranges": [list(rng["x"])]},
            {"col": y_col, "ranges": [list(rng["y"])]},
        ],
    }

def selection_from_bar_click(click_data, x_col, df):
    """Read clickData from a bar chart into a single-category selection."""
    if not click_data:
        return EMPTY_SELECTION
    points = click_data.get("points") or []
    if not points:
        return EMPTY_SELECTION
    value = points[0].get("x")
    # For categorical X, build a filter that matches the clicked category.
    # We represent it as a range that matches exactly one value via a tight range.
    if value is None:
        return EMPTY_SELECTION
    return {
        "source": "bar",
        "filters": [{"col": x_col, "ranges": [[value, value]]}],
    }
