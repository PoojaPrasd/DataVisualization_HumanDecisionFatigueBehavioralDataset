import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Global Aesthetics
global_template = "plotly_white"
font_family = "Inter, sans-serif"

from .theme import (
    FATIGUE_COLORS as fatigue_colors,
    SYS_REC_COLORS as sys_rec_colors,
    SLEEP_GROUP_COLORS as sleep_group_colors,
    OKABE_ITO as okabe_ito,
    TIME_COLORS as time_of_day_colors,
    apply_theme,
)
cluster_map = {0: 'Collaborative / Balanced', 1: 'Stressed / Isolated', 2: 'Low Engagement'}

def _apply_theme(fig):
    fig.update_layout(
        template=global_template,
        font_family=font_family,
        margin=dict(l=40, r=40, t=60, b=40),
        title_font=dict(size=16, family=font_family, color="#2C3E50"),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        hoverlabel=dict(bgcolor="white", font_size=12, font_family=font_family)
    )
    # Tufte principles: minimal gridlines
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor='rgba(200,200,200,0.3)', zeroline=False)
    return fig


# ── TAB 1: WELLBEING ──────────────────────────────────────────────────────────

def create_fatigue_distribution_bar(df):
    df_plot = df.dropna(subset=['Time_of_Day', 'Fatigue_Level'])
    agg = df_plot.groupby(['Time_of_Day', 'Fatigue_Level'], observed=False).size().reset_index(name='Count')
    fig = px.bar(agg, x='Time_of_Day', y='Count', color='Fatigue_Level',
                 barmode='group',
                 category_orders={'Time_of_Day': ['Morning', 'Afternoon', 'Evening', 'Night'],
                                  'Fatigue_Level': ['Low', 'Medium', 'High']},
                 color_discrete_map=fatigue_colors,
                 labels={'Time_of_Day': 'Time of Day', 'Count': 'Number of Observations'},
                 title='Fatigue Level Composition by Time of Day')
    return _apply_theme(fig)

def create_stress_fatigue_boxplot(df):
    df_plot = df.dropna(subset=['Fatigue_Level', 'Stress_Level_1_10'])
    fig = px.box(df_plot, x='Fatigue_Level', y='Stress_Level_1_10', color='Fatigue_Level',
                 color_discrete_map=fatigue_colors,
                 category_orders={'Fatigue_Level': ['Low', 'Medium', 'High']},
                 labels={'Stress_Level_1_10': 'Stress Level (1-10)', 'Fatigue_Level': 'Fatigue Level'},
                 title='Stress Distribution Across Fatigue Levels')
    return _apply_theme(fig)

def create_sleep_fatigue_boxplot(df):
    df_plot = df.dropna(subset=['Fatigue_Level', 'Sleep_Hours_Last_Night'])
    fig = px.box(df_plot, x='Fatigue_Level', y='Sleep_Hours_Last_Night', color='Fatigue_Level',
                 color_discrete_map=fatigue_colors,
                 category_orders={'Fatigue_Level': ['Low', 'Medium', 'High']},
                 labels={'Sleep_Hours_Last_Night': 'Sleep Hours Last Night', 'Fatigue_Level': 'Fatigue Level'},
                 title='Sleep Hours vs Fatigue Levels')
    return _apply_theme(fig)

def create_system_rec_distribution(df):
    df_plot = df.dropna(subset=['System_Recommendation'])
    agg = df_plot['System_Recommendation'].value_counts().reset_index()
    agg.columns = ['System_Recommendation', 'Count']
    
    # Calculate critical intervention percentage for center annotation
    total = agg['Count'].sum()
    take_break_count = agg[agg['System_Recommendation'] == 'Take Break']['Count'].sum()
    pct = (take_break_count / total) * 100 if total > 0 else 0
    
    fig = px.pie(agg, names='System_Recommendation', values='Count',
                 hole=0.55, title='System Recommendation Distribution',
                 color='System_Recommendation',
                 color_discrete_map=sys_rec_colors)
                 
    # Add multiple idioms: Pull out the critical slice, show values and percentages
    pull_values = [0.1 if rec == 'Take Break' else 0 for rec in agg['System_Recommendation']]
    fig.update_traces(
        textposition='outside', 
        textinfo='label+percent+value',
        pull=pull_values,
        marker=dict(line=dict(color='#ffffff', width=2))
    )
    
    # Center text highlighting critical action
    fig.add_annotation(
        x=0.5, y=0.5, text=f"<b>{pct:.1f}%</b><br>Critical",
        font=dict(size=20, color="#E74C3C"), showarrow=False
    )
    
    return _apply_theme(fig)

def create_hierarchical_sunburst(df):
    df_plot = df.dropna(subset=['System_Recommendation', 'Fatigue_Level', 'Time_of_Day'])
    agg = df_plot.groupby(['System_Recommendation', 'Time_of_Day', 'Fatigue_Level'], observed=False).size().reset_index(name='Count')
    
    # Use facet_row instead of facet_col to stack vertically, preventing label overlap
    fig = px.bar(agg, x='Count', y='Time_of_Day', color='Fatigue_Level',
                 facet_row='System_Recommendation', orientation='h',
                 color_discrete_map=fatigue_colors,
                 category_orders={'System_Recommendation': ['Take Break', 'Slow Down', 'Continue'],
                                  'Time_of_Day': ['Night', 'Evening', 'Afternoon', 'Morning'],
                                  'Fatigue_Level': ['Low', 'Medium', 'High']},
                 title="Hierarchical Breakdown (Faceted Stacked Flow)",
                 labels={'Count': 'Total Interventions', 'Time_of_Day': ''},
                 height=600) # Increased height to fit stacked rows gracefully
                 
    # X labels on bottom of each row
    fig.update_xaxes(matches=None, showticklabels=True, title_text="Interventions")
    
    # Y labels explicitly visible on the far left, zero chance of overlap
    fig.update_yaxes(matches=None, showticklabels=True)
    
    # Make facet headers clean and bold
    fig.for_each_annotation(lambda a: a.update(text=a.text.split('=')[-1], font_size=14, font_weight='bold'))
    
    # Adjust layout for elegance
    fig.update_layout(legend_title_text='Fatigue Level', hovermode='y unified')
    
    return _apply_theme(fig)

def create_mood_shift_violin(df):
    df_plot = df.dropna(subset=['Time_of_Day', 'Mid_Shift_Mood_Score'])
    fig = px.violin(df_plot, x='Time_of_Day', y='Mid_Shift_Mood_Score', color='Time_of_Day',
                    box=True, title='Mood Score Distribution by Time of Day',
                    color_discrete_map=time_of_day_colors,
                    labels={'Time_of_Day': 'Time of Day', 'Mid_Shift_Mood_Score': 'Mid-Shift Mood Score'})
    fig.update_traces(opacity=0.8)
    return _apply_theme(fig)


# ── TAB 2: RISK PROFILE ───────────────────────────────────────────────────────

def create_load_error_scatter(df):
    df_plot = df.dropna(subset=['Cognitive_Load_Score', 'Error_Rate', 'Fatigue_Level'])
    fig = px.scatter(df_plot, x='Cognitive_Load_Score', y='Error_Rate', color='Fatigue_Level',
                     color_discrete_map=fatigue_colors, opacity=0.7, render_mode='svg',
                     labels={'Cognitive_Load_Score': 'Cognitive Load Score', 'Error_Rate': 'Error Rate'},
                     title='Cognitive Load vs Error Rate')
    return _apply_theme(fig)

def create_stress_fatigue_quadrant(df):
    df_plot = df.dropna(subset=['Stress_Level_1_10', 'Decision_Fatigue_Score'])
    fig = px.density_contour(df_plot, x='Stress_Level_1_10', y='Decision_Fatigue_Score',
                             color_discrete_sequence=['#2C3E50'],
                             labels={'Stress_Level_1_10': 'Stress Level (1-10)',
                                     'Decision_Fatigue_Score': 'Decision Fatigue Score'},
                             title='Density Map: Stress vs Decision Fatigue')
    fig.update_traces(contours_coloring="fill", contours_showlabels=False)
    return _apply_theme(fig)

def create_sleep_fatigue_trend(df):
    df_plot = df.dropna(subset=['Sleep_Group', 'Decision_Fatigue_Score'])
    agg = df_plot.groupby('Sleep_Group', observed=False)['Decision_Fatigue_Score'].mean().reset_index()
    fig = px.bar(agg, x='Sleep_Group', y='Decision_Fatigue_Score', color='Sleep_Group',
                 color_discrete_map=sleep_group_colors,
                 labels={'Sleep_Group': 'Sleep Duration Group', 'Decision_Fatigue_Score': 'Avg Decision Fatigue'},
                 title='Average Decision Fatigue by Sleep Group')
    return _apply_theme(fig)

def create_sleep_error_trend(df):
    df_plot = df.dropna(subset=['Sleep_Group'])
    agg = df_plot['Sleep_Group'].value_counts().reset_index()
    agg.columns = ['Sleep_Group', 'Count']
    fig = px.bar(agg, x='Sleep_Group', y='Count', color='Sleep_Group',
                 color_discrete_map=sleep_group_colors,
                 labels={'Sleep_Group': 'Sleep Quality Category', 'Count': 'Number of Employees'},
                 title='Total Population by Sleep Category')
    return _apply_theme(fig)


# ── TAB 3: WORKLOAD ───────────────────────────────────────────────────────────

def create_decision_error_bubble(df):
    df_plot = df.dropna(subset=['Decisions_Made', 'Error_Rate', 'Hours_Awake', 'Fatigue_Level'])
    # Plotly bubble requires size > 0
    df_plot = df_plot[df_plot['Hours_Awake'] > 0]
    fig = px.scatter(df_plot, x='Decisions_Made', y='Error_Rate',
                     size='Hours_Awake', color='Fatigue_Level',
                     color_discrete_map=fatigue_colors, opacity=0.6, render_mode='svg',
                     labels={'Decisions_Made': 'Total Decisions Made', 'Error_Rate': 'Error Rate',
                             'Hours_Awake': 'Hours Awake'},
                     title='Decision Volume vs Error Rate (Bubble Size = Hours Awake)')
    return _apply_theme(fig)

def create_task_error_faceted(df):
    df_plot = df.dropna(subset=['Task_Switches', 'Error_Rate', 'Experience_Group', 'Fatigue_Level'])
    fig = px.scatter(df_plot, x='Task_Switches', y='Error_Rate',
                     facet_col='Experience_Group', color='Fatigue_Level',
                     color_discrete_map=fatigue_colors, opacity=0.7, render_mode='svg',
                     category_orders={'Experience_Group': ['New (0-3)', 'Mid-level (3-7)', 'Senior (7-15)', 'Veteran (15+)']},
                     labels={'Task_Switches': 'Task Switches', 'Error_Rate': 'Error Rate'},
                     title='Task Switching Impact on Errors by Experience')
    # Fix overlapping facet labels: shorten annotation text and reduce font size
    fig.for_each_annotation(lambda a: a.update(text=a.text.split('=')[-1], font_size=11))
    fig.update_xaxes(tickangle=0)
    return _apply_theme(fig)

def create_density_fatigue_scatter(df):
    df_plot = df.dropna(subset=['Time_of_Day', 'Decision_Fatigue_Score', 'Experience_Group'])
    fig = px.box(df_plot, x='Time_of_Day', y='Decision_Fatigue_Score', color='Experience_Group',
                 color_discrete_sequence=okabe_ito,
                 labels={'Time_of_Day': 'Time of Day', 'Decision_Fatigue_Score': 'Decision Fatigue Score'},
                 title='Decision Fatigue Across Shifts by Experience Level')
    return _apply_theme(fig)

PCP_DIMENSIONS = [
    "Hours_Awake",
    "Sleep_Hours_Last_Night",
    "Decisions_Made",
    "Task_Switches",
    "Avg_Decision_Time_sec",
    "Stress_Level_1_10",
    "Cognitive_Load_Score",
    "Error_Rate",
    "Decision_Fatigue_Score",
]

def create_workload_parallel_coords(df, selection=None, sample_size=2500):
    """Brushable PCP. Persists constraintranges from the selection store."""
    if df is None or df.empty:
        return go.Figure()

    sample = df.sample(min(sample_size, len(df)), random_state=42)

    fatigue_code = {"Low": 0, "Medium": 1, "High": 2}
    color_vals = sample["Fatigue_Level"].map(fatigue_code).fillna(1).astype(int)

    persisted = {}
    if selection and selection.get("filters"):
        for f in selection["filters"]:
            persisted[f["col"]] = f["ranges"]

    dimensions = []
    for col in PCP_DIMENSIONS:
        if col not in df.columns:
            continue
        dim = dict(
            label=col.replace("_", " "),
            values=sample[col],
            range=[float(df[col].min()), float(df[col].max())],
        )
        if col in persisted:
            ranges = persisted[col]
            dim["constraintrange"] = ranges[0] if len(ranges) == 1 else ranges
        dimensions.append(dim)

    fig = go.Figure(data=go.Parcoords(
        line=dict(
            color=color_vals,
            colorscale=[[0, fatigue_colors["Low"]],
                        [0.5, fatigue_colors["Moderate"]],
                        [1, fatigue_colors["High"]]],
            cmin=0, cmax=2, showscale=False,
        ),
        dimensions=dimensions,
        labelfont=dict(size=10, color="#495057"),
        tickfont=dict(size=9, color="#6c757d"),
    ))
    apply_theme(fig, height=240, show_legend=False)
    return fig


# ── TAB 4: RECOVERY ───────────────────────────────────────────────────────────

def create_caffeine_hydration_heatmap(df):
    df_plot = df.dropna(subset=['Caffeine_Group', 'Hydration_Ratio', 'Avg_Decision_Time_sec'])
    fig = px.density_heatmap(df_plot, x='Caffeine_Group', y='Hydration_Ratio',
                             z='Avg_Decision_Time_sec', histfunc='avg',
                             color_continuous_scale='Viridis',
                             category_orders={'Caffeine_Group': ['Low', 'Medium', 'High']},
                             labels={'Caffeine_Group': 'Caffeine Intake',
                                     'Hydration_Ratio': 'Hydration Ratio',
                                     'Avg_Decision_Time_sec': 'Avg Decision Time (s)'},
                             title='Caffeine & Hydration Effect on Decision Time')
    return _apply_theme(fig)

def create_gym_sleep_load_heatmap(df):
    df_plot = df.dropna(subset=['Gym_Group', 'Sleep_Group', 'Cognitive_Load_Score'])
    fig = px.density_heatmap(df_plot, x='Gym_Group', y='Sleep_Group',
                             z='Cognitive_Load_Score', histfunc='avg',
                             color_continuous_scale='Blues',
                             category_orders={
                                 'Gym_Group': ['No Activity', 'Low Activity', 'Moderate Activity', 'High Activity'],
                                 'Sleep_Group': ['Poor Sleep', 'Adequate Sleep', 'Good Sleep']
                             },
                             labels={'Gym_Group': 'Gym Activity', 'Sleep_Group': 'Sleep Group',
                                     'Cognitive_Load_Score': 'Avg Cognitive Load'},
                             title='Gym Activity and Sleep vs Cognitive Load')
    return _apply_theme(fig)

def create_sleep_quality_boxplot(df):
    df_plot = df.dropna(subset=['Sleep_Group', 'Mid_Shift_Mood_Score'])
    fig = px.box(df_plot, x='Sleep_Group', y='Mid_Shift_Mood_Score', color='Sleep_Group',
                 color_discrete_map=sleep_group_colors,
                 labels={'Sleep_Group': 'Sleep Group', 'Mid_Shift_Mood_Score': 'Mid-Shift Mood Score'},
                 title='Sleep Duration Effect on Mood')
    return _apply_theme(fig)

def create_experience_stress_boxplot(df):
    df_plot = df.dropna(subset=['Experience_Group', 'Stress_Level_1_10', 'Fatigue_Level'])
    fig = px.box(df_plot, x='Experience_Group', y='Stress_Level_1_10', color='Fatigue_Level',
                 color_discrete_map=fatigue_colors,
                 labels={'Experience_Group': 'Experience Level', 'Stress_Level_1_10': 'Stress Level (1-10)'},
                 title='Stress Resilience by Experience Level')
    return _apply_theme(fig)


# ── TAB 5: INTERVENTION ───────────────────────────────────────────────────────

def create_perfect_storm_heatmap(df):
    df_plot = df.dropna(subset=['Stress_Group', 'Sleep_Group', 'Error_Rate'])
    fig = px.density_heatmap(df_plot, x='Stress_Group', y='Sleep_Group',
                             z='Error_Rate', histfunc='avg',
                             color_continuous_scale='Reds',
                             category_orders={
                                 'Stress_Group': ['Low', 'Medium', 'High'],
                                 'Sleep_Group': ['Poor Sleep', 'Adequate Sleep', 'Good Sleep']
                             },
                             labels={'Stress_Group': 'Stress Level', 'Sleep_Group': 'Sleep Group',
                                     'Error_Rate': 'Avg Error Rate'},
                             title='The "Perfect Storm" of Errors (Stress vs Sleep)')
    return _apply_theme(fig)

def create_risk_index_scatter(df):
    df_plot = df.dropna(subset=['Fatigue_Risk_Index', 'Error_Rate', 'System_Recommendation'])
    fig = px.scatter(df_plot, x='Fatigue_Risk_Index', y='Error_Rate', color='System_Recommendation',
                     color_discrete_map=sys_rec_colors, opacity=0.7, render_mode='svg',
                     labels={'Fatigue_Risk_Index': 'Fatigue Risk Index', 'Error_Rate': 'Error Rate'},
                     title='Composite Risk Index vs Actual Error Rate')
    return _apply_theme(fig)

def create_avg_risk_profile_bar(df):
    df_plot = df.dropna(subset=['System_Recommendation', 'Fatigue_Risk_Index'])
    agg = df_plot.groupby('System_Recommendation', observed=False)['Fatigue_Risk_Index'].mean().reset_index()
    fig = px.bar(agg, x='System_Recommendation', y='Fatigue_Risk_Index', color='System_Recommendation',
                 color_discrete_map=sys_rec_colors,
                 labels={'System_Recommendation': 'System Recommendation',
                         'Fatigue_Risk_Index': 'Avg Risk Index'},
                 title='Average Risk Index by Intervention Type')
    return _apply_theme(fig)

def create_intervention_streamgraph(df):
    df_plot = df.dropna(subset=['Time_of_Day', 'System_Recommendation', 'Decisions_Made'])
    agg = df_plot.groupby(['Time_of_Day', 'System_Recommendation'], observed=False)['Decisions_Made'].sum().reset_index()
    fig = px.area(
        agg, x='Time_of_Day', y='Decisions_Made', color='System_Recommendation',
        line_group='System_Recommendation',
        category_orders={'Time_of_Day': ['Morning', 'Afternoon', 'Evening', 'Night']},
        color_discrete_map=sys_rec_colors,
        labels={'Time_of_Day': 'Time of Day', 'Decisions_Made': 'Total Decisions Made'},
        title='Decision Volume by System Recommendation Over Time'
    )
    fig.update_traces(mode='lines', stackgroup='one', opacity=0.8)
    return _apply_theme(fig)


# ── TAB 6: ARCHETYPES ─────────────────────────────────────────────────────────

def create_pca_scatter(df):
    df_plot = df.dropna(subset=['PCA_1', 'PCA_2', 'Behavioural_Archetype'])
    fig = px.scatter(df_plot, x='PCA_1', y='PCA_2', color='Behavioural_Archetype',
                     opacity=0.7, title='Behavioural Archetypes (PCA Projection)',
                     color_discrete_sequence=okabe_ito, render_mode='svg',
                     labels={'PCA_1': 'Principal Component 1 (Workload & Stress)',
                             'PCA_2': 'Principal Component 2 (Engagement)',
                             'Behavioural_Archetype': 'Archetype'})
    return _apply_theme(fig)

def create_pca_loadings_bar(df):
    if 'pca_loadings' in df.attrs:
        loadings = df.attrs['pca_loadings']
        fig = px.bar(loadings, x=loadings.index, y=['PC1', 'PC2'], barmode='group',
                     title='PCA Feature Loadings (What drives the variance?)',
                     labels={'index': 'Feature', 'value': 'Loading Weight',
                             'variable': 'Principal Component'})
        fig.update_layout(xaxis_tickangle=-45)
        return _apply_theme(fig)
    return go.Figure()

def create_cluster_profile_heatmap(df):
    cols = ['Stress_Level_1_10', 'Cognitive_Load_Score', 'Peer_Collaboration_Pings',
            'Break_Room_Entry_Count', 'Vending_Machine_Sugar_Purchases', 'Error_Rate']
    df_plot = df.dropna(subset=['Behavioural_Archetype'] + cols)
    agg = df_plot.groupby('Behavioural_Archetype')[cols].mean()
    agg_norm = (agg - agg.min()) / (agg.max() - agg.min() + 1e-9)
    # Rename columns for readability
    agg_norm.columns = ['Stress', 'Cog. Load', 'Collab. Pings', 'Break Room', 'Sugar Purchases', 'Error Rate']
    fig = px.imshow(agg_norm, text_auto=".2f", aspect="auto", color_continuous_scale='Magma',
                    title='Archetype Trait Heatmap (Normalized Means)',
                    labels={'x': 'Feature', 'y': 'Archetype'})
    return _apply_theme(fig)

def create_archetype_parallel_coords_risk(df):
    # Logical flow: Stress → Cog Load → Fatigue → Error (cause → effect sequence)
    dims = ['Stress_Level_1_10', 'Cognitive_Load_Score', 'Decision_Fatigue_Score', 'Error_Rate']
    cols = dims + ['Cluster_ID']
    df_plot = df.dropna(subset=cols)

    unique_clusters = sorted(df_plot['Cluster_ID'].unique())
    colors = px.colors.qualitative.Plotly

    short_labels = {
        'Stress_Level_1_10': 'Stress (1-10)',
        'Cognitive_Load_Score': 'Cog. Load',
        'Decision_Fatigue_Score': 'Fatigue Score',
        'Error_Rate': 'Error Rate',
        'Cluster_ID': 'Cluster'
    }

    fig = px.parallel_coordinates(df_plot, color='Cluster_ID', dimensions=dims,
                                  color_continuous_scale=colors,
                                  labels=short_labels,
                                  title='Archetype Risk Profiles (Stress → Load → Fatigue → Error)')
    fig = _apply_theme(fig)
    fig.update_layout(margin=dict(t=100, b=60, l=80, r=80), coloraxis_showscale=False)
    fig.update_coloraxes(showscale=False)
    fig.update_traces(line=dict(showscale=False))
    for i, c in enumerate(unique_clusters):
        name = cluster_map.get(int(c), f"Cluster {int(c)}")
        fig.add_trace(go.Scatter(x=[None], y=[None], mode='lines',
                                 line=dict(color=colors[i % len(colors)], width=4),
                                 name=name))
    fig.update_layout(showlegend=True, legend_title_text='Archetype')
    return fig

def create_archetype_parallel_coords_behaviour(df):
    # Logical flow: Sleep → Mood → Social Engagement → Breaks (recovery → output sequence)
    dims = ['Sleep_Hours_Last_Night', 'Mid_Shift_Mood_Score', 'Peer_Collaboration_Pings',
            'Break_Room_Entry_Count']
    cols = dims + ['Cluster_ID']
    df_plot = df.dropna(subset=cols)

    unique_clusters = sorted(df_plot['Cluster_ID'].unique())
    colors = px.colors.qualitative.Plotly

    short_labels = {
        'Sleep_Hours_Last_Night': 'Sleep (hrs)',
        'Peer_Collaboration_Pings': 'Collab. Pings',
        'Mid_Shift_Mood_Score': 'Mood Score',
        'Break_Room_Entry_Count': 'Break Room',
        'Cluster_ID': 'Cluster'
    }

    fig = px.parallel_coordinates(df_plot, color='Cluster_ID', dimensions=dims,
                                  color_continuous_scale=colors,
                                  labels=short_labels,
                                  title='Archetype Lifestyle (Sleep → Mood → Collaboration → Breaks)')
    fig = _apply_theme(fig)
    fig.update_layout(margin=dict(t=100, b=60, l=80, r=80), coloraxis_showscale=False)
    fig.update_coloraxes(showscale=False)
    fig.update_traces(line=dict(showscale=False))
    for i, c in enumerate(unique_clusters):
        name = cluster_map.get(int(c), f"Cluster {int(c)}")
        fig.add_trace(go.Scatter(x=[None], y=[None], mode='lines',
                                 line=dict(color=colors[i % len(colors)], width=4),
                                 name=name))
    fig.update_layout(showlegend=True, legend_title_text='Archetype')
    return fig


# ── TAB 7: WORKLOAD + CONFOUNDING ────────────────────────────────────────────

def _fit_line(x, y):
    x = np.asarray(x, dtype=float); y = np.asarray(y, dtype=float)
    keep = ~(np.isnan(x) | np.isnan(y))
    x, y = x[keep], y[keep]
    if len(x) < 5 or np.std(x) == 0 or np.std(y) == 0:
        return None
    slope, intercept = np.polyfit(x, y, 1)
    x_line = np.linspace(x.min(), x.max(), 50)
    return x_line, slope * x_line + intercept, float(np.corrcoef(x, y)[0, 1] ** 2)

def create_confounding_scatter(df, x_var, y_var, color_var, selection=None,
                               sample_size=2500):
    """Scatter + per-group regressions. Solid = full data, dashed = brushed subset."""
    from .theme import get_color_map, get_category_order, apply_theme, OKABE_ITO
    from .selection import compute_mask, has_selection

    if df is None or df.empty:
        return go.Figure()

    color_map = get_color_map(color_var) or {}
    order = get_category_order(color_var) or sorted(df[color_var].dropna().unique())
    sample = df.sample(min(sample_size, len(df)), random_state=42)

    fig = go.Figure()
    for i, grp in enumerate(order):
        sub = sample[sample[color_var] == grp]
        if not len(sub):
            continue
        color = color_map.get(grp, OKABE_ITO[i % len(OKABE_ITO)])
        fig.add_trace(go.Scatter(
            x=sub[x_var], y=sub[y_var], mode="markers",
            name=str(grp), legendgroup=str(grp),
            marker=dict(size=5, color=color, opacity=0.4),
        ))

    overall = _fit_line(df[x_var], df[y_var])
    if overall:
        xs, ys, r2 = overall
        fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines",
                                 line=dict(color="#1a1a1a", width=2.5),
                                 name=f"Overall (R²={r2:.2f})"))
    for i, grp in enumerate(order):
        sub = df[df[color_var] == grp]
        ln = _fit_line(sub[x_var], sub[y_var])
        if ln:
            xs, ys, _ = ln
            color = color_map.get(grp, OKABE_ITO[i % len(OKABE_ITO)])
            fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines",
                                     line=dict(color=color, width=2),
                                     legendgroup=str(grp), showlegend=False))

    if has_selection(selection):
        mask = compute_mask(df, selection)
        if mask.sum() > 10:
            df_sel = df.loc[mask]
            sel_overall = _fit_line(df_sel[x_var], df_sel[y_var])
            if sel_overall:
                xs, ys, r2 = sel_overall
                fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines",
                                         line=dict(color="#1a1a1a", width=2, dash="dash"),
                                         name=f"Selection (R²={r2:.2f})"))
            for i, grp in enumerate(order):
                sub = df_sel[df_sel[color_var] == grp]
                ln = _fit_line(sub[x_var], sub[y_var])
                if ln:
                    xs, ys, _ = ln
                    color = color_map.get(grp, OKABE_ITO[i % len(OKABE_ITO)])
                    fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines",
                                             line=dict(color=color, width=2, dash="dash"),
                                             legendgroup=str(grp), showlegend=False))

    apply_theme(fig, height=300)
    fig.update_layout(xaxis_title=x_var.replace("_", " "),
                      yaxis_title=y_var.replace("_", " "),
                      dragmode="select")
    return fig

def create_comparative_box(df, y_var, selection=None):
    from .theme import SELECTION_COLORS, NEUTRAL, apply_theme
    from .selection import compute_mask, has_selection

    fig = go.Figure()
    if has_selection(selection):
        mask = compute_mask(df, selection)
        fig.add_trace(go.Box(y=df.loc[mask, y_var], name="Selected",
                             marker_color=SELECTION_COLORS["Selected"], boxmean=True))
        fig.add_trace(go.Box(y=df.loc[~mask, y_var], name="Not selected",
                             marker_color=SELECTION_COLORS["Not selected"], boxmean=True))
    else:
        fig.add_trace(go.Box(y=df[y_var], name="All data",
                             marker_color=NEUTRAL, boxmean=True))
    apply_theme(fig, height=250)
    fig.update_layout(yaxis_title=y_var.replace("_", " "), showlegend=False)
    return fig

def create_comparative_bar(df, x_cat, y_var, selection=None):
    from .theme import SELECTION_COLORS, NEUTRAL, get_category_order, apply_theme
    from .selection import compute_mask, has_selection

    order = get_category_order(x_cat)
    fig = go.Figure()
    if has_selection(selection):
        mask = compute_mask(df, selection)
        df_use = df.copy()
        df_use["__grp"] = np.where(mask, "Selected", "Not selected")
        agg = df_use.groupby([x_cat, "__grp"], observed=True)[y_var].mean().reset_index()
        for grp_name, color in SELECTION_COLORS.items():
            sub = agg[agg["__grp"] == grp_name]
            fig.add_trace(go.Bar(x=sub[x_cat], y=sub[y_var],
                                 name=grp_name, marker_color=color))
        fig.update_layout(barmode="group")
    else:
        agg = df.groupby(x_cat, observed=True)[y_var].mean().reset_index()
        fig.add_trace(go.Bar(x=agg[x_cat], y=agg[y_var], marker_color=NEUTRAL))
    apply_theme(fig, height=250)
    if order:
        fig.update_xaxes(categoryorder="array", categoryarray=order)
    fig.update_layout(yaxis_title=f"Mean {y_var.replace('_', ' ')}",
                      xaxis_title=x_cat.replace("_", " "))
    return fig
