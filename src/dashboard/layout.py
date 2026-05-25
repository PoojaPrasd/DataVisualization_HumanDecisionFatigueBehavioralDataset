from dash import html, dcc
import dash_bootstrap_components as dbc
try:
    from .components import (
        create_fatigue_distribution_bar,
        create_stress_fatigue_boxplot,
        create_sleep_fatigue_boxplot,
        create_system_rec_distribution,
        create_hierarchical_sunburst,
        create_mood_shift_violin,
        create_load_error_scatter,
        create_stress_fatigue_quadrant,
        create_sleep_fatigue_trend,
        create_sleep_error_trend,
        create_decision_error_bubble,
        create_task_error_faceted,
        create_density_fatigue_scatter,
        create_workload_parallel_coords,
        create_caffeine_hydration_heatmap,
        create_gym_sleep_load_heatmap,
        create_sleep_quality_boxplot,
        create_mood_fatigue_quadrant,
        create_perfect_storm_heatmap,
        create_risk_index_scatter,
        create_avg_risk_profile_bar,
        create_intervention_streamgraph,
        create_pca_scatter,
        create_pca_loadings_bar,
        create_cluster_profile_heatmap,
        create_archetype_parallel_coords_risk,
        create_archetype_parallel_coords_behaviour
    )
except ImportError:
    from components import (
        create_fatigue_distribution_bar,
        create_stress_fatigue_boxplot,
        create_sleep_fatigue_boxplot,
        create_system_rec_distribution,
        create_hierarchical_sunburst,
        create_mood_shift_violin,
        create_load_error_scatter,
        create_stress_fatigue_quadrant,
        create_sleep_fatigue_trend,
        create_sleep_error_trend,
        create_decision_error_bubble,
        create_task_error_faceted,
        create_density_fatigue_scatter,
        create_workload_parallel_coords,
        create_caffeine_hydration_heatmap,
        create_gym_sleep_load_heatmap,
        create_sleep_quality_boxplot,
        create_mood_fatigue_quadrant,
        create_perfect_storm_heatmap,
        create_risk_index_scatter,
        create_avg_risk_profile_bar,
        create_intervention_streamgraph,
        create_pca_scatter,
        create_pca_loadings_bar,
        create_cluster_profile_heatmap,
        create_archetype_parallel_coords_risk,
        create_archetype_parallel_coords_behaviour
    )

def create_chart_card(fig, hr_utility):
    return dbc.Card(
        [
            dbc.CardBody([
                html.P(hr_utility, className="text-muted small mb-3 fst-italic"),
                dcc.Graph(figure=fig, style={"minHeight": "350px"})
            ])
        ],
        className="shadow rounded-3 border-0 h-100",
        style={"backgroundColor": "#ffffff", "transition": "transform 0.2s", "overflow": "hidden"}
    )

def create_layout(df):
    # Tab 1 Figures
    fig_t1_1 = create_fatigue_distribution_bar(df)
    fig_t1_2 = create_stress_fatigue_boxplot(df)
    fig_t1_3 = create_sleep_fatigue_boxplot(df)
    fig_t1_4 = create_system_rec_distribution(df)
    fig_t1_5 = create_hierarchical_sunburst(df)
    fig_t1_6 = create_mood_shift_violin(df)
    
    # Tab 2 Figures
    fig_t2_1 = create_load_error_scatter(df)
    fig_t2_2 = create_stress_fatigue_quadrant(df)
    fig_t2_3 = create_sleep_fatigue_trend(df)
    fig_t2_4 = create_sleep_error_trend(df)
    
    # Tab 3 Figures
    fig_t3_1 = create_decision_error_bubble(df)
    fig_t3_2 = create_task_error_faceted(df)
    fig_t3_3 = create_density_fatigue_scatter(df)
    fig_t3_4 = create_workload_parallel_coords(df)
    
    # Tab 4 Figures
    fig_t4_1 = create_caffeine_hydration_heatmap(df)
    fig_t4_2 = create_gym_sleep_load_heatmap(df)
    fig_t4_3 = create_sleep_quality_boxplot(df)
    fig_t4_4 = create_mood_fatigue_quadrant(df)
    
    # Tab 5 Figures
    fig_t5_1 = create_perfect_storm_heatmap(df)
    fig_t5_2 = create_risk_index_scatter(df)
    fig_t5_3 = create_avg_risk_profile_bar(df)
    fig_t5_4 = create_intervention_streamgraph(df) # 4th graph for Tab 5
    
    # Tab 6 Figures
    fig_t6_1 = create_pca_scatter(df)
    fig_t6_2 = create_pca_loadings_bar(df)
    fig_t6_3 = create_cluster_profile_heatmap(df)
    fig_t6_4a = create_archetype_parallel_coords_risk(df)
    fig_t6_4b = create_archetype_parallel_coords_behaviour(df)

    tab1_content = html.Div([
        dbc.Row([
            dbc.Col(create_chart_card(fig_t1_1, "HR Utility: Instantly see whether high fatigue is rare or widespread across the organisation."), md=6),
            dbc.Col(create_chart_card(fig_t1_5, "HR Utility: Drill down hierarchically to see how system recommendations distribute across fatigue levels and shift types."), md=6)
        ], className="mb-4 mt-4"),
        dbc.Row([
            dbc.Col(create_chart_card(fig_t1_3, "HR Utility: Assess whether high fatigue states appear directly linked to insufficient sleep."), md=6),
            dbc.Col(create_chart_card(fig_t1_4, "HR Utility: Check whether automated system recommendations align accurately with observed fatigue severity."), md=6)
        ], className="mb-4"),
        dbc.Row([
            dbc.Col(create_chart_card(fig_t1_2, "HR Utility: Distinguish between general stress patterns and isolated extreme cases linked to fatigue."), md=6),
            dbc.Col(create_chart_card(fig_t1_6, "HR Utility: Observe the exact shape of mood score distributions across different shift types, revealing hidden bipolarities."), md=6)
        ], className="mb-4")
    ])

    tab2_content = html.Div([
        dbc.Row([
            dbc.Col(create_chart_card(fig_t2_1, "HR Utility: Identify if high cognitive load corresponds to higher error rates, and locate risky fatigued cohorts."), md=6),
            dbc.Col(create_chart_card(fig_t2_2, "HR Utility: Density hotspots quickly reveal where stress and fatigue concentrate to flag highest-risk employee states."), md=6)
        ], className="mb-4 mt-4"),
        dbc.Row([
            dbc.Col(create_chart_card(fig_t2_3, "HR Utility: See whether reduced sleep consistently corresponds to higher reported fatigue."), md=6),
            dbc.Col(create_chart_card(fig_t2_4, "HR Utility: View the absolute count of employees suffering from poor sleep vs healthy sleep routines."), md=6)
        ], className="mb-4")
    ])

    tab3_content = html.Div([
        dbc.Row([
            dbc.Col(create_chart_card(fig_t3_1, "HR Utility: See if high decision volume is associated with more errors, especially for fatigued employees."), md=6),
            dbc.Col(create_chart_card(fig_t3_2, "HR Utility: See if experienced employees handle task switching better, or if task switching uniformly increases errors."), md=6)
        ], className="mb-4 mt-4"),
        dbc.Row([
            dbc.Col(create_chart_card(fig_t3_3, "HR Utility: Identify structural shift timing and experience level factors that heavily drive decision fatigue."), md=6),
            dbc.Col(create_chart_card(fig_t3_4, "HR Utility: Spot complex workload profiles, such as high workload + high fatigue + high error paths."), md=6)
        ], className="mb-4")
    ])

    tab4_content = html.Div([
        dbc.Row([
            dbc.Col(create_chart_card(fig_t4_1, "HR Utility: Identify if high caffeine is associated with faster or slower decisions depending on hydration."), md=6),
            dbc.Col(create_chart_card(fig_t4_2, "HR Utility: See if physical activity lowers cognitive load only when supported by sufficient sleep."), md=6)
        ], className="mb-4 mt-4"),
        dbc.Row([
            dbc.Col(create_chart_card(fig_t4_3, "HR Utility: Detect mismatches between an employee's perceived sleep quality and actual sleep duration."), md=6),
            dbc.Col(create_chart_card(fig_t4_4, "HR Utility: Ensure that a reported positive mood is not concealing severe underlying cognitive fatigue."), md=6)
        ], className="mb-4")
    ])

    tab5_content = html.Div([
        dbc.Row([
            dbc.Col(create_chart_card(fig_t5_1, "HR Utility: Identify high-risk conditional combinations, such as poor sleep + high stress + high caffeine."), md=6),
            dbc.Col(create_chart_card(fig_t5_4, "HR Utility: Visualize intervention opportunities over time using streamgraph representing error trends."), md=6)
        ], className="mb-4 mt-4"),
        dbc.Row([
            dbc.Col(create_chart_card(fig_t5_2, "HR Utility: Identify observations where calculated wellbeing risk directly coincides with performance risk."), md=6),
            dbc.Col(create_chart_card(fig_t5_3, "HR Utility: Evaluate whether the system's categorical recommendations map to genuinely meaningful risk differences."), md=6)
        ], className="mb-4")
    ])

    pca_explainer_card = dbc.Card([
        dbc.CardBody([
            html.H5("💡 Understanding PCA and Clustering", className="card-title text-primary"),
            dcc.Markdown('''
            **Principal Component Analysis (PCA)** simplifies our complex 12-dimensional dataset (including stress, errors, sleep, etc.) down to 2 key dimensions (PC1 and PC2) so we can visualize it on a simple 2D map. 
            - Elements driving PC1 typically represent *Workload & Stress*.
            - Elements driving PC2 typically represent *Engagement & Collaboration*.
            
            **K-Means Clustering** then naturally groups similar employees together into distinct "Archetypes". This allows us to quickly identify groups like the high-risk *Stressed/Isolated* cohort versus the healthy *Collaborative* cohort, enabling targeted HR interventions.
            ''', className="small text-secondary mb-0")
        ])
    ], className="shadow-sm rounded-3 border-0 bg-white mb-4")

    tab6_content = html.Div([
        dbc.Row([
            dbc.Col(pca_explainer_card, md=12)
        ], className="mt-4"),
        dbc.Row([
            dbc.Col(create_chart_card(fig_t6_1, "HR Utility: See whether employee observations naturally form distinct wellbeing profiles in 2D space."), md=6),
            dbc.Col(create_chart_card(fig_t6_2, "HR Utility: Understand which original variables (stress, workload, etc.) drive the underlying archetypes."), md=6)
        ], className="mb-4"),
        dbc.Row([
            dbc.Col(create_chart_card(fig_t6_3, "HR Utility: Identify interpretable groupings such as overloaded high-risk employees vs balanced collaborators."), md=12)
        ], className="mb-4"),
        dbc.Row([
            dbc.Col(create_chart_card(fig_t6_4a, "HR Utility: Understand the specific stress, fatigue, and error traits that distinguish each behavioural cluster."), md=6),
            dbc.Col(create_chart_card(fig_t6_4b, "HR Utility: Understand the lifestyle and behavioral traits (sleep, mood, collaboration) defining each cluster."), md=6)
        ], className="mb-4")
    ])

    return dbc.Container(
        fluid=True,
        style={
            "minHeight": "100vh",
            "background": "linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)",
            "fontFamily": "Inter, sans-serif"
        },
        className="p-4",
        children=[
            dbc.Row([
                dbc.Col(
                    html.H1("Neuropulse: Workforce Decision Safety Dashboard", 
                            className="text-center mb-4 fw-bold",
                            style={"color": "#2c3e50", "letterSpacing": "-0.5px"}
                    )
                )
            ]),
            dbc.Tabs([
                dbc.Tab(tab1_content, label="Wellbeing", tab_id="tab-1", label_style={"fontWeight": "600", "whiteSpace": "nowrap", "padding": "10px 15px"}),
                dbc.Tab(tab2_content, label="Risk Profile", tab_id="tab-2", label_style={"fontWeight": "600", "whiteSpace": "nowrap", "padding": "10px 15px"}),
                dbc.Tab(tab3_content, label="Workload", tab_id="tab-3", label_style={"fontWeight": "600", "whiteSpace": "nowrap", "padding": "10px 15px"}),
                dbc.Tab(tab4_content, label="Recovery", tab_id="tab-4", label_style={"fontWeight": "600", "whiteSpace": "nowrap", "padding": "10px 15px"}),
                dbc.Tab(tab5_content, label="Intervention", tab_id="tab-5", label_style={"fontWeight": "600", "whiteSpace": "nowrap", "padding": "10px 15px"}),
                dbc.Tab(tab6_content, label="Archetypes", tab_id="tab-6", label_style={"fontWeight": "600", "whiteSpace": "nowrap", "padding": "10px 15px"}),
            ], id="tabs", active_tab="tab-1", className="mb-4 flex-nowrap overflow-auto", style={"scrollbarWidth": "none"})
        ]
    )
