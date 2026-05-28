from dash import html, dcc
import dash_bootstrap_components as dbc

try:
    from .components import (
        create_fatigue_distribution_bar,
        create_hierarchical_sunburst,
        create_sleep_target_boxplot,
        create_mood_target_scatter,
        create_load_error_scatter,
        create_stress_fatigue_quadrant,
        create_sleep_fatigue_trend,
        create_decision_error_bubble,
        create_task_error_faceted,
        create_workload_parallel_coords,
        create_decision_density_target_scatter,
        create_gym_sleep_load_heatmap,
        create_perfect_storm_heatmap,
        create_risk_index_scatter,
        create_avg_risk_profile_bar,
        create_intervention_streamgraph,
    )
except ImportError:
    from components import (
        create_fatigue_distribution_bar,
        create_hierarchical_sunburst,
        create_sleep_target_boxplot,
        create_mood_target_scatter,
        create_load_error_scatter,
        create_stress_fatigue_quadrant,
        create_sleep_fatigue_trend,
        create_decision_error_bubble,
        create_task_error_faceted,
        create_workload_parallel_coords,
        create_decision_density_target_scatter,
        create_gym_sleep_load_heatmap,
        create_perfect_storm_heatmap,
        create_risk_index_scatter,
        create_avg_risk_profile_bar,
        create_intervention_streamgraph,
    )


FILTER_COLUMNS = [
    ("Time_of_Day", "Time of day"),
    ("Fatigue_Level", "Fatigue level"),
    ("System_Recommendation", "System recommendation"),
    ("Sleep_Group", "Sleep group"),
    ("Experience_Group", "Experience group"),
    ("Stress_Group", "Stress group"),
    ("Caffeine_Group", "Caffeine group"),
    ("Gym_Group", "Gym group"),
    ("Self_Reported_Sleep_Quality", "Sleep quality"),
    ("Behavioural_Archetype", "Behavioural archetype"),
    ("Anomaly_Cohort", "Anomaly cohort"),
]

COLOR_COLUMNS = [
    ("System_Recommendation", "System recommendation"),
    ("Time_of_Day", "Time of day"),
    ("Sleep_Group", "Sleep group"),
    ("Experience_Group", "Experience group"),
    ("Stress_Group", "Stress group"),
    ("Caffeine_Group", "Caffeine group"),
    ("Gym_Group", "Gym group"),
    ("Self_Reported_Sleep_Quality", "Sleep quality"),
    ("Behavioural_Archetype", "Behavioural archetype"),
]

TARGET_COLUMNS = [
    ("Error_Rate", "Error rate"),
    ("Cognitive_Load_Score", "Cognitive load"),
    ("Stress_Level_1_10", "Stress level"),
    ("Mid_Shift_Mood_Score", "Mood score"),
    ("Avg_Decision_Time_sec", "Decision time"),
]

FILTER_VALUE_ORDERS = {
    "Time_of_Day": ["Morning", "Afternoon", "Evening", "Night"],
    "Fatigue_Level": ["Low", "Medium", "High"],
    "System_Recommendation": ["Continue", "Slow Down", "Take Break"],
    "Sleep_Group": ["Poor Sleep", "Adequate Sleep", "Good Sleep"],
    "Experience_Group": ["New (0-3)", "Mid-level (3-7)", "Senior (7-15)", "Veteran (15+)"],
    "Stress_Group": ["Low", "Medium", "High"],
    "Caffeine_Group": ["Low", "Medium", "High"],
    "Gym_Group": ["No Activity", "Low Activity", "Moderate Activity", "High Activity"],
    "Behavioural_Archetype": ["Collaborative / Balanced", "Low Engagement", "Stressed / Isolated"],
    "Anomaly_Cohort": [
        "Expected trend",
        "Night peer-support buffer",
        "Veteran stress resilience",
        "Active high-density resilience",
        "Masked continue risk",
    ],
}

GRAPH_IDS = [
    "wellbeing-fatigue",
    "wellbeing-breakdown",
    "wellbeing-sleep-target",
    "wellbeing-mood-target",
    "risk-load-target",
    "risk-stress-target",
    "risk-sleep-target",
    "risk-recovery-target",
    "workload-decisions",
    "workload-switches",
    "workload-density",
    "workload-parallel",
    "intervention-context",
    "intervention-line",
    "intervention-scatter",
    "intervention-rec-target",
]


def get_zoom_axis_map(target_col):
    return {
        "wellbeing-fatigue": ("Time_of_Day", None),
        "wellbeing-breakdown": (None, "Time_of_Day"),
        "wellbeing-sleep-target": ("Sleep_Group", target_col),
        "wellbeing-mood-target": ("Mid_Shift_Mood_Score", target_col),
        "risk-load-target": ("Cognitive_Load_Score", target_col),
        "risk-stress-target": ("Stress_Level_1_10", "Log_Error_Rate"),
        "risk-sleep-target": ("Sleep_Group", target_col),
        "risk-recovery-target": ("Gym_Group", "Sleep_Group"),
        "workload-decisions": ("Decisions_Made", target_col),
        "workload-switches": ("Task_Switches", target_col),
        "workload-density": ("Decision_Density", target_col),
        "workload-parallel": (None, None),
        "intervention-context": ("Stress_Group", "Sleep_Group"),
        "intervention-line": ("Time_of_Day", "Decisions_Made"),
        "intervention-scatter": ("Hydration_Ratio", target_col),
        "intervention-rec-target": ("System_Recommendation", target_col),
    }


def create_chart_card(fig, graph_id):
    return dbc.Card(
        [
            dbc.CardBody([
                dcc.Graph(
                    id=graph_id,
                    figure=fig,
                    config={"displayModeBar": False, "responsive": True},
                    style={"height": "calc((100vh - 150px) / 2)", "minHeight": "260px"},
                )
            ], className="p-1")
        ],
        className="shadow-sm rounded-2 border-0 h-100",
        style={"backgroundColor": "#ffffff", "overflow": "hidden"}
    )


def _dropdown_options(df, column):
    if column not in df:
        return []
    values = [str(v) for v in df[column].dropna().unique()]
    ordered_values = FILTER_VALUE_ORDERS.get(column)
    if ordered_values:
        values = [value for value in ordered_values if value in values]
    else:
        values = sorted(values)
    return [{"label": value, "value": value} for value in values]


def create_filter_sidebar(df):
    controls = [
        html.H5("Filters", className="fw-bold mb-2", style={"color": "#1f2d3d"}),
        html.P("Apply one selection set across every tab.", className="text-muted small mb-3"),
        html.Label("Color plots by", className="small fw-semibold mb-1"),
        dcc.Dropdown(
            id="color-by-filter",
            options=[{"label": label, "value": value} for value, label in COLOR_COLUMNS if value in df],
            value="System_Recommendation" if "System_Recommendation" in df else None,
            clearable=False,
            className="mb-2",
        ),
        html.Label("Target variable", className="small fw-semibold mb-1"),
        dcc.Dropdown(
            id="target-variable-filter",
            options=[{"label": label, "value": value} for value, label in TARGET_COLUMNS if value in df],
            value="Error_Rate" if "Error_Rate" in df else None,
            clearable=False,
            className="mb-3",
        ),
        html.Label("Optional filter", className="small fw-semibold mb-1"),
        dcc.Dropdown(
            id="dynamic-filter-column",
            options=[{"label": label, "value": value} for value, label in FILTER_COLUMNS if value in df],
            value=None,
            clearable=True,
            placeholder="Choose a filter",
            className="mb-2",
        ),
        html.Label("Filter values", className="small fw-semibold mb-1"),
        dcc.Dropdown(
            id="dynamic-filter-values",
            options=[],
            value=[],
            multi=True,
            placeholder="All values",
            className="mb-2",
        ),
    ]

    return dbc.Card(
        dbc.CardBody(controls),
        className="shadow border-0",
        style={
            "backgroundColor": "#ffffff",
            "borderRadius": "8px",
            "position": "sticky",
            "top": "8px",
            "maxHeight": "calc(100vh - 58px)",
            "overflowY": "auto",
        },
    )


def create_tab_contents(df, color_by="System_Recommendation", target_col="Error_Rate"):
    fig_wellbeing_1 = create_fatigue_distribution_bar(df, color_by=color_by)
    fig_wellbeing_2 = create_hierarchical_sunburst(df, color_by=color_by)
    fig_wellbeing_3 = create_sleep_target_boxplot(df, color_by=color_by, target_col=target_col)
    fig_wellbeing_4 = create_mood_target_scatter(df, color_by=color_by, target_col=target_col)

    fig_risk_1 = create_load_error_scatter(df, color_by=color_by, target_col=target_col)
    fig_risk_2 = create_stress_fatigue_quadrant(df, target_col=target_col)
    fig_risk_3 = create_sleep_fatigue_trend(df, color_by=color_by, target_col=target_col)
    fig_recovery_2 = create_gym_sleep_load_heatmap(df, target_col=target_col)

    fig_workload_1 = create_decision_error_bubble(df, color_by=color_by, target_col=target_col)
    fig_workload_2 = create_task_error_faceted(df, color_by=color_by, target_col=target_col)
    fig_workload_3 = create_decision_density_target_scatter(df, color_by=color_by, target_col=target_col)
    fig_workload_4 = create_workload_parallel_coords(df, target_col=target_col)

    fig_intervention_line = create_intervention_streamgraph(df, color_by=color_by)
    fig_intervention_scatter = create_risk_index_scatter(df, color_by=color_by, target_col=target_col)
    fig_intervention_context = create_perfect_storm_heatmap(df, target_col=target_col)
    fig_intervention_bar = create_avg_risk_profile_bar(df, target_col=target_col)

    tab_bg = {
        "wellbeing": "linear-gradient(160deg, #e8f5e9 0%, #c8e6c9 100%)",
        "risk_recovery": "linear-gradient(160deg, #fff3e0 0%, #d6ecf2 100%)",
        "workload_memo": "linear-gradient(160deg, #e3f2fd 0%, #f4ecfb 100%)",
        "recovery_intervention": "linear-gradient(160deg, #f3e5f5 0%, #f8bbd0 100%)",
    }

    def tab_wrap(children, theme_key):
        return html.Div(children, style={
            "background": tab_bg[theme_key],
            "borderRadius": "0 0 8px 8px",
            "padding": "6px",
        })

    wellbeing_tab = tab_wrap([
        dbc.Row([
            dbc.Col(create_chart_card(fig_wellbeing_1, "wellbeing-fatigue"), md=6),
            dbc.Col(create_chart_card(fig_wellbeing_2, "wellbeing-breakdown"), md=6),
        ], className="g-2 mb-2"),
        dbc.Row([
            dbc.Col(create_chart_card(fig_wellbeing_3, "wellbeing-sleep-target"), md=6),
            dbc.Col(create_chart_card(fig_wellbeing_4, "wellbeing-mood-target"), md=6),
        ], className="g-2"),
    ], "wellbeing")

    risk_recovery_tab = tab_wrap([
        dbc.Row([
            dbc.Col(create_chart_card(fig_risk_1, "risk-load-target"), md=6),
            dbc.Col(create_chart_card(fig_risk_2, "risk-stress-target"), md=6),
        ], className="g-2 mb-2"),
        dbc.Row([
            dbc.Col(create_chart_card(fig_risk_3, "risk-sleep-target"), md=6),
            dbc.Col(create_chart_card(fig_recovery_2, "risk-recovery-target"), md=6),
        ], className="g-2"),
    ], "risk_recovery")

    workload_memo_tab = tab_wrap([
        dbc.Row([
            dbc.Col(create_chart_card(fig_workload_1, "workload-decisions"), md=6),
            dbc.Col(create_chart_card(fig_workload_2, "workload-switches"), md=6),
        ], className="g-2 mb-2"),
        dbc.Row([
            dbc.Col(create_chart_card(fig_workload_3, "workload-density"), md=6),
            dbc.Col(create_chart_card(fig_workload_4, "workload-parallel"), md=6),
        ], className="g-2"),
    ], "workload_memo")

    recovery_intervention_tab = tab_wrap([
        dbc.Row([
            dbc.Col(create_chart_card(fig_intervention_context, "intervention-context"), md=6),
            dbc.Col(create_chart_card(fig_intervention_line, "intervention-line"), md=6),
        ], className="g-2 mb-2"),
        dbc.Row([
            dbc.Col(create_chart_card(fig_intervention_scatter, "intervention-scatter"), md=6),
            dbc.Col(create_chart_card(fig_intervention_bar, "intervention-rec-target"), md=6),
        ], className="g-2"),
    ], "recovery_intervention")

    return wellbeing_tab, risk_recovery_tab, workload_memo_tab, recovery_intervention_tab


def create_tabs_content(df, color_by="System_Recommendation", target_col="Error_Rate"):
    wellbeing_tab, risk_tab, workload_tab, intervention_tab = create_tab_contents(df, color_by, target_col)
    label_style = {"fontWeight": "600", "whiteSpace": "nowrap", "padding": "10px 15px"}
    return dbc.Tabs([
        dbc.Tab(html.Div(id="tab-1-content", children=wellbeing_tab), label="Wellbeing", tab_id="tab-1", label_style=label_style),
        dbc.Tab(html.Div(id="tab-2-content", children=risk_tab), label="Risk Profile", tab_id="tab-2", label_style=label_style),
        dbc.Tab(html.Div(id="tab-3-content", children=workload_tab), label="Workload & Confounding Memo", tab_id="tab-3", label_style=label_style),
        dbc.Tab(html.Div(id="tab-4-content", children=intervention_tab), label="Intervention and recovery", tab_id="tab-4", label_style=label_style),
    ], id="tabs", active_tab="tab-1", className="mb-2 flex-nowrap overflow-auto", style={"scrollbarWidth": "none"})


def create_layout(df):
    return dbc.Container(
        fluid=True,
        style={
            "height": "100vh",
            "overflow": "hidden",
            "background": "linear-gradient(160deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)",
            "fontFamily": "Inter, sans-serif",
        },
        className="p-2",
        children=[
            dbc.Row([
                dbc.Col(
                    html.H1(
                        "Neuropulse: Workforce Decision Safety Dashboard",
                        className="text-center mb-2 fw-bold",
                        style={
                            "color": "#ffffff",
                            "letterSpacing": "0",
                            "textShadow": "0 2px 12px rgba(0,0,0,0.4)",
            "fontSize": "1.45rem",
                            "lineHeight": "1.15",
                        },
                    )
                )
            ]),
            dbc.Row([
                dbc.Col(create_filter_sidebar(df), width=12, lg=3, xl=2, className="mb-4"),
                dbc.Col(html.Div(id="dashboard-tabs", children=create_tabs_content(df)), width=12, lg=9, xl=10),
            ], className="g-4"),
        ],
    )
