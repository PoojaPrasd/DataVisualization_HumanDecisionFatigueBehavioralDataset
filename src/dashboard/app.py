from dash import Dash, Input, Output, State, ctx
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

try:
    from .data_loader import df
    from .layout import (
        FILTER_ALL,
        GRAPH_IDS,
        WELLBEING_GRAPH_IDS,
        create_dashboard_page,
        create_layout,
        create_tab_contents,
        get_zoom_axis_map,
        _all_filter_value_options,
        create_welcome_page,
        is_filter_active,
    )
    from .selection import EMPTY_SELECTION, selection_from_pcp_figure, selection_from_scatter_brush
except ImportError:
    from data_loader import df
    from layout import (
        FILTER_ALL,
        GRAPH_IDS,
        WELLBEING_GRAPH_IDS,
        create_dashboard_page,
        create_layout,
        create_tab_contents,
        get_zoom_axis_map,
        _all_filter_value_options,
        create_welcome_page,
        is_filter_active,
    )
    from selection import EMPTY_SELECTION, selection_from_pcp_figure, selection_from_scatter_brush

# Initialize the Dash app with a Bootstrap theme
app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY], suppress_callback_exceptions=True)
app.title = "Neuropulse Dashboard"

# Set the layout
app.layout = create_layout(df)


@app.callback(
    Output("page-content", "children"),
    Input("login-button", "n_clicks"),
    State("login-username", "value"),
    State("login-password", "value"),
    prevent_initial_call=True,
)
def show_dashboard(n_clicks, username, password):
    if username == "gph" and password == "gph":
        return create_dashboard_page(df)
    return create_welcome_page(login_error=True)


@app.callback(
    Output("dynamic-filter-values", "options"),
    Output("dynamic-filter-values", "value"),
    Output("dynamic-filter-values", "disabled"),
    Input("dynamic-filter-column", "value"),
)
def update_dynamic_filter_values(filter_column):
    if not filter_column or filter_column == FILTER_ALL:
        return [{"label": "All", "value": FILTER_ALL}], [FILTER_ALL], True
    options = _all_filter_value_options(df, filter_column)
    all_values = [option["value"] for option in options]
    return options, all_values, False


@app.callback(
    Output("tab-1-content", "children"),
    Output("tab-2-content", "children"),
    Output("tab-4-content", "children"),
    Input("color-by-filter", "value"),
    Input("target-variable-filter", "value"),
    Input("dynamic-filter-column", "value"),
    Input("dynamic-filter-values", "value"),
    *[Input(graph_id, "relayoutData") for graph_id in GRAPH_IDS],
    *[Input(graph_id, "restyleData") for graph_id in GRAPH_IDS],
)
def update_dashboard(color_by, target_col, filter_column, filter_values, *interaction_values):
    relayout_values = interaction_values[:len(GRAPH_IDS)]
    restyle_values = interaction_values[len(GRAPH_IDS):]
    filtered = df.copy()
    if is_filter_active(filter_column, filter_values):
        filtered = filtered[filtered[filter_column].astype(str).isin(filter_values)]

    density_axis_ranges = None
    legend_filter = None
    try:
        triggered_id = ctx.triggered_id
        triggered_prop = next(iter(ctx.triggered_prop_ids.keys()), "")
    except Exception:
        triggered_id = None
        triggered_prop = ""
    if triggered_id in GRAPH_IDS:
        graph_index = GRAPH_IDS.index(triggered_id)
        if triggered_prop.endswith(".restyleData"):
            legend_filter = _legend_filter(triggered_id, restyle_values[graph_index], color_by or "System_Recommendation")
            if legend_filter and legend_filter[0] in filtered.columns:
                filtered = filtered[filtered[legend_filter[0]].astype(str) == legend_filter[1]]
        elif triggered_id not in WELLBEING_GRAPH_IDS:
            relayout_data = relayout_values[graph_index]
            if triggered_id == "risk-stress-target" and relayout_data:
                density_axis_ranges = (_axis_range(relayout_data, "xaxis"), _axis_range(relayout_data, "yaxis"))
            filtered = apply_zoom_filter(filtered, triggered_id, relayout_data, target_col or "Error_Rate")

    wb, risk, workload, interv = create_tab_contents(
        filtered,
        color_by=color_by or "System_Recommendation",
        target_col=target_col or "Error_Rate",
        density_axis_ranges=density_axis_ranges,
        wellbeing_df=filtered if legend_filter and triggered_id in WELLBEING_GRAPH_IDS else df,
    )
    return wb, risk, interv


@app.callback(
    Output("selection-store", "data", allow_duplicate=True),
    Input("reset-selection-btn", "n_clicks"),
    prevent_initial_call=True,
)
def reset_selection(_):
    return EMPTY_SELECTION


@app.callback(
    Output("selection-store", "data", allow_duplicate=True),
    Input("pcp-graph", "restyleData"),
    State("pcp-graph", "figure"),
    prevent_initial_call=True,
)
def pcp_writes_selection(_, figure):
    return selection_from_pcp_figure(figure)


@app.callback(
    Output("pcp-graph", "figure"),
    Input("selection-store", "data"),
)
def render_pcp(selection):
    if selection and selection.get("source") == "pcp":
        raise PreventUpdate
    try:
        from .components import create_brushable_pcp
    except ImportError:
        from components import create_brushable_pcp
    return create_brushable_pcp(df, selection=selection)


@app.callback(
    Output("conf-scatter", "figure"),
    Output("comp-box", "figure"),
    Input("selection-store", "data"),
    Input("conf-x", "value"),
    Input("target-variable-filter", "value"),
    Input("color-by-filter", "value"),
)
def render_three_charts(selection, conf_x, target_var, color_var):
    try:
        from .components import create_confounding_scatter, create_comparative_box
    except ImportError:
        from components import create_confounding_scatter, create_comparative_box
    y_var = target_var or "Error_Rate"
    color = color_var or "System_Recommendation"
    fig_scatter = create_confounding_scatter(df, conf_x, y_var, color, selection=selection)
    fig_box = create_comparative_box(df, y_var, selection=selection)
    return fig_scatter, fig_box


@app.callback(
    Output("selection-store", "data", allow_duplicate=True),
    Input("conf-scatter", "selectedData"),
    State("conf-x", "value"),
    State("target-variable-filter", "value"),
    prevent_initial_call=True,
)
def scatter_writes_selection(selected, x_col, y_col):
    result = selection_from_scatter_brush(selected, x_col, y_col or "Error_Rate")
    if not result.get("filters"):
        raise PreventUpdate
    return result


def apply_zoom_filter(data, graph_id, relayout_data, target_col):
    if not relayout_data or any(key.endswith("autorange") for key in relayout_data):
        return data

    axis_map = get_zoom_axis_map(target_col)
    x_col, y_col = axis_map.get(graph_id, (None, None))
    filtered = data

    x_range = _axis_range(relayout_data, "xaxis")
    y_range = _axis_range(relayout_data, "yaxis")
    if x_range and x_col in filtered.columns and _is_numeric(filtered[x_col]):
        filtered = filtered[_display_series(filtered[x_col], x_col).between(x_range[0], x_range[1], inclusive="both")]
    if y_range and y_col in filtered.columns and _is_numeric(filtered[y_col]):
        filtered = filtered[_display_series(filtered[y_col], y_col).between(y_range[0], y_range[1], inclusive="both")]
    return filtered


def _display_series(series, column):
    if column == "Error_Rate":
        return series * 100
    return series


def _legend_filter(graph_id, restyle_data, color_by):
    if not restyle_data or not isinstance(restyle_data, (list, tuple)) or len(restyle_data) < 2:
        return None
    trace_indices = restyle_data[1]
    if not trace_indices:
        return None
    try:
        trace_index = int(trace_indices[0])
    except (TypeError, ValueError):
        return None

    column, categories = _legend_categories(graph_id, color_by)
    if not column or trace_index < 0 or trace_index >= len(categories):
        return None
    return column, str(categories[trace_index])


def _legend_categories(graph_id, color_by):
    orders = {
        "Fatigue_Level": ["Low", "Medium", "High"],
        "System_Recommendation": ["Continue", "Slow Down", "Take Break"],
        "Sleep_Group": ["Poor Sleep", "Adequate Sleep", "Good Sleep"],
        "Time_of_Day": ["Morning", "Afternoon", "Evening", "Night"],
        "Experience_Group": ["New (0-3)", "Mid-level (3-7)", "Senior (7-15)", "Veteran (15+)"],
        "Stress_Group": ["Low", "Medium", "High"],
        "Caffeine_Group": ["Low", "Medium", "High"],
        "Gym_Group": ["No Activity", "Low Activity", "Moderate Activity", "High Activity"],
        "Hydration_Group": ["Low Hydration", "Balanced Hydration", "High Hydration"],
        "Sugar_Group": ["No Snacks", "Moderate Snacks", "High Snacks"],
        "Break_Group": ["Few Breaks", "Moderate Breaks", "Frequent Breaks"],
        "Behavioural_Archetype": ["Collaborative / Balanced", "Low Engagement", "Stressed / Isolated"],
        "Anomaly_Cohort": [
            "Expected trend", "Routine stable pocket", "Night peer-support buffer",
            "Veteran stress resilience", "Active high-density resilience",
            "Recovery pacing pocket", "Masked continue risk", "Overload failure pocket",
        ],
    }
    fixed = {
        "wellbeing-fatigue": "Fatigue_Level",
        "wellbeing-sleep-target": "Fatigue_Level",
        "wellbeing-mood-target": "System_Recommendation",
        "intervention-line": "Sleep_Group",
        "intervention-scatter": "System_Recommendation",
    }
    column = fixed.get(graph_id)
    if graph_id in {"risk-load-target", "risk-sleep-target"}:
        column = color_by
    if not column:
        return None, []
    if column in orders:
        values = [value for value in orders[column] if column in df.columns and value in set(df[column].astype(str))]
    elif column in df.columns:
        values = sorted(df[column].dropna().astype(str).unique())
    else:
        values = []
    return column, values


def _axis_range(relayout_data, axis):
    array_key = f"{axis}.range"
    if array_key in relayout_data and isinstance(relayout_data[array_key], (list, tuple)) and len(relayout_data[array_key]) == 2:
        try:
            start = float(relayout_data[array_key][0])
            end = float(relayout_data[array_key][1])
            return (min(start, end), max(start, end))
        except (TypeError, ValueError):
            return None

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


if __name__ == '__main__':
    app.run(debug=True, port=8050)
