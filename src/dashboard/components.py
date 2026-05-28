import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Global Aesthetics
global_template = "plotly_white"
font_family = "Inter, sans-serif"

# Perceptually uniform and colorblind-aware palettes
fatigue_colors = {'Low': '#2ECC71', 'Medium': '#F1C40F', 'High': '#E74C3C'}
sys_rec_colors = {'Continue': '#27AE60', 'Slow Down': '#F1C40F', 'Take Break': '#E74C3C'}  # Traffic-light: Green → Yellow → Red
sleep_group_colors = {'Poor Sleep': '#E74C3C', 'Adequate Sleep': '#F1C40F', 'Good Sleep': '#2ECC71'}
okabe_ito = ['#E69F00', '#56B4E9', '#009E73', '#F0E442', '#0072B2', '#D55E00', '#CC79A7', '#000000']
time_of_day_colors = {'Morning': '#FF9F1C', 'Afternoon': '#2EC4B6', 'Evening': '#7B68EE', 'Night': '#1B263B'}  # Warm sunrise / Teal / Indigo / Dark navy
cluster_map = {0: 'Collaborative / Balanced', 1: 'Stressed / Isolated', 2: 'Low Engagement'}
CATEGORY_ORDERS = {
    'Fatigue_Level': ['Low', 'Medium', 'High'],
    'System_Recommendation': ['Continue', 'Slow Down', 'Take Break'],
    'Sleep_Group': ['Poor Sleep', 'Adequate Sleep', 'Good Sleep'],
    'Stress_Group': ['Low', 'Medium', 'High'],
    'Caffeine_Group': ['Low', 'Medium', 'High'],
    'Gym_Group': ['No Activity', 'Low Activity', 'Moderate Activity', 'High Activity'],
    'Time_of_Day': ['Morning', 'Afternoon', 'Evening', 'Night'],
    'Experience_Group': ['New (0-3)', 'Mid-level (3-7)', 'Senior (7-15)', 'Veteran (15+)'],
    'Behavioural_Archetype': ['Collaborative / Balanced', 'Low Engagement', 'Stressed / Isolated'],
    'Anomaly_Cohort': [
        'Expected trend',
        'Night peer-support buffer',
        'Veteran stress resilience',
        'Active high-density resilience',
        'Masked continue risk',
    ],
}
COLOR_MAPS = {
    'Fatigue_Level': fatigue_colors,
    'System_Recommendation': sys_rec_colors,
    'Sleep_Group': sleep_group_colors,
    'Time_of_Day': time_of_day_colors,
}
axis_labels = {
    'Hours_Awake': 'Hours Awake',
    'Decisions_Made': 'Decisions Made',
    'Task_Switches': 'Task Switches',
    'Avg_Decision_Time_sec': 'Avg Decision Time (s)',
    'Sleep_Hours_Last_Night': 'Sleep Hours Last Night',
    'Stress_Level_1_10': 'Stress Level (1-10)',
    'Error_Rate': 'Error Rate',
    'Cognitive_Load_Score': 'Cognitive Load Score',
    'Decision_Fatigue_Score': 'Decision Fatigue Score',
    'Mid_Shift_Mood_Score': 'Mid-Shift Mood Score',
    'Peer_Collaboration_Pings': 'Peer Collaboration Pings',
    'Break_Room_Entry_Count': 'Break Room Entries',
    'Hydration_Ratio': 'Hydration Ratio',
    'Fatigue_Risk_Index': 'Fatigue Risk Index',
    'Anomaly_Cohort': 'Anomaly Cohort',
}

def _label(column):
    return axis_labels.get(column, column.replace('_', ' '))

def _color_kwargs(df_plot, default_color, default_map=None, color_by=None):
    active_color = color_by if color_by in df_plot.columns else default_color
    kwargs = {'color': active_color}
    color_map = COLOR_MAPS.get(active_color, default_map if active_color == default_color else None)
    if color_map:
        kwargs['color_discrete_map'] = color_map
    else:
        kwargs['color_discrete_sequence'] = okabe_ito
    return kwargs

def _unique_columns(columns):
    return list(dict.fromkeys(columns))

def _category_orders(*columns):
    return {column: CATEGORY_ORDERS[column] for column in columns if column in CATEGORY_ORDERS}

def _prepare_ordered_categories(df_plot):
    df_plot = df_plot.copy()
    for column, order in CATEGORY_ORDERS.items():
        if column in df_plot:
            df_plot[column] = pd.Categorical(df_plot[column], categories=order, ordered=True)
    return df_plot

def _apply_theme(fig):
    fig.update_layout(
        template=global_template,
        font_family=font_family,
        margin=dict(l=34, r=24, t=42, b=32),
        title_font=dict(size=14, family=font_family, color="#2C3E50"),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        hoverlabel=dict(bgcolor="white", font_size=12, font_family=font_family),
        dragmode='zoom',
        uirevision='dashboard-view'
    )
    fig.update_layout(legend_traceorder='normal')
    # Tufte principles: minimal gridlines
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor='rgba(200,200,200,0.3)', zeroline=False)
    return fig

# ── TAB 1: WELLBEING ──────────────────────────────────────────────────────────

def create_fatigue_distribution_bar(df, color_by=None):
    df_plot = df.dropna(subset=['Time_of_Day', 'Fatigue_Level'])
    df_plot = _prepare_ordered_categories(df_plot)
    color_col = color_by if color_by in df_plot.columns else 'Fatigue_Level'
    agg = df_plot.groupby(_unique_columns(['Time_of_Day', color_col]), observed=False).size().reset_index(name='Count')
    fig = px.bar(agg, x='Time_of_Day', y='Count',
                 barmode='group',
                 **_color_kwargs(agg, 'Fatigue_Level', fatigue_colors, color_col),
                 category_orders=_category_orders('Time_of_Day', 'Fatigue_Level', color_col),
                 labels={'Time_of_Day': 'Time of Day', 'Count': 'Number of Observations'},
                 title='Fatigue Level Composition by Time of Day')
    return _apply_theme(fig)

def create_stress_fatigue_boxplot(df):
    df_plot = df.dropna(subset=['Fatigue_Level', 'Stress_Level_1_10'])
    df_plot = _prepare_ordered_categories(df_plot)
    fig = px.box(df_plot, x='Fatigue_Level', y='Stress_Level_1_10', color='Fatigue_Level',
                 color_discrete_map=fatigue_colors,
                 category_orders=_category_orders('Fatigue_Level'),
                 labels={'Stress_Level_1_10': 'Stress Level (1-10)', 'Fatigue_Level': 'Fatigue Level'},
                 title='Stress Distribution Across Fatigue Levels')
    return _apply_theme(fig)

def create_sleep_fatigue_boxplot(df):
    df_plot = df.dropna(subset=['Fatigue_Level', 'Sleep_Hours_Last_Night'])
    df_plot = _prepare_ordered_categories(df_plot)
    fig = px.box(df_plot, x='Fatigue_Level', y='Sleep_Hours_Last_Night', color='Fatigue_Level',
                 color_discrete_map=fatigue_colors,
                 category_orders=_category_orders('Fatigue_Level'),
                 labels={'Sleep_Hours_Last_Night': 'Sleep Hours Last Night', 'Fatigue_Level': 'Fatigue Level'},
                 title='Sleep Hours vs Fatigue Levels')
    return _apply_theme(fig)

def create_sleep_target_boxplot(df, color_by=None, target_col='Error_Rate'):
    target_col = target_col if target_col in df else 'Error_Rate'
    df_plot = df.dropna(subset=['Sleep_Group', target_col])
    df_plot = _prepare_ordered_categories(df_plot)
    fig = px.box(
        df_plot, x='Sleep_Group', y=target_col,
        **_color_kwargs(df_plot, 'Sleep_Group', sleep_group_colors, color_by),
        category_orders=_category_orders('Sleep_Group', color_by),
        labels={'Sleep_Group': 'Sleep Group', target_col: _label(target_col)},
        title=f'Sleep Group vs {_label(target_col)}'
    )
    return _apply_theme(fig)

def create_mood_target_scatter(df, color_by=None, target_col='Error_Rate'):
    target_col = target_col if target_col in df else 'Error_Rate'
    df_plot = df.dropna(subset=['Mid_Shift_Mood_Score', target_col, 'Time_of_Day'])
    df_plot = _prepare_ordered_categories(df_plot)
    fig = px.scatter(
        df_plot, x='Mid_Shift_Mood_Score', y=target_col,
        **_color_kwargs(df_plot, 'Time_of_Day', time_of_day_colors, color_by),
        opacity=0.55, render_mode='webgl',
        category_orders=_category_orders('Time_of_Day', color_by),
        labels={'Mid_Shift_Mood_Score': 'Mood Score', target_col: _label(target_col)},
        title=f'Mood Score vs {_label(target_col)}'
    )
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

def create_hierarchical_sunburst(df, color_by=None):
    df_plot = df.dropna(subset=['System_Recommendation', 'Fatigue_Level', 'Time_of_Day'])
    df_plot = _prepare_ordered_categories(df_plot)
    color_col = color_by if color_by in df_plot.columns else 'Fatigue_Level'
    agg = df_plot.groupby(_unique_columns(['System_Recommendation', 'Time_of_Day', color_col]), observed=False).size().reset_index(name='Count')
    
    # Use facet_row instead of facet_col to stack vertically, preventing label overlap
    fig = px.bar(
        agg, x='Count', y='Time_of_Day',
        facet_row='System_Recommendation', orientation='h',
        **_color_kwargs(agg, 'Fatigue_Level', fatigue_colors, color_col),
        category_orders=_category_orders('System_Recommendation', 'Time_of_Day', 'Fatigue_Level', color_col),
        title="Hierarchical Breakdown",
        labels={'Count': 'Interventions', 'Time_of_Day': ''},
    )

    fig = _apply_theme(fig)
    fig.update_xaxes(
        matches=None,
        showticklabels=True,
        title_text="",
        tickfont=dict(size=9),
        showgrid=True,
        gridcolor='rgba(200,200,200,0.25)',
        automargin=True,
    )
    fig.update_yaxes(
        matches=None,
        showticklabels=True,
        title_text="",
        tickfont=dict(size=10),
        automargin=True,
        categoryorder='array',
        categoryarray=CATEGORY_ORDERS['Time_of_Day'],
    )
    fig.for_each_annotation(
        lambda a: a.update(
            text=a.text.split('=')[-1],
            x=1.01,
            xanchor='left',
            font_size=10,
            font_color='#2C3E50',
        )
    )
    fig.update_layout(
        bargap=0.32,
        hovermode='y unified',
        legend_title_text=_label(color_col),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='left',
            x=0,
            font=dict(size=10),
        ),
        margin=dict(l=88, r=104, t=68, b=34),
    )
    return fig

def create_mood_shift_violin(df):
    df_plot = df.dropna(subset=['Time_of_Day', 'Mid_Shift_Mood_Score'])
    df_plot = _prepare_ordered_categories(df_plot)
    fig = px.violin(df_plot, x='Time_of_Day', y='Mid_Shift_Mood_Score', color='Time_of_Day',
                    box=True, title='Mood Score Distribution by Time of Day',
                    color_discrete_map=time_of_day_colors,
                    category_orders=_category_orders('Time_of_Day'),
                    labels={'Time_of_Day': 'Time of Day', 'Mid_Shift_Mood_Score': 'Mid-Shift Mood Score'})
    fig.update_traces(opacity=0.8)
    return _apply_theme(fig)


# ── TAB 2: RISK PROFILE ───────────────────────────────────────────────────────

def create_load_error_scatter(df, color_by=None, target_col='Error_Rate'):
    target_col = target_col if target_col in df else 'Error_Rate'
    df_plot = df.dropna(subset=['Cognitive_Load_Score', target_col, 'Fatigue_Level'])
    df_plot = _prepare_ordered_categories(df_plot)
    fig = px.scatter(df_plot, x='Cognitive_Load_Score', y=target_col,
                     **_color_kwargs(df_plot, 'Fatigue_Level', fatigue_colors, color_by),
                     opacity=0.7, render_mode='webgl',
                     category_orders=_category_orders('Fatigue_Level', color_by),
                     labels={'Cognitive_Load_Score': 'Cognitive Load Score', target_col: _label(target_col)},
                     title=f'Cognitive Load vs {_label(target_col)}')
    return _apply_theme(fig)

def create_stress_fatigue_quadrant(df, target_col='Error_Rate'):
    df_plot = df.dropna(subset=['Stress_Level_1_10', 'Error_Rate'])
    df_plot = df_plot.copy()
    df_plot['Log_Error_Rate'] = np.log10(df_plot['Error_Rate'].clip(lower=0) + 0.001)
    fig = px.density_contour(df_plot, x='Stress_Level_1_10', y='Log_Error_Rate',
                             color_discrete_sequence=['#2C3E50'],
                             labels={'Stress_Level_1_10': 'Stress Level (1-10)',
                                     'Log_Error_Rate': 'log10(Error Rate + 0.001)'},
                             title='Density Map: Stress vs log(Error Rate)')
    fig.update_traces(contours_coloring="fill", contours_showlabels=False)
    return _apply_theme(fig)

def create_sleep_fatigue_trend(df, color_by=None, target_col='Decision_Fatigue_Score'):
    target_col = target_col if target_col in df else 'Decision_Fatigue_Score'
    df_plot = df.dropna(subset=['Sleep_Group', target_col])
    df_plot = _prepare_ordered_categories(df_plot)
    color_col = color_by if color_by in df_plot.columns else 'Sleep_Group'
    agg = df_plot.groupby(_unique_columns(['Sleep_Group', color_col]), observed=False)[target_col].mean().reset_index()
    fig = px.bar(agg, x='Sleep_Group', y=target_col,
                 **_color_kwargs(agg, 'Sleep_Group', sleep_group_colors, color_col),
                 category_orders=_category_orders('Sleep_Group', color_col),
                 labels={'Sleep_Group': 'Sleep Duration Group', target_col: f'Avg {_label(target_col)}'},
                 title=f'Average {_label(target_col)} by Sleep Group')
    return _apply_theme(fig)

def create_sleep_error_trend(df, color_by=None):
    df_plot = df.dropna(subset=['Sleep_Group'])
    df_plot = _prepare_ordered_categories(df_plot)
    color_col = color_by if color_by in df_plot.columns else 'Sleep_Group'
    agg = df_plot.groupby(_unique_columns(['Sleep_Group', color_col]), observed=False).size().reset_index(name='Count')
    fig = px.bar(agg, x='Sleep_Group', y='Count',
                 **_color_kwargs(agg, 'Sleep_Group', sleep_group_colors, color_col),
                 category_orders=_category_orders('Sleep_Group', color_col),
                 labels={'Sleep_Group': 'Sleep Quality Category', 'Count': 'Number of Employees'},
                 title='Total Population by Sleep Category')
    return _apply_theme(fig)


# ── TAB 3: WORKLOAD ───────────────────────────────────────────────────────────

def create_decision_error_bubble(df, color_by=None, target_col='Error_Rate'):
    target_col = target_col if target_col in df else 'Error_Rate'
    df_plot = df.dropna(subset=['Decisions_Made', target_col, 'Hours_Awake', 'Fatigue_Level'])
    df_plot = _prepare_ordered_categories(df_plot)
    # Plotly bubble requires size > 0
    df_plot = df_plot[df_plot['Hours_Awake'] > 0]
    fig = px.scatter(df_plot, x='Decisions_Made', y=target_col,
                     size='Hours_Awake',
                     **_color_kwargs(df_plot, 'Fatigue_Level', fatigue_colors, color_by),
                     opacity=0.6, render_mode='webgl',
                     category_orders=_category_orders('Fatigue_Level', color_by),
                     labels={'Decisions_Made': 'Total Decisions Made', target_col: _label(target_col),
                             'Hours_Awake': 'Hours Awake'},
                     title=f'Decision Volume vs {_label(target_col)}')
    return _apply_theme(fig)

def create_task_error_faceted(df, color_by=None, target_col='Error_Rate'):
    target_col = target_col if target_col in df else 'Error_Rate'
    df_plot = df.dropna(subset=['Task_Switches', target_col, 'Experience_Group', 'Fatigue_Level'])
    df_plot = _prepare_ordered_categories(df_plot)
    fig = px.scatter(df_plot, x='Task_Switches', y=target_col,
                     facet_col='Experience_Group',
                     **_color_kwargs(df_plot, 'Fatigue_Level', fatigue_colors, color_by),
                     opacity=0.7, render_mode='webgl',
                     category_orders=_category_orders('Experience_Group', 'Fatigue_Level', color_by),
                     labels={'Task_Switches': 'Task Switches', target_col: _label(target_col)},
                     title=f'Task Switching vs {_label(target_col)} by Experience')
    # Fix overlapping facet labels: shorten annotation text and reduce font size
    fig.for_each_annotation(lambda a: a.update(text=a.text.split('=')[-1], font_size=11))
    fig.update_xaxes(tickangle=0)
    return _apply_theme(fig)

def create_density_fatigue_scatter(df, color_by=None, target_col='Decision_Fatigue_Score'):
    target_col = target_col if target_col in df else 'Decision_Fatigue_Score'
    df_plot = df.dropna(subset=['Time_of_Day', target_col, 'Experience_Group'])
    df_plot = _prepare_ordered_categories(df_plot)
    fig = px.box(df_plot, x='Time_of_Day', y=target_col,
                 **_color_kwargs(df_plot, 'Experience_Group', None, color_by),
                 category_orders=_category_orders('Time_of_Day', 'Experience_Group', color_by),
                 labels={'Time_of_Day': 'Time of Day', target_col: _label(target_col)},
                 title=f'{_label(target_col)} Across Shifts')
    return _apply_theme(fig)

def create_workload_parallel_coords(df, target_col='Error_Rate'):
    target_col = target_col if target_col in df else 'Error_Rate'
    cols = _unique_columns(['Hours_Awake', 'Decisions_Made', 'Task_Switches', 'Cognitive_Load_Score', target_col])
    df_plot = df.dropna(subset=cols)
    dimension_labels = {
        'Hours_Awake': 'Hours\nAwake',
        'Decisions_Made': 'Decisions\nMade',
        'Task_Switches': 'Task\nSwitches',
        'Cognitive_Load_Score': 'Cognitive\nLoad',
        target_col: _label(target_col).replace(' ', '\n')
    }
    fig = go.Figure(data=go.Parcoords(
        line=dict(
            color=df_plot[target_col],
            colorscale='Reds',
            showscale=True,
            colorbar=dict(title=_label(target_col), len=0.78, y=0.48),
        ),
        labelfont=dict(size=11, color='#2C3E50'),
        tickfont=dict(size=9, color='#34495E'),
        dimensions=[
            dict(
                label=dimension_labels.get(column, _label(column)),
                values=df_plot[column],
            )
            for column in cols
        ],
    ))
    fig.update_layout(title=f'Workload Dynamics by {_label(target_col)}')
    fig = _apply_theme(fig)
    fig.update_layout(margin=dict(l=58, r=58, t=64, b=44))
    return fig

def create_decision_density_target_scatter(df, color_by=None, target_col='Error_Rate'):
    target_col = target_col if target_col in df else 'Error_Rate'
    df_plot = df.dropna(subset=['Decision_Density', target_col])
    df_plot = _prepare_ordered_categories(df_plot)
    fig = px.scatter(
        df_plot, x='Decision_Density', y=target_col,
        **_color_kwargs(df_plot, 'Fatigue_Level', fatigue_colors, color_by),
        opacity=0.6, render_mode='webgl',
        category_orders=_category_orders('Fatigue_Level', color_by),
        labels={'Decision_Density': 'Decisions per Hour Awake', target_col: _label(target_col)},
        title=f'Decision Density vs {_label(target_col)}'
    )
    return _apply_theme(fig)


# ── TAB 4: RECOVERY ───────────────────────────────────────────────────────────

def create_caffeine_hydration_heatmap(df, target_col='Avg_Decision_Time_sec'):
    target_col = target_col if target_col in df else 'Avg_Decision_Time_sec'
    df_plot = df.dropna(subset=['Caffeine_Group', 'Hydration_Ratio', target_col])
    df_plot = _prepare_ordered_categories(df_plot)
    fig = px.density_heatmap(df_plot, x='Caffeine_Group', y='Hydration_Ratio',
                             z=target_col, histfunc='avg',
                             color_continuous_scale='Viridis',
                             category_orders=_category_orders('Caffeine_Group'),
                             labels={'Caffeine_Group': 'Caffeine Intake',
                                     'Hydration_Ratio': 'Hydration Ratio',
                                     target_col: f'Avg {_label(target_col)}'},
                             title=f'Caffeine & Hydration vs {_label(target_col)}')
    return _apply_theme(fig)

def create_gym_sleep_load_heatmap(df, target_col='Cognitive_Load_Score'):
    target_col = target_col if target_col in df else 'Cognitive_Load_Score'
    df_plot = df.dropna(subset=['Gym_Group', 'Sleep_Group', target_col])
    df_plot = _prepare_ordered_categories(df_plot)
    fig = px.density_heatmap(df_plot, x='Gym_Group', y='Sleep_Group',
                             z=target_col, histfunc='avg',
                             color_continuous_scale='Blues',
                             category_orders=_category_orders('Gym_Group', 'Sleep_Group'),
                             labels={'Gym_Group': 'Gym Activity', 'Sleep_Group': 'Sleep Group',
                                     target_col: f'Avg {_label(target_col)}'},
                             title=f'Gym Activity and Sleep vs {_label(target_col)}')
    fig = _apply_theme(fig)
    fig.update_xaxes(categoryorder='array', categoryarray=CATEGORY_ORDERS['Gym_Group'])
    fig.update_yaxes(categoryorder='array', categoryarray=CATEGORY_ORDERS['Sleep_Group'])
    return fig

def create_sleep_quality_boxplot(df, color_by=None, target_col='Mid_Shift_Mood_Score'):
    target_col = target_col if target_col in df else 'Mid_Shift_Mood_Score'
    df_plot = df.dropna(subset=['Sleep_Group', target_col])
    df_plot = _prepare_ordered_categories(df_plot)
    fig = px.box(df_plot, x='Sleep_Group', y=target_col,
                 **_color_kwargs(df_plot, 'Sleep_Group', sleep_group_colors, color_by),
                 category_orders=_category_orders('Sleep_Group', color_by),
                 labels={'Sleep_Group': 'Sleep Group', target_col: _label(target_col)},
                 title=f'Sleep Duration vs {_label(target_col)}')
    return _apply_theme(fig)

def create_experience_stress_boxplot(df, color_by=None, target_col='Stress_Level_1_10'):
    target_col = target_col if target_col in df else 'Stress_Level_1_10'
    df_plot = df.dropna(subset=['Experience_Group', target_col, 'Fatigue_Level'])
    df_plot = _prepare_ordered_categories(df_plot)
    fig = px.box(df_plot, x='Experience_Group', y=target_col,
                 **_color_kwargs(df_plot, 'Fatigue_Level', fatigue_colors, color_by),
                 category_orders=_category_orders('Experience_Group', 'Fatigue_Level', color_by),
                 labels={'Experience_Group': 'Experience Level', target_col: _label(target_col)},
                 title=f'Experience Level vs {_label(target_col)}')
    return _apply_theme(fig)


# ── TAB 5: INTERVENTION ───────────────────────────────────────────────────────

def create_perfect_storm_heatmap(df, target_col='Error_Rate'):
    target_col = target_col if target_col in df else 'Error_Rate'
    df_plot = df.dropna(subset=['Stress_Group', 'Sleep_Group', target_col])
    df_plot = _prepare_ordered_categories(df_plot)
    fig = px.density_heatmap(df_plot, x='Stress_Group', y='Sleep_Group',
                             z=target_col, histfunc='avg',
                             color_continuous_scale='Reds',
                             category_orders=_category_orders('Stress_Group', 'Sleep_Group'),
                             labels={'Stress_Group': 'Stress Level', 'Sleep_Group': 'Sleep Group',
                                     target_col: f'Avg {_label(target_col)}'},
                             title=f'Stress and Sleep vs {_label(target_col)}')
    fig = _apply_theme(fig)
    fig.update_xaxes(categoryorder='array', categoryarray=CATEGORY_ORDERS['Stress_Group'])
    fig.update_yaxes(categoryorder='array', categoryarray=CATEGORY_ORDERS['Sleep_Group'])
    return fig

def create_risk_index_scatter(df, color_by=None, target_col='Error_Rate'):
    target_col = target_col if target_col in df else 'Error_Rate'
    df_plot = df.dropna(subset=['Hydration_Ratio', 'Break_Room_Entry_Count', target_col, 'System_Recommendation'])
    df_plot = _prepare_ordered_categories(df_plot)
    fig = px.scatter(df_plot, x='Hydration_Ratio', y=target_col,
                     size='Break_Room_Entry_Count',
                     **_color_kwargs(df_plot, 'System_Recommendation', sys_rec_colors, color_by),
                     opacity=0.7, render_mode='webgl',
                     category_orders=_category_orders('System_Recommendation', color_by),
                     labels={'Hydration_Ratio': 'Hydration Ratio',
                             'Break_Room_Entry_Count': 'Break Room Entries',
                             target_col: _label(target_col)},
                     title=f'Hydration and Break Behavior vs {_label(target_col)}')
    return _apply_theme(fig)

def create_avg_risk_profile_bar(df, target_col='Fatigue_Risk_Index'):
    target_col = target_col if target_col in df else 'Fatigue_Risk_Index'
    df_plot = df.dropna(subset=['System_Recommendation', target_col])
    df_plot = _prepare_ordered_categories(df_plot)
    agg = df_plot.groupby('System_Recommendation', observed=False)[target_col].mean().reset_index()
    fig = px.bar(agg, x='System_Recommendation', y=target_col, color='System_Recommendation',
                 color_discrete_map=sys_rec_colors,
                 category_orders=_category_orders('System_Recommendation'),
                 labels={'System_Recommendation': 'System Recommendation',
                         target_col: f'Avg {_label(target_col)}'},
                 title=f'Average {_label(target_col)} by Recommendation')
    return _apply_theme(fig)

def create_intervention_streamgraph(df, color_by=None):
    df_plot = df.dropna(subset=['Time_of_Day', 'System_Recommendation', 'Decisions_Made'])
    df_plot = _prepare_ordered_categories(df_plot)
    color_col = color_by if color_by in df_plot.columns else 'System_Recommendation'
    agg = df_plot.groupby(_unique_columns(['Time_of_Day', color_col]), observed=False)['Decisions_Made'].sum().reset_index()
    fig = px.area(
        agg, x='Time_of_Day', y='Decisions_Made',
        line_group=color_col,
        **_color_kwargs(agg, 'System_Recommendation', sys_rec_colors, color_col),
        category_orders=_category_orders('Time_of_Day', 'System_Recommendation', color_col),
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
