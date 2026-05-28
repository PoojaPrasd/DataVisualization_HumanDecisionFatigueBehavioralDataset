from dash import Dash, Input, Output, ctx
import dash_bootstrap_components as dbc
import numpy as np
try:
    from .data_loader import df
    from .layout import (
        GRAPH_IDS, create_layout, create_tab_contents,
        get_zoom_axis_map, _dropdown_options
    )
except ImportError:
    from data_loader import df
    from layout import (
        GRAPH_IDS, create_layout, create_tab_contents,
        get_zoom_axis_map, _dropdown_options
    )

# Initialize the Dash app with a Bootstrap theme
app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
app.title = "Neuropulse Dashboard"

# Set the layout
app.layout = create_layout(df)


@app.callback(
    Output("dynamic-filter-values", "options"),
    Output("dynamic-filter-values", "value"),
    Input("dynamic-filter-column", "value"),
)
def update_dynamic_filter_values(filter_column):
    if not filter_column:
        return [], []
    return _dropdown_options(df, filter_column), []


@app.callback(
    Output("tab-1-content", "children"),
    Output("tab-2-content", "children"),
    Output("tab-3-content", "children"),
    Output("tab-4-content", "children"),
    Input("color-by-filter", "value"),
    Input("target-variable-filter", "value"),
    Input("dynamic-filter-column", "value"),
    Input("dynamic-filter-values", "value"),
    *[Input(graph_id, "relayoutData") for graph_id in GRAPH_IDS],
)
def update_dashboard(color_by, target_col, filter_column, filter_values, *relayout_values):
    filtered = df.copy()
    if filter_column in filtered and filter_values:
        filtered = filtered[filtered[filter_column].astype(str).isin(filter_values)]

    try:
        triggered_id = ctx.triggered_id
    except Exception:
        triggered_id = None
    if triggered_id in GRAPH_IDS:
        relayout_data = relayout_values[GRAPH_IDS.index(triggered_id)]
        filtered = apply_zoom_filter(filtered, triggered_id, relayout_data, target_col or "Error_Rate")

    return create_tab_contents(
        filtered,
        color_by=color_by or "System_Recommendation",
        target_col=target_col or "Error_Rate",
    )


def apply_zoom_filter(data, graph_id, relayout_data, target_col):
    if not relayout_data or any(key.endswith("autorange") for key in relayout_data):
        return data

    axis_map = get_zoom_axis_map(target_col)
    x_col, y_col = axis_map.get(graph_id, (None, None))
    filtered = data

    x_range = _axis_range(relayout_data, "xaxis")
    y_range = _axis_range(relayout_data, "yaxis")
    if x_range and x_col in filtered and _is_numeric(filtered[x_col]):
        filtered = filtered[filtered[x_col].between(x_range[0], x_range[1], inclusive="both")]
    if y_col == "Log_Error_Rate" and y_range and "Error_Rate" in filtered:
        log_error = np.log10(filtered["Error_Rate"].clip(lower=0) + 0.001)
        filtered = filtered[log_error.between(y_range[0], y_range[1], inclusive="both")]
        return filtered
    if y_range and y_col in filtered and _is_numeric(filtered[y_col]):
        filtered = filtered[filtered[y_col].between(y_range[0], y_range[1], inclusive="both")]
    return filtered


def _axis_range(relayout_data, axis):
    start_key = f"{axis}.range[0]"
    end_key = f"{axis}.range[1]"
    if start_key not in relayout_data or end_key not in relayout_data:
        return None
    try:
        start = float(relayout_data[start_key])
        end = float(relayout_data[end_key])
    except (TypeError, ValueError):
        return None
    return (min(start, end), max(start, end))


def _is_numeric(series):
    return getattr(series, "dtype", None).kind in "biufc"


# We provide a main execution block to allow running the app directly
if __name__ == '__main__':
    # Run the server on localhost port 8050
    app.run(debug=True, port=8050)
