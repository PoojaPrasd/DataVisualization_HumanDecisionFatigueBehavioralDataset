from dash import Dash, Input, Output, State, ctx, no_update
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import math
import pandas as pd

try:
    from .data_loader import df
    from .layout import (
        FILTER_ALL,
        GRAPH_IDS,
        WELLBEING_GRAPH_IDS,
        create_layout,
        create_tab_contents,
        get_zoom_axis_map,
        _all_filter_value_options,
        is_filter_active,
    )
    from .selection import EMPTY_SELECTION, selection_from_pcp_figure, selection_from_scatter_brush
except ImportError:
    from data_loader import df
    from layout import (
        FILTER_ALL,
        GRAPH_IDS,
        WELLBEING_GRAPH_IDS,
        create_layout,
        create_tab_contents,
        get_zoom_axis_map,
        _all_filter_value_options,
        is_filter_active,
    )
    from selection import EMPTY_SELECTION, selection_from_pcp_figure, selection_from_scatter_brush

# Initialize the Dash app with a Bootstrap theme
app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY], suppress_callback_exceptions=True)
app.title = "Neuropulse Dashboard"

# Set the layout
app.layout = create_layout(df)


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
    Input("reset-selection-btn", "n_clicks"),
    *[Input(graph_id, "relayoutData") for graph_id in GRAPH_IDS],
    *[Input(graph_id, "selectedData") for graph_id in GRAPH_IDS],
    *[Input(graph_id, "clickData") for graph_id in GRAPH_IDS],
    *[Input(graph_id, "restyleData") for graph_id in GRAPH_IDS],
)
def update_dashboard(color_by, target_col, filter_column, filter_values, reset_clicks, *interaction_values):
    relayout_values = interaction_values[:len(GRAPH_IDS)]
    selected_values = interaction_values[len(GRAPH_IDS):len(GRAPH_IDS) * 2]
    click_values = interaction_values[len(GRAPH_IDS) * 2:len(GRAPH_IDS) * 3]
    restyle_values = interaction_values[len(GRAPH_IDS) * 3:]
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
    if triggered_id == "reset-selection-btn":
        wb, risk, workload, interv = create_tab_contents(
            filtered,
            color_by=color_by or "System_Recommendation",
            target_col=target_col or "Error_Rate",
            tabs={"wellbeing", "risk", "intervention"},
        )
        return wb, risk, interv

    target_tabs = None
    if triggered_id in GRAPH_IDS:
        target_tabs = {_graph_tab(triggered_id)}
        graph_index = GRAPH_IDS.index(triggered_id)
        if triggered_prop.endswith(".restyleData"):
            legend_filter = _legend_filter(triggered_id, restyle_values[graph_index], color_by or "System_Recommendation")
            if legend_filter and legend_filter[0] in filtered.columns:
                filtered = filtered[filtered[legend_filter[0]].astype(str) == legend_filter[1]]
        elif triggered_prop.endswith(".relayoutData"):
            relayout_data = relayout_values[graph_index]
            if triggered_id == "risk-stress-target" and relayout_data:
                density_axis_ranges = (_axis_range(relayout_data, "xaxis"), _axis_range(relayout_data, "yaxis"))
            filtered = apply_zoom_filter(filtered, triggered_id, relayout_data, target_col or "Error_Rate")
        elif triggered_prop.endswith(".selectedData"):
            selected_data = selected_values[graph_index]
            filtered = apply_selection_filter(filtered, triggered_id, selected_data, target_col or "Error_Rate")
        elif triggered_prop.endswith(".clickData"):
            click_data = click_values[graph_index]
            filtered = apply_click_filter(filtered, triggered_id, click_data, target_col or "Error_Rate")

    render_tabs = target_tabs or {"wellbeing", "risk", "intervention"}
    wb, risk, workload, interv = create_tab_contents(
        filtered,
        color_by=color_by or "System_Recommendation",
        target_col=target_col or "Error_Rate",
        density_axis_ranges=density_axis_ranges,
        wellbeing_df=filtered if triggered_id in WELLBEING_GRAPH_IDS else df,
        tabs=render_tabs,
    )
    return wb or no_update, risk or no_update, interv or no_update


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


@app.callback(
    Output("selection-store", "data", allow_duplicate=True),
    Input("conf-scatter", "relayoutData"),
    prevent_initial_call=True,
)
def reset_scatter_selection_on_autorange(relayout_data):
    if relayout_data and any(key.endswith("autorange") for key in relayout_data):
        return EMPTY_SELECTION
    raise PreventUpdate


def apply_zoom_filter(data, graph_id, relayout_data, target_col):
    if not relayout_data or any(key.endswith("autorange") for key in relayout_data):
        return data
    if graph_id == "intervention-line":
        return _filter_intervention_line_region(data, relayout_data, target_col)

    axis_map = get_zoom_axis_map(target_col)
    x_col, y_col = axis_map.get(graph_id, (None, None))
    filtered = data

    x_range = _axis_range(relayout_data, "xaxis")
    y_range = _axis_range(relayout_data, "yaxis")
    filtered = _filter_axis_range(filtered, x_col, x_range)
    filtered = _filter_axis_range(filtered, y_col, y_range)
    return filtered


def apply_selection_filter(data, graph_id, selected_data, target_col):
    if not selected_data:
        return data
    if graph_id == "intervention-line":
        return _filter_intervention_line_points(data, selected_data, target_col)

    axis_map = get_zoom_axis_map(target_col)
    x_col, y_col = axis_map.get(graph_id, (None, None))
    if not x_col and not y_col:
        return data

    filtered = data
    ranges = selected_data.get("range") if isinstance(selected_data, dict) else None
    if isinstance(ranges, dict):
        filtered = _filter_axis_range(filtered, x_col, _selection_axis_range(ranges, "x"))
        filtered = _filter_axis_range(filtered, y_col, _selection_axis_range(ranges, "y"))
        return filtered

    points = selected_data.get("points", []) if isinstance(selected_data, dict) else []
    if not points:
        return data
    x_values = [point.get("x") for point in points if "x" in point]
    y_values = [point.get("y") for point in points if "y" in point]
    filtered = _filter_axis_values(filtered, x_col, x_values)
    filtered = _filter_axis_values(filtered, y_col, y_values)
    return filtered


def apply_click_filter(data, graph_id, click_data, target_col):
    if graph_id != "intervention-line" or not click_data:
        return data
    return _filter_intervention_line_points(data, click_data, target_col)


def _graph_tab(graph_id):
    if graph_id in WELLBEING_GRAPH_IDS:
        return "wellbeing"
    if graph_id.startswith("risk-"):
        return "risk"
    if graph_id.startswith("intervention-"):
        return "intervention"
    return "workload"


def _filter_axis_range(data, column, axis_range):
    if not axis_range or not column or column not in data.columns:
        return data
    if _is_numeric(data[column]):
        series = _display_series(data[column], column)
        return data[series.between(axis_range[0], axis_range[1], inclusive="both")]

    selected = _categories_in_range(data[column], column, axis_range)
    if not selected:
        return data
    return data[data[column].astype(str).isin(selected)]


def _filter_intervention_line_region(data, relayout_data, target_col):
    x_range = _axis_range(relayout_data, "xaxis")
    y_range = _axis_range(relayout_data, "yaxis")
    if not x_range and not y_range:
        return data

    agg = _intervention_line_agg(data, target_col)
    if agg.empty:
        return data

    selected_gyms = _categories_in_range(data["Gym_Group"], "Gym_Group", x_range) if x_range else None
    if selected_gyms is not None:
        agg = agg[agg["Gym_Group"].astype(str).isin(selected_gyms)]
    if y_range:
        display_col = _display_column(target_col)
        agg = agg[agg[display_col].between(y_range[0], y_range[1], inclusive="both")]
    return _filter_intervention_line_pairs(data, agg)


def _filter_intervention_line_points(data, point_data, target_col):
    points = point_data.get("points", []) if isinstance(point_data, dict) else []
    if not points:
        ranges = point_data.get("range") if isinstance(point_data, dict) else None
        if isinstance(ranges, dict):
            relayout_like = {}
            if "x" in ranges:
                relayout_like["xaxis.range"] = ranges["x"]
            if "y" in ranges:
                relayout_like["yaxis.range"] = ranges["y"]
            return _filter_intervention_line_region(data, relayout_like, target_col)
        return data

    agg = _intervention_line_agg(data, target_col)
    if agg.empty:
        return data

    pairs = []
    sleep_order = _ordered_values("Sleep_Group", data["Sleep_Group"])
    display_col = _display_column(target_col)
    for point in points:
        gym_group = point.get("x")
        sleep_group = point.get("customdata", [None])[0] if point.get("customdata") else None
        if sleep_group is None:
            sleep_group = point.get("legendgroup") or point.get("curveNumber")
        if isinstance(sleep_group, int) and 0 <= sleep_group < len(sleep_order):
            sleep_group = sleep_order[sleep_group]

        if sleep_group is None and "curveNumber" in point:
            try:
                curve_index = int(point["curveNumber"])
                sleep_group = sleep_order[curve_index] if 0 <= curve_index < len(sleep_order) else None
            except (TypeError, ValueError):
                sleep_group = None

        point_match = agg
        if gym_group is not None:
            point_match = point_match[point_match["Gym_Group"].astype(str) == str(gym_group)]
        if sleep_group is not None:
            point_match = point_match[point_match["Sleep_Group"].astype(str) == str(sleep_group)]
        elif point.get("y") is not None:
            try:
                y_value = float(point["y"])
                point_match = point_match[(point_match[display_col] - y_value).abs() < 1e-9]
            except (TypeError, ValueError):
                pass
        pairs.append(point_match[["Gym_Group", "Sleep_Group"]])

    if not pairs:
        return data
    selected_pairs = pd.concat(pairs).drop_duplicates()
    return _filter_intervention_line_pairs(data, selected_pairs)


def _intervention_line_agg(data, target_col):
    required = ["Gym_Group", "Sleep_Group", target_col]
    if any(column not in data.columns for column in required):
        return data.iloc[0:0].copy()
    display_col = _display_column(target_col)
    plot_data = data.dropna(subset=required).copy()
    if target_col == "Error_Rate":
        plot_data[display_col] = plot_data[target_col] * 100
    else:
        plot_data[display_col] = plot_data[target_col]
    return plot_data.groupby(["Gym_Group", "Sleep_Group"], observed=False)[display_col].mean().reset_index()


def _filter_intervention_line_pairs(data, pairs):
    if pairs.empty:
        return data.iloc[0:0].copy()
    selected = set(zip(pairs["Gym_Group"].astype(str), pairs["Sleep_Group"].astype(str)))
    mask = [
        (str(gym_group), str(sleep_group)) in selected
        for gym_group, sleep_group in zip(data["Gym_Group"], data["Sleep_Group"])
    ]
    return data[mask]


def _display_column(target_col):
    return "Error_Rate_pct" if target_col == "Error_Rate" else target_col


def _filter_axis_values(data, column, values):
    if not values or not column or column not in data.columns:
        return data
    values = [value for value in values if value is not None]
    if not values:
        return data
    if _is_numeric(data[column]):
        try:
            numeric_values = [float(value) for value in values]
        except (TypeError, ValueError):
            return data
        return _filter_axis_range(data, column, (min(numeric_values), max(numeric_values)))
    selected = {str(value) for value in values}
    return data[data[column].astype(str).isin(selected)]


def _categories_in_range(series, column, axis_range):
    categories = _ordered_values(column, series)
    if not categories:
        return []
    start, end = axis_range
    try:
        lo = max(0, int(math.ceil(float(start))))
        hi = min(len(categories) - 1, int(math.floor(float(end))))
        return categories[lo:hi + 1] if lo <= hi else []
    except (TypeError, ValueError):
        start_value, end_value = str(start), str(end)
        if start_value not in categories or end_value not in categories:
            return []
        lo, hi = sorted((categories.index(start_value), categories.index(end_value)))
        return categories[lo:hi + 1]


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
    return column, _ordered_values(column, df[column] if column in df.columns else None, orders)


def _ordered_values(column, series, orders=None):
    orders = orders or {
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
    }
    if series is None:
        return []
    present = set(series.dropna().astype(str))
    if column in orders:
        return [value for value in orders[column] if value in present]
    return sorted(present)


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


def _selection_axis_range(ranges, axis):
    value = ranges.get(axis)
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        return None
    try:
        start = float(value[0])
        end = float(value[1])
    except (TypeError, ValueError):
        return None
    return (min(start, end), max(start, end))


def _is_numeric(series):
    return getattr(series, "dtype", None).kind in "biufc"


if __name__ == '__main__':
    app.run(debug=True, port=8050)
