"""
Decision Fatigue Explorer — v2
Linked-view dashboard built around Munzner's nested model:
  - WHY: identify factor relationships; find subgroups; detect confounds
  - HOW: parallel coordinates + brushable scatter + comparative box/bar + regression overlay
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import Dash, html, dcc, callback, Output, Input, State, ctx
import dash_bootstrap_components as dbc

# ── 1. DATA & CONSTANTS ───────────────────────────────────────────────────────
df = pd.read_csv("data/human_decision_fatigue_dataset_enriched.csv")

FATIGUE_ORDER       = ["Low", "Moderate", "High"]
TIME_ORDER          = ["Morning", "Afternoon", "Evening", "Night"]
SLEEP_QUALITY_ORDER = ["Poor", "Fair", "Good", "Excellent"]
FATIGUE_COLORS      = {"Low": "#1D9E75", "Moderate": "#EF9F27", "High": "#E24B4A"}
TIME_COLORS         = {"Morning": "#378ADD", "Afternoon": "#EF9F27",
                       "Evening": "#534AB7", "Night": "#1D9E75"}
GROUP_COLOR_SEQ     = ["#378ADD", "#EF9F27", "#534AB7", "#1D9E75"]

df["Fatigue_Level"] = pd.Categorical(df["Fatigue_Level"], categories=FATIGUE_ORDER, ordered=True)
df["Time_of_Day"]   = pd.Categorical(df["Time_of_Day"], categories=TIME_ORDER, ordered=True)
df["Self_Reported_Sleep_Quality"] = pd.Categorical(
    df["Self_Reported_Sleep_Quality"], categories=SLEEP_QUALITY_ORDER, ordered=True)

# Numeric encoding of Fatigue_Level for the PCP color scale (Parcoords requires numbers)
df["_fatigue_code"] = df["Fatigue_Level"].map({"Low": 0, "Moderate": 1, "High": 2}).astype(int)

PCP_VARS = [
    "Hours_Awake", "Sleep_Hours_Last_Night", "Decisions_Made",
    "Avg_Decision_Time_sec", "Stress_Level_1_10", "Error_Rate",
    "Cognitive_Load_Score", "Decision_Fatigue_Score",
    "Years_at_Company", "Peer_Collaboration_Pings", "Mid_Shift_Mood_Score",
]
NUMERIC_COLS = [c for c in df.columns
                if c not in ["Time_of_Day", "Fatigue_Level", "System_Recommendation",
                             "Self_Reported_Sleep_Quality", "_fatigue_code"]]
CATEGORICAL_COLS = ["Time_of_Day", "Fatigue_Level", "Self_Reported_Sleep_Quality", "System_Recommendation"]

# Pre-sample once for the visual layer (selection logic still operates on full data)
SAMPLE = df.sample(min(2500, len(df)), random_state=42).copy()

# ── 2. APP INIT ───────────────────────────────────────────────────────────────
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Decision Fatigue Explorer"

# ── 3. STYLE CONSTANTS ────────────────────────────────────────────────────────
LABEL_STYLE  = {"fontSize": "12px", "fontWeight": "500", "color": "#6c757d", "marginBottom": "4px"}
HEADER_STYLE = {"fontSize": "13px", "fontWeight": "600", "color": "#1a1a1a", "marginBottom": "4px"}
HINT_STYLE   = {"fontSize": "11px", "color": "#6c757d", "margin": "0 0 6px"}
CARD_STYLE   = {"border": "0.5px solid #dee2e6", "borderRadius": "10px"}
CHART_LAYOUT = dict(
    margin=dict(l=40, r=20, t=10, b=40),
    paper_bgcolor="white", plot_bgcolor="white",
    font=dict(size=11, color="#495057"),
    xaxis=dict(showgrid=True, gridcolor="#f0f0f0", linecolor="#dee2e6"),
    yaxis=dict(showgrid=True, gridcolor="#f0f0f0", linecolor="#dee2e6"),
)

# ── 4. HELPERS ────────────────────────────────────────────────────────────────
def kpi_card(label, value, color):
    return dbc.Card(dbc.CardBody([
        html.P(label, style={"fontSize": "11px", "color": "#6c757d",
                             "marginBottom": "4px", "fontWeight": "500"}),
        html.H3(value, style={"fontSize": "20px", "fontWeight": "600", "color": color, "margin": 0}),
    ]), style=CARD_STYLE)

def fit_line(x, y):
    """Linear regression; returns (x_line, y_line, r2) or None for invalid input."""
    x = np.asarray(x, dtype=float); y = np.asarray(y, dtype=float)
    keep = ~(np.isnan(x) | np.isnan(y))
    x, y = x[keep], y[keep]
    if len(x) < 5 or np.std(x) == 0 or np.std(y) == 0:
        return None
    slope, intercept = np.polyfit(x, y, 1)
    x_line = np.linspace(x.min(), x.max(), 50)
    y_line = slope * x_line + intercept
    r2 = float(np.corrcoef(x, y)[0, 1] ** 2)
    return x_line, y_line, r2

def has_active_selection(pcp_store, scatter_store):
    return bool(pcp_store) or bool(scatter_store and scatter_store.get("x"))

def compute_mask(pcp_store, scatter_store):
    """Combine PCP axis brushes and scatter rectangular brush into one boolean mask."""
    mask = pd.Series(True, index=df.index)
    if pcp_store:
        for col, ranges in pcp_store.items():
            if col not in df.columns or not ranges:
                continue
            col_mask = pd.Series(False, index=df.index)
            for r in ranges:
                col_mask |= df[col].between(r[0], r[1])
            mask &= col_mask
    if scatter_store and scatter_store.get("x"):
        xr, yr = scatter_store["x"], scatter_store["y"]
        mask &= df[scatter_store["x_col"]].between(xr[0], xr[1])
        mask &= df[scatter_store["y_col"]].between(yr[0], yr[1])
    return mask

# ── 5. FIGURES ────────────────────────────────────────────────────────────────
def make_pcp(pcp_store):
    """Parallel coordinates plot — colored by fatigue level, brushable on every axis."""
    dimensions = []
    for col in PCP_VARS:
        dim = dict(
            label=col.replace("_", " "),
            values=SAMPLE[col],
            range=[df[col].min(), df[col].max()],
        )
        # Persist user brushes across re-renders
        if pcp_store and col in pcp_store:
            dim["constraintrange"] = pcp_store[col]
        dimensions.append(dim)

    fig = go.Figure(data=go.Parcoords(
        line=dict(
            color=SAMPLE["_fatigue_code"],
            colorscale=[[0, FATIGUE_COLORS["Low"]],
                        [0.5, FATIGUE_COLORS["Moderate"]],
                        [1, FATIGUE_COLORS["High"]]],
            cmin=0, cmax=2, showscale=False,
        ),
        dimensions=dimensions,
        labelfont=dict(size=10, color="#495057"),
        tickfont=dict(size=9, color="#6c757d"),
    ))
    fig.update_layout(margin=dict(l=60, r=60, t=40, b=20),
                      paper_bgcolor="white", plot_bgcolor="white", height=380)
    return fig

def make_brush_scatter(scatter_store):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=SAMPLE["Years_at_Company"], y=SAMPLE["Peer_Collaboration_Pings"],
        mode="markers",
        marker=dict(size=5, color="#378ADD", opacity=0.35),
        hovertemplate="Years: %{x:.1f}<br>Pings: %{y}<extra></extra>",
        showlegend=False,
    ))
    if scatter_store and scatter_store.get("x"):
        xr, yr = scatter_store["x"], scatter_store["y"]
        fig.add_shape(type="rect", x0=xr[0], x1=xr[1], y0=yr[0], y1=yr[1],
                      line=dict(color="#E24B4A", width=2, dash="dot"),
                      fillcolor="rgba(226,75,74,0.08)", layer="above")
    fig.update_layout(**CHART_LAYOUT)
    fig.update_layout(xaxis_title="Years at Company",
                      yaxis_title="Peer Collaboration Pings",
                      dragmode="select", height=320)
    return fig

def make_box(mask, has_sel, y_var):
    fig = go.Figure()
    if has_sel:
        fig.add_trace(go.Box(y=df.loc[mask, y_var], name="Selected",
                             marker_color="#E24B4A", boxmean=True))
        fig.add_trace(go.Box(y=df.loc[~mask, y_var], name="Not selected",
                             marker_color="#adb5bd", boxmean=True))
    else:
        fig.add_trace(go.Box(y=df[y_var], name="All data",
                             marker_color="#6c757d", boxmean=True))
    fig.update_layout(**CHART_LAYOUT)
    fig.update_layout(yaxis_title=y_var.replace("_", " "), showlegend=False, height=320)
    return fig

def make_bar(mask, has_sel, x_cat, y_var):
    fig = go.Figure()
    if has_sel:
        df_use = df.copy(); df_use["__grp"] = np.where(mask, "Selected", "Not selected")
        agg = (df_use.groupby([x_cat, "__grp"], observed=True)[y_var]
                       .mean().reset_index())
        for grp, color in [("Selected", "#E24B4A"), ("Not selected", "#adb5bd")]:
            sub = agg[agg["__grp"] == grp]
            fig.add_trace(go.Bar(x=sub[x_cat], y=sub[y_var], name=grp,
                                 marker_color=color))
        fig.update_layout(barmode="group")
    else:
        agg = df.groupby(x_cat, observed=True)[y_var].mean().reset_index()
        fig.add_trace(go.Bar(x=agg[x_cat], y=agg[y_var], marker_color="#6c757d"))
    fig.update_layout(**CHART_LAYOUT)
    fig.update_layout(yaxis_title=f"Mean {y_var.replace('_', ' ')}",
                      xaxis_title=x_cat.replace("_", " "), height=320,
                      legend=dict(orientation="h", y=1.02, x=0, font=dict(size=10)))
    return fig

def make_confounding(mask, has_sel, x_var, y_var, color_cat):
    """Scatter + per-group OLS lines (solid = full data, dashed = brushed subset)."""
    color_map = {"Fatigue_Level": FATIGUE_COLORS, "Time_of_Day": TIME_COLORS}.get(color_cat)
    groups = (df[color_cat].cat.categories.tolist()
              if hasattr(df[color_cat], "cat") else sorted(df[color_cat].unique()))
    group_color = lambda i, g: (color_map[g] if color_map else GROUP_COLOR_SEQ[i % len(GROUP_COLOR_SEQ)])

    fig = go.Figure()
    # Scatter points (sampled, by group)
    for i, grp in enumerate(groups):
        sub = SAMPLE[SAMPLE[color_cat] == grp]
        if not len(sub):
            continue
        fig.add_trace(go.Scatter(
            x=sub[x_var], y=sub[y_var], mode="markers",
            name=str(grp), legendgroup=str(grp),
            marker=dict(size=5, color=group_color(i, grp), opacity=0.4),
        ))

    # Solid: overall regression on FULL data
    overall = fit_line(df[x_var], df[y_var])
    if overall:
        xs, ys, r2 = overall
        fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines",
                                 line=dict(color="#1a1a1a", width=2.5),
                                 name=f"Overall (R²={r2:.2f})",
                                 legendgroup="overall"))
    # Solid: per-group regression on FULL data
    for i, grp in enumerate(groups):
        sub = df[df[color_cat] == grp]
        ln = fit_line(sub[x_var], sub[y_var])
        if ln:
            xs, ys, r2 = ln
            fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines",
                                     line=dict(color=group_color(i, grp), width=2),
                                     legendgroup=str(grp), showlegend=False,
                                     hovertemplate=f"{grp} R²={r2:.2f}<extra></extra>"))

    # Dashed: same lines but fit on the BRUSHED subset (only if user has brushed)
    if has_sel and mask.sum() > 10:
        df_sel = df.loc[mask]
        sel_overall = fit_line(df_sel[x_var], df_sel[y_var])
        if sel_overall:
            xs, ys, r2 = sel_overall
            fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines",
                                     line=dict(color="#1a1a1a", width=2, dash="dash"),
                                     name=f"Overall · selection (R²={r2:.2f})",
                                     legendgroup="overall_sel"))
        for i, grp in enumerate(groups):
            sub = df_sel[df_sel[color_cat] == grp]
            ln = fit_line(sub[x_var], sub[y_var])
            if ln:
                xs, ys, r2 = ln
                fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines",
                                         line=dict(color=group_color(i, grp), width=2, dash="dash"),
                                         legendgroup=str(grp), showlegend=False,
                                         hovertemplate=f"{grp} sel R²={r2:.2f}<extra></extra>"))

    fig.update_layout(**CHART_LAYOUT)
    fig.update_layout(xaxis_title=x_var.replace("_", " "),
                      yaxis_title=y_var.replace("_", " "), height=420,
                      legend=dict(orientation="h", yanchor="bottom", y=1.02,
                                  xanchor="left", x=0, font=dict(size=10)))
    return fig

# ── 6. DROPDOWN OPTIONS ───────────────────────────────────────────────────────
NUM_OPTS = [{"label": c.replace("_", " "), "value": c} for c in NUMERIC_COLS]
CAT_OPTS = [{"label": c.replace("_", " "), "value": c} for c in CATEGORICAL_COLS]

# ── 7. LAYOUT ─────────────────────────────────────────────────────────────────
app.layout = dbc.Container(
    fluid=True,
    style={"backgroundColor": "#f8f9fa", "minHeight": "100vh", "padding": "24px"},
    children=[
        dcc.Store(id="pcp-store", data={}),
        dcc.Store(id="scatter-store", data={}),

        # Header
        dbc.Row(dbc.Col(html.Div([
            html.H1("Decision Fatigue Explorer",
                    style={"fontSize": "22px", "fontWeight": "600",
                           "color": "#1a1a1a", "margin": 0}),
            html.P("HR Director view — 25,000 employee decision states · linked-view exploratory analysis",
                   style={"fontSize": "13px", "color": "#6c757d", "margin": 0}),
        ], style={"marginBottom": "20px"}))),

        # KPI row (last card is dynamic)
        dbc.Row([
            dbc.Col(kpi_card("Records", f"{len(df):,}", "#378ADD"), width=3),
            dbc.Col(kpi_card("Avg fatigue", f"{df['Decision_Fatigue_Score'].mean():.1f}", "#EF9F27"), width=3),
            dbc.Col(kpi_card("Avg error rate", f"{df['Error_Rate'].mean():.3f}", "#E24B4A"), width=3),
            dbc.Col(html.Div(id="selection-kpi"), width=3),
        ], className="mb-3"),

        # Section A — Parallel Coordinates
        dbc.Row(dbc.Col(dbc.Card(dbc.CardBody([
            html.Div([
                html.P("A · Multidimensional view — Parallel Coordinates", style=HEADER_STYLE),
                html.P("Drag along any axis to brush a range. Multiple axes combine with AND.", style=HINT_STYLE),
                html.Button("Reset all brushes", id="reset-btn", n_clicks=0,
                            style={"fontSize": "11px", "padding": "4px 10px",
                                   "border": "0.5px solid #dee2e6", "borderRadius": "6px",
                                   "background": "white", "cursor": "pointer"}),
            ]),
            dcc.Graph(id="pcp-graph", config={"displayModeBar": False}),
        ]), style=CARD_STYLE)), className="mb-3"),

        # Section B — three linked views driven by brushing
        dbc.Row([
            dbc.Col(dbc.Card(dbc.CardBody([
                html.P("B1 · Brushable scatter — Years × Pings", style=HEADER_STYLE),
                html.P("Box-select to define an employee subgroup.", style=HINT_STYLE),
                dcc.Graph(id="brush-scatter",
                          config={"displayModeBar": True,
                                  "modeBarButtonsToRemove": ["lasso2d", "autoScale2d", "zoom2d", "pan2d"],
                                  "displaylogo": False}),
            ]), style=CARD_STYLE), width=4),

            dbc.Col(dbc.Card(dbc.CardBody([
                html.P("B2 · Selected vs not — distribution comparison", style=HEADER_STYLE),
                html.Label("Compare on:", style={**LABEL_STYLE, "fontSize": "11px"}),
                dcc.Dropdown(id="box-y", options=NUM_OPTS, value="Error_Rate",
                             clearable=False, style={"fontSize": "11px", "marginBottom": "4px"}),
                dcc.Graph(id="box-graph", config={"displayModeBar": False}),
            ]), style=CARD_STYLE), width=4),

            dbc.Col(dbc.Card(dbc.CardBody([
                html.P("B3 · Mean by category, split by selection", style=HEADER_STYLE),
                html.Label("X (category):", style={**LABEL_STYLE, "fontSize": "11px"}),
                dcc.Dropdown(id="bar-x", options=CAT_OPTS, value="Time_of_Day",
                             clearable=False, style={"fontSize": "11px", "marginBottom": "4px"}),
                dcc.Graph(id="bar-graph", config={"displayModeBar": False}),
            ]), style=CARD_STYLE), width=4),
        ], className="mb-3"),

        # Section C — Confounding analysis
        dbc.Row(dbc.Col(dbc.Card(dbc.CardBody([
            html.P("C · Confounding analysis — overall vs per-group regression", style=HEADER_STYLE),
            html.P("Solid = full data, dashed = brushed selection. Compare slopes to detect interaction or Simpson-like effects.",
                   style=HINT_STYLE),
            dbc.Row([
                dbc.Col([html.Label("X axis", style={**LABEL_STYLE, "fontSize": "11px"}),
                         dcc.Dropdown(id="conf-x", options=NUM_OPTS, value="Hours_Awake",
                                      clearable=False, style={"fontSize": "12px"})], width=4),
                dbc.Col([html.Label("Y axis", style={**LABEL_STYLE, "fontSize": "11px"}),
                         dcc.Dropdown(id="conf-y", options=NUM_OPTS, value="Error_Rate",
                                      clearable=False, style={"fontSize": "12px"})], width=4),
                dbc.Col([html.Label("Color by (categorical)", style={**LABEL_STYLE, "fontSize": "11px"}),
                         dcc.Dropdown(id="conf-color", options=CAT_OPTS, value="Time_of_Day",
                                      clearable=False, style={"fontSize": "12px"})], width=4),
            ], className="mb-2"),
            dcc.Graph(id="conf-graph", config={"displayModeBar": False}),
        ]), style=CARD_STYLE))),
    ],
)

# ── 8. CALLBACKS ──────────────────────────────────────────────────────────────
@callback(
    Output("pcp-store", "data"),
    Input("pcp-graph", "restyleData"),
    Input("reset-btn", "n_clicks"),
    State("pcp-graph", "figure"),
    prevent_initial_call=True,
)
def update_pcp_store(restyle, reset_clicks, figure):
    """Read constraintranges from the PCP figure into a JSON-friendly store."""
    if ctx.triggered_id == "reset-btn":
        return {}
    new_state = {}
    if figure and figure.get("data"):
        for dim in figure["data"][0].get("dimensions", []):
            cr, label = dim.get("constraintrange"), dim.get("label")
            if cr and label:
                col = label.replace(" ", "_")
                # Normalize to list-of-pairs: [[lo,hi]] or [[lo1,hi1],[lo2,hi2]]
                new_state[col] = cr if isinstance(cr[0], (list, tuple)) else [cr]
    return new_state

@callback(
    Output("scatter-store", "data"),
    Input("brush-scatter", "selectedData"),
    Input("reset-btn", "n_clicks"),
    prevent_initial_call=True,
)
def update_scatter_store(selected, reset_clicks):
    if ctx.triggered_id == "reset-btn":
        return {}
    if not selected:
        return {}
    rng = selected.get("range", {})
    if not rng or "x" not in rng:
        return {}
    return {"x": rng["x"], "y": rng["y"],
            "x_col": "Years_at_Company", "y_col": "Peer_Collaboration_Pings"}

@callback(
    Output("pcp-graph", "figure"),
    Output("brush-scatter", "figure"),
    Output("box-graph", "figure"),
    Output("bar-graph", "figure"),
    Output("conf-graph", "figure"),
    Output("selection-kpi", "children"),
    Input("pcp-store", "data"),
    Input("scatter-store", "data"),
    Input("box-y", "value"),
    Input("bar-x", "value"),
    Input("conf-x", "value"),
    Input("conf-y", "value"),
    Input("conf-color", "value"),
)
def render_all(pcp_store, scatter_store, box_y, bar_x, conf_x, conf_y, conf_color):
    has_sel = has_active_selection(pcp_store, scatter_store)
    mask = compute_mask(pcp_store, scatter_store)

    fig_pcp     = make_pcp(pcp_store)
    fig_scatter = make_brush_scatter(scatter_store)
    fig_box     = make_box(mask, has_sel, box_y)
    fig_bar     = make_bar(mask, has_sel, bar_x, box_y)
    fig_conf    = make_confounding(mask, has_sel, conf_x, conf_y, conf_color)

    if has_sel:
        n_sel = int(mask.sum())
        kpi = kpi_card("Selected records", f"{n_sel:,} ({n_sel/len(df)*100:.1f}%)", "#534AB7")
    else:
        kpi = kpi_card("Selected records", "— none —", "#6c757d")

    return fig_pcp, fig_scatter, fig_box, fig_bar, fig_conf, kpi


if __name__ == "__main__":
    app.run(debug=True)
