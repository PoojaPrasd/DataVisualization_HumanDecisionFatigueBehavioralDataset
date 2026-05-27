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
        create_experience_stress_boxplot,
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
        create_experience_stress_boxplot,
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
    fig_t4_4 = create_experience_stress_boxplot(df)
    
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

    # ── Thematic tab background styles ────────────────────────────────────────
    tab_bg = {
        'wellbeing':     'linear-gradient(160deg, #e8f5e9 0%, #c8e6c9 100%)',  # Mint green – calm
        'risk':          'linear-gradient(160deg, #fff3e0 0%, #ffe0b2 100%)',  # Amber – caution
        'workload':      'linear-gradient(160deg, #e3f2fd 0%, #bbdefb 100%)',  # Steel blue – focus
        'recovery':      'linear-gradient(160deg, #f3e5f5 0%, #e1bee7 100%)',  # Lavender – restore
        'intervention':  'linear-gradient(160deg, #fce4ec 0%, #f8bbd0 100%)',  # Rose – urgent
        'archetypes':    'linear-gradient(160deg, #ede7f6 0%, #d1c4e9 100%)',  # Deep violet – insight
        'dictionary':    'linear-gradient(160deg, #e8eaf6 0%, #c5cae9 100%)',  # Soft indigo – reference
    }

    def tab_wrap(children, theme_key):
        return html.Div(children, style={
            'background': tab_bg[theme_key],
            'borderRadius': '0 0 16px 16px',
            'padding': '8px 8px 16px 8px',
            'minHeight': '600px'
        })

    tab1_content = tab_wrap([
        dbc.Row([
            dbc.Col(create_chart_card(fig_t1_1, "Instantly see whether high fatigue is rare or widespread across the organisation."), md=6),
            dbc.Col(create_chart_card(fig_t1_5, "Drill down hierarchically to see how system recommendations distribute across fatigue levels and shift types."), md=6)
        ], className="mb-4 mt-4"),
        dbc.Row([
            dbc.Col(create_chart_card(fig_t1_3, "Assess whether high fatigue states appear directly linked to insufficient sleep."), md=6),
            dbc.Col(create_chart_card(fig_t1_4, "Check whether automated system recommendations align accurately with observed fatigue severity."), md=6)
        ], className="mb-4"),
        dbc.Row([
            dbc.Col(create_chart_card(fig_t1_2, "Distinguish between general stress patterns and isolated extreme cases linked to fatigue."), md=6),
            dbc.Col(create_chart_card(fig_t1_6, "Observe the exact shape of mood score distributions across different shift types."), md=6)
        ], className="mb-4")
    ], 'wellbeing')

    tab2_content = tab_wrap([
        dbc.Row([
            dbc.Col(create_chart_card(fig_t2_1, "Identify if high cognitive load corresponds to higher error rates, and locate risky fatigued cohorts."), md=6),
            dbc.Col(create_chart_card(fig_t2_2, "Density hotspots quickly reveal where stress and fatigue concentrate to flag highest-risk employee states."), md=6)
        ], className="mb-4 mt-4"),
        dbc.Row([
            dbc.Col(create_chart_card(fig_t2_3, "See whether reduced sleep consistently corresponds to higher reported fatigue."), md=6),
            dbc.Col(create_chart_card(fig_t2_4, "View the absolute count of employees suffering from poor sleep vs healthy sleep routines."), md=6)
        ], className="mb-4")
    ], 'risk')

    tab3_content = tab_wrap([
        dbc.Row([
            dbc.Col(create_chart_card(fig_t3_1, "See if high decision volume is associated with more errors, especially for fatigued employees."), md=6),
            dbc.Col(create_chart_card(fig_t3_2, "See if experienced employees handle task switching better, or if task switching uniformly increases errors."), md=6)
        ], className="mb-4 mt-4"),
        dbc.Row([
            dbc.Col(create_chart_card(fig_t3_3, "Identify structural shift timing and experience level factors that heavily drive decision fatigue."), md=6),
            dbc.Col(create_chart_card(fig_t3_4, "Spot complex workload profiles, such as high workload + high fatigue + high error paths."), md=6)
        ], className="mb-4")
    ], 'workload')

    tab4_content = tab_wrap([
        dbc.Row([
            dbc.Col(create_chart_card(fig_t4_1, "Identify if high caffeine is associated with faster or slower decisions depending on hydration."), md=6),
            dbc.Col(create_chart_card(fig_t4_2, "See if physical activity lowers cognitive load only when supported by sufficient sleep."), md=6)
        ], className="mb-4 mt-4"),
        dbc.Row([
            dbc.Col(create_chart_card(fig_t4_3, "Detect mismatches between an employee's perceived sleep quality and actual sleep duration."), md=6),
            dbc.Col(create_chart_card(fig_t4_4, "See how stress levels differ across experience groups and fatigue states."), md=6)
        ], className="mb-4")
    ], 'recovery')

    tab5_content = tab_wrap([
        dbc.Row([
            dbc.Col(create_chart_card(fig_t5_1, "Identify high-risk conditional combinations, such as poor sleep + high stress."), md=6),
            dbc.Col(create_chart_card(fig_t5_4, "Visualize how decision volume flows across intervention recommendation types over the day."), md=6)
        ], className="mb-4 mt-4"),
        dbc.Row([
            dbc.Col(create_chart_card(fig_t5_2, "Identify observations where calculated wellbeing risk directly coincides with performance risk."), md=6),
            dbc.Col(create_chart_card(fig_t5_3, "Evaluate whether the system's categorical recommendations map to genuinely meaningful risk differences."), md=6)
        ], className="mb-4")
    ], 'intervention')

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

    tab6_content = tab_wrap([
        dbc.Row([
            dbc.Col(pca_explainer_card, md=12)
        ], className="mt-4"),
        dbc.Row([
            dbc.Col(create_chart_card(fig_t6_1, "See whether employee observations naturally form distinct wellbeing profiles in 2D space."), md=6),
            dbc.Col(create_chart_card(fig_t6_2, "Understand which original variables (stress, workload, etc.) drive the underlying archetypes."), md=6)
        ], className="mb-4"),
        dbc.Row([
            dbc.Col(create_chart_card(fig_t6_3, "Identify interpretable groupings such as overloaded high-risk employees vs balanced collaborators."), md=12)
        ], className="mb-4"),
        dbc.Row([
            dbc.Col(create_chart_card(fig_t6_4a, "Understand the specific stress, fatigue, and error traits that distinguish each behavioural cluster."), md=6),
            dbc.Col(create_chart_card(fig_t6_4b, "Understand the lifestyle and behavioral traits (sleep, mood, collaboration) defining each cluster."), md=6)
        ], className="mb-4")
    ], 'archetypes')

    # ── TAB 7: DATA DICTIONARY ────────────────────────────────────────────────
    dict_header_style = {
        'backgroundColor': '#3949AB', 'color': '#ffffff', 'padding': '10px 16px',
        'fontSize': '0.85rem', 'fontWeight': '700', 'letterSpacing': '0.5px',
        'borderBottom': '2px solid #283593'
    }
    dict_cell_style = {
        'padding': '10px 16px', 'fontSize': '0.82rem', 'borderBottom': '1px solid #e0e0e0',
        'verticalAlign': 'top', 'lineHeight': '1.5'
    }
    dict_cell_alt = {**dict_cell_style, 'backgroundColor': 'rgba(232,234,246,0.35)'}

    def dict_row(var, dtype, source, desc, alt=False):
        s = dict_cell_alt if alt else dict_cell_style
        badge_color = {'Numeric': '#1565C0', 'Categorical': '#6A1B9A', 'Derived': '#E65100', 'Score': '#2E7D32'}.get(dtype, '#546E7A')
        return html.Tr([
            html.Td(html.Code(var, style={'fontSize': '0.82rem', 'backgroundColor': '#f5f5f5',
                                          'padding': '2px 6px', 'borderRadius': '4px'}), style=s),
            html.Td(html.Span(dtype, style={'backgroundColor': badge_color, 'color': '#fff',
                                            'padding': '2px 8px', 'borderRadius': '12px',
                                            'fontSize': '0.72rem', 'fontWeight': '600'}), style=s),
            html.Td(source, style=s),
            html.Td(desc, style=s)
        ])

    raw_variables = [
        ('Hours_Awake', 'Numeric', 'Raw', 'Total hours the employee has been awake at the time of observation. Higher values indicate longer wakefulness, which is strongly linked to cognitive decline.'),
        ('Decisions_Made', 'Numeric', 'Raw', 'Cumulative number of workplace decisions made during the shift. Reflects cognitive workload volume.'),
        ('Task_Switches', 'Numeric', 'Raw', 'Number of context switches between different tasks. Frequent switching increases cognitive overhead and error probability.'),
        ('Avg_Decision_Time_sec', 'Numeric', 'Raw', 'Average time (in seconds) taken per decision. Longer times may signal cognitive fatigue or increased task complexity.'),
        ('Sleep_Hours_Last_Night', 'Numeric', 'Raw', 'Self-reported total sleep duration the night before. A key predictor of next-day cognitive performance.'),
        ('Time_of_Day', 'Categorical', 'Raw', 'The shift period: Morning, Afternoon, Evening, or Night. Captures circadian rhythm effects on decision quality.'),
        ('Caffeine_Intake_Cups', 'Numeric', 'Raw', 'Number of caffeinated beverages consumed. May temporarily mask fatigue but does not restore actual cognitive function.'),
        ('Stress_Level_1_10', 'Score', 'Raw', 'Self-reported stress level on a 1–10 scale. Higher values indicate acute psychological pressure.'),
        ('Error_Rate', 'Numeric', 'Raw', 'Proportion of incorrect decisions out of total decisions made. The primary performance outcome variable.'),
        ('Cognitive_Load_Score', 'Score', 'Raw', 'Composite measure (0–100) of current mental workload derived from task complexity and volume.'),
        ('Decision_Fatigue_Score', 'Score', 'Raw', 'Composite index (0–100) representing cumulative decision fatigue. Higher = more depleted.'),
        ('Fatigue_Level', 'Categorical', 'Raw', 'Categorical label (Low / Medium / High) derived from the Decision Fatigue Score thresholds.'),
        ('System_Recommendation', 'Categorical', 'Raw', 'Automated intervention label: "Continue" (safe), "Slow Down" (caution), or "Take Break" (critical).'),
        ('Years_at_Company', 'Numeric', 'Raw', 'Employee tenure in years. Used to segment by experience level (New / Mid-level / Senior / Veteran).'),
        ('Self_Reported_Sleep_Quality', 'Categorical', 'Raw', 'Subjective sleep quality rating. May diverge from actual sleep hours, revealing perception gaps.'),
        ('Break_Room_Entry_Count', 'Numeric', 'Raw', 'Number of break room visits during the shift. A proxy for micro-recovery behaviour.'),
        ('Water_Dispenser_Refills', 'Numeric', 'Raw', 'Number of water refills. Used to compute the Hydration Ratio as a wellness indicator.'),
        ('Vending_Machine_Sugar_Purchases', 'Numeric', 'Raw', 'Sugar snack purchases from vending machines. May indicate stress-eating or energy-seeking behaviour.'),
        ('Corporate_Gym_Entry_Mins', 'Numeric', 'Raw', 'Minutes spent in the corporate gym. Used to segment employees by physical activity level.'),
        ('Peer_Collaboration_Pings', 'Numeric', 'Raw', 'Number of collaboration messages sent/received. High values indicate social engagement; low values suggest isolation.'),
        ('Mid_Shift_Mood_Score', 'Score', 'Raw', 'Self-reported mood score captured mid-shift (1–10). Tracks emotional state during the work period.'),
    ]
    derived_variables = [
        ('Decision_Density', 'Derived', 'Computed', 'Decisions Made ÷ Hours Awake. Measures decision-making intensity per hour of wakefulness.'),
        ('Hydration_Ratio', 'Derived', 'Computed', 'Water Refills ÷ (Caffeine Cups + 1). Higher ratio indicates healthier hydration relative to stimulant intake.'),
        ('Sleep_Deficit', 'Derived', 'Computed', 'max(0, 8 − Sleep Hours). Quantifies shortfall from the recommended 8-hour baseline.'),
        ('Fatigue_Risk_Index', 'Derived', 'Computed', 'Weighted composite: 0.35 × Fatigue + 0.25 × Stress + 0.20 × Cog Load + 0.20 × Sleep Deficit. Synthesises multiple risk factors into a single actionable score.'),
        ('Sleep_Group', 'Derived', 'Binned', 'Categorises sleep hours: Poor Sleep (≤5h), Adequate Sleep (5–7h), Good Sleep (>7h).'),
        ('Experience_Group', 'Derived', 'Binned', 'Categorises tenure: New (0–3y), Mid-level (3–7y), Senior (7–15y), Veteran (15+y).'),
        ('Gym_Group', 'Derived', 'Binned', 'Categorises gym minutes: No Activity (0), Low (1–20), Moderate (21–45), High (>45).'),
        ('Stress_Group', 'Derived', 'Binned', 'Categorises stress: Low (1–3), Medium (4–7), High (8–10).'),
        ('Caffeine_Group', 'Derived', 'Binned', 'Categorises caffeine intake: Low (0–1), Medium (2–3), High (>3 cups).'),
        ('PCA_1 / PCA_2', 'Derived', 'PCA', 'First two principal components from 12 standardised features. PC1 captures workload/stress variance; PC2 captures engagement/collaboration variance.'),
        ('Cluster_ID', 'Derived', 'K-Means', 'Cluster assignment (0, 1, or 2) from K-Means on standardised features.'),
        ('Behavioural_Archetype', 'Derived', 'Mapped', 'Human-readable label for each cluster: Collaborative/Balanced, Stressed/Isolated, or Low Engagement.'),
    ]

    all_rows = []
    for i, (var, dtype, source, desc) in enumerate(raw_variables + derived_variables):
        all_rows.append(dict_row(var, dtype, source, desc, alt=(i % 2 == 1)))

    dict_table = html.Table([
        html.Thead(html.Tr([
            html.Th('Variable', style=dict_header_style),
            html.Th('Type', style=dict_header_style),
            html.Th('Source', style=dict_header_style),
            html.Th('Description', style=dict_header_style),
        ])),
        html.Tbody(all_rows)
    ], style={'width': '100%', 'borderCollapse': 'collapse', 'backgroundColor': '#ffffff',
             'borderRadius': '12px', 'overflow': 'hidden', 'boxShadow': '0 2px 12px rgba(0,0,0,0.08)'})

    tab7_content = tab_wrap([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4('📖 Data Dictionary', className='mb-1 fw-bold', style={'color': '#283593'}),
                        html.P('Complete reference of all variables used in this dashboard — including raw measurements, derived metrics, and ML-generated features.',
                               className='text-muted small mb-4'),
                        html.H6('🔹 Raw Variables (from sensor & survey data)', className='fw-bold mb-3',
                                style={'color': '#1565C0'}),
                        html.Hr(style={'borderColor': '#e0e0e0', 'margin': '0 0 4px 0'}),
                    ])
                ], className='shadow-sm rounded-3 border-0 bg-white mb-2', style={'overflow': 'visible'})
            ], md=12)
        ], className='mt-4'),
        dbc.Row([
            dbc.Col(dict_table, md=12)
        ], className='mb-4')
    ], 'dictionary')

    return dbc.Container(
        fluid=True,
        style={
            "minHeight": "100vh",
            "background": "linear-gradient(160deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)",
            "fontFamily": "Inter, sans-serif"
        },
        className="p-4",
        children=[
            dbc.Row([
                dbc.Col(
                    html.Img(src="/assets/banner.png", style={"width": "100%", "maxHeight": "200px", "objectFit": "cover", "borderRadius": "12px"}),
                    className="mb-4 text-center"
                )
            ]),
            dbc.Row([
                dbc.Col(
                    html.H1("Neuropulse: Workforce Decision Safety Dashboard",
                            className="text-center mb-4 fw-bold",
                            style={"color": "#ffffff", "letterSpacing": "-0.5px",
                                   "textShadow": "0 2px 12px rgba(0,0,0,0.4)", "fontSize": "2.2rem"}
                    )
                )
            ]),
            dbc.Tabs([
                dbc.Tab(tab1_content, label="🌿 Wellbeing", tab_id="tab-1", label_style={"fontWeight": "600", "whiteSpace": "nowrap", "padding": "10px 15px"}),
                dbc.Tab(tab2_content, label="⚠️ Risk Profile", tab_id="tab-2", label_style={"fontWeight": "600", "whiteSpace": "nowrap", "padding": "10px 15px"}),
                dbc.Tab(tab3_content, label="⚙️ Workload", tab_id="tab-3", label_style={"fontWeight": "600", "whiteSpace": "nowrap", "padding": "10px 15px"}),
                dbc.Tab(tab4_content, label="🔋 Recovery", tab_id="tab-4", label_style={"fontWeight": "600", "whiteSpace": "nowrap", "padding": "10px 15px"}),
                dbc.Tab(tab5_content, label="🛑 Intervention", tab_id="tab-5", label_style={"fontWeight": "600", "whiteSpace": "nowrap", "padding": "10px 15px"}),
                dbc.Tab(tab6_content, label="👥 Archetypes", tab_id="tab-6", label_style={"fontWeight": "600", "whiteSpace": "nowrap", "padding": "10px 15px"}),
                dbc.Tab(tab7_content, label="📖 Data Dictionary", tab_id="tab-7", label_style={"fontWeight": "600", "whiteSpace": "nowrap", "padding": "10px 15px"}),
            ], id="tabs", active_tab="tab-1", className="mb-4 flex-nowrap overflow-auto", style={"scrollbarWidth": "none"})
        ]
    )
