import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Global Aesthetics
global_template = "plotly_white"
font_family = "Inter, sans-serif"

# Perceptually uniform and colorblind-aware palettes
fatigue_colors = {'Low': '#2ECC71', 'Medium': '#F1C40F', 'High': '#E74C3C'}
sys_rec_colors = {'Continue': '#27AE60', 'Slow Down': '#F1C40F', 'Take Break': '#E74C3C'}  # Traffic-light: green, yellow, red
wellbeing_sys_rec_colors = {
    'Continue': '#3B82C4',    # Steel blue
    'Slow Down': '#8E6BBE',   # Soft purple
    'Take Break': '#E07A2F',  # Burnt orange
}
sleep_group_colors = {'Poor Sleep': '#E74C3C', 'Adequate Sleep': '#F1C40F', 'Good Sleep': '#2ECC71'}
okabe_ito = ['#E69F00', '#56B4E9', '#009E73', '#F0E442', '#0072B2', '#D55E00', '#CC79A7', '#000000']
time_of_day_colors = {'Morning': '#FF9F1C', 'Afternoon': '#2EC4B6', 'Evening': '#7B68EE', 'Night': '#1B263B'}  # Warm sunrise / Teal / Indigo / Dark navy
red_cream_scale = ['#FFF7EC', '#FEE8C8', '#FDBB84', '#FC8D59', '#D7301F', '#7F0000']
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
    'Hydration_Group': ['Low Hydration', 'Balanced Hydration', 'High Hydration'],
    'Sugar_Group': ['No Snacks', 'Moderate Snacks', 'High Snacks'],
    'Break_Group': ['Few Breaks', 'Moderate Breaks', 'Frequent Breaks'],
    'Behavioural_Archetype': ['Collaborative / Balanced', 'Low Engagement', 'Stressed / Isolated'],
    'Anomaly_Cohort': [
        'Expected trend',
        'Routine stable pocket',
        'Night peer-support buffer',
        'Veteran stress resilience',
        'Active high-density resilience',
        'Recovery pacing pocket',
        'Masked continue risk',
        'Overload failure pocket',
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

def _metric_label(column):
    if column == 'Error_Rate':
        return 'Error Rate (%)'
    if column == 'Avg_Decision_Time_sec':
        return 'Decision Time (s)'
    return _label(column)

def _metric_frame(df_plot, column):
    display_col = column
    if column == 'Error_Rate':
        display_col = 'Error_Rate_pct'
        df_plot = df_plot.copy()
        df_plot[display_col] = df_plot[column] * 100
    return df_plot, display_col, _metric_label(column)

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

def _set_average_colorbar(fig, label):
    fig.update_coloraxes(colorbar_title_text=f'Average {label}')
    return fig

# ΓöÇΓöÇ TAB 1: WELLBEING ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ

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
                 title='Timing: Fatigue Level by Time of Day')
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
                 title='Recovery: Sleep Hours by Fatigue Level')
    return _apply_theme(fig)


def create_wellbeing_system_rec_stacked_bar(df):
    """Stacked bar: how system recommendations shift across the day."""
    df_plot = df.dropna(subset=['Time_of_Day', 'System_Recommendation'])
    df_plot = _prepare_ordered_categories(df_plot)
    agg = df_plot.groupby(['Time_of_Day', 'System_Recommendation'], observed=False).size().reset_index(name='Count')
    fig = px.bar(
        agg, x='Time_of_Day', y='Count', color='System_Recommendation',
        barmode='stack',
        color_discrete_map=wellbeing_sys_rec_colors,
        category_orders=_category_orders('Time_of_Day', 'System_Recommendation'),
        labels={'Time_of_Day': 'Time of Day', 'Count': 'Observations', 'System_Recommendation': 'Recommendation'},
        title='Response: System Recommendations Across the Shift',
    )
    fig.update_layout(legend_title_text='Recommendation')
    return _apply_theme(fig)


def create_wellbeing_stress_sleep_heatmap(df):
    """Heatmap: average decision fatigue where stress and sleep intersect."""
    df_plot = df.dropna(subset=['Stress_Group', 'Sleep_Group', 'Decision_Fatigue_Score'])
    df_plot = _prepare_ordered_categories(df_plot)
    fig = px.density_heatmap(
        df_plot, x='Stress_Group', y='Sleep_Group',
        z='Decision_Fatigue_Score', histfunc='avg',
        color_continuous_scale='YlOrRd',
        category_orders=_category_orders('Stress_Group', 'Sleep_Group'),
        labels={
            'Stress_Group': 'Stress Level',
            'Sleep_Group': 'Sleep Group',
            'Decision_Fatigue_Score': 'Decision Fatigue Score',
        },
        title='Risk Zones: Decision Fatigue by Stress and Sleep',
    )
    return _set_average_colorbar(_apply_theme(fig), 'Decision Fatigue Score')


def create_sleep_target_boxplot(df, color_by=None, target_col='Error_Rate'):
    target_col = target_col if target_col in df else 'Error_Rate'
    df_plot = df.dropna(subset=['Sleep_Group', target_col])
    df_plot, display_col, display_label = _metric_frame(df_plot, target_col)
    df_plot = _prepare_ordered_categories(df_plot)
    fig = px.box(
        df_plot, x='Sleep_Group', y=display_col,
        **_color_kwargs(df_plot, 'Sleep_Group', sleep_group_colors, color_by),
        category_orders=_category_orders('Sleep_Group', color_by),
        labels={'Sleep_Group': 'Sleep Group', display_col: display_label},
        title=f'Sleep Group vs {display_label}'
    )
    return _apply_theme(fig)

def create_mood_target_scatter(df, color_by=None, target_col='Error_Rate'):
    target_col = target_col if target_col in df else 'Error_Rate'
    df_plot = df.dropna(subset=['Mid_Shift_Mood_Score', target_col, 'Time_of_Day'])
    df_plot, display_col, display_label = _metric_frame(df_plot, target_col)
    df_plot = _prepare_ordered_categories(df_plot)
    fig = px.scatter(
        df_plot, x='Mid_Shift_Mood_Score', y=display_col,
        **_color_kwargs(df_plot, 'Time_of_Day', time_of_day_colors, color_by),
        opacity=0.55, render_mode='webgl',
        category_orders=_category_orders('Time_of_Day', color_by),
        labels={'Mid_Shift_Mood_Score': 'Mood Score', display_col: display_label},
        title=f'Mood Score vs {display_label}'
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


# ΓöÇΓöÇ TAB 2: RISK PROFILE ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ

def create_load_error_scatter(df, color_by=None, target_col='Error_Rate'):
    target_col = target_col if target_col in df else 'Error_Rate'
    df_plot = df.dropna(subset=['Cognitive_Load_Score', target_col, 'Fatigue_Level'])
    df_plot, display_col, display_label = _metric_frame(df_plot, target_col)
    df_plot = _prepare_ordered_categories(df_plot)
    fig = px.scatter(df_plot, x='Cognitive_Load_Score', y=display_col,
                     **_color_kwargs(df_plot, 'Fatigue_Level', fatigue_colors, color_by),
                     opacity=0.7, render_mode='webgl',
                     category_orders=_category_orders('Fatigue_Level', color_by),
                     labels={'Cognitive_Load_Score': 'Cognitive Load Score', display_col: display_label},
                     title=f'Cognitive Load vs {display_label}')
    return _apply_theme(fig)

def create_stress_fatigue_quadrant(df, target_col='Error_Rate', axis_ranges=None):
    df_plot = df.dropna(subset=['Decision_Density', 'Cognitive_Load_Score'])
    df_plot = df_plot.copy()
    fig = px.density_contour(df_plot, x='Decision_Density', y='Cognitive_Load_Score',
                             color_discrete_sequence=['#2C3E50'],
                             labels={'Decision_Density': 'Decisions per Hour Awake',
                                     'Cognitive_Load_Score': 'Cognitive Load Score'},
                             title='Density Map: Decision Density vs Cognitive Load')
    fig.update_traces(contours_coloring="fill", contours_showlabels=False)
    fig = _apply_theme(fig)
    if axis_ranges:
        x_range, y_range = axis_ranges
        if x_range:
            fig.update_xaxes(range=list(x_range))
        if y_range:
            fig.update_yaxes(range=list(y_range))
    return fig

def create_sleep_fatigue_trend(df, color_by=None, target_col='Decision_Fatigue_Score'):
    target_col = target_col if target_col in df else 'Decision_Fatigue_Score'
    df_plot = df.dropna(subset=['Sleep_Group', target_col])
    df_plot, display_col, display_label = _metric_frame(df_plot, target_col)
    df_plot = _prepare_ordered_categories(df_plot)
    color_col = color_by if color_by in df_plot.columns else 'Sleep_Group'
    agg = df_plot.groupby(_unique_columns(['Sleep_Group', color_col]), observed=False)[display_col].mean().reset_index()
    fig = px.bar(agg, x='Sleep_Group', y=display_col,
                 **_color_kwargs(agg, 'Sleep_Group', sleep_group_colors, color_col),
                 category_orders=_category_orders('Sleep_Group', color_col),
                 labels={'Sleep_Group': 'Sleep Duration Group', display_col: display_label},
                 title=f'Average {display_label} by Sleep Group')
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


# ΓöÇΓöÇ TAB 3: WORKLOAD ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ

def create_decision_error_bubble(df, color_by=None, target_col='Error_Rate'):
    target_col = target_col if target_col in df else 'Error_Rate'
    df_plot = df.dropna(subset=['Decisions_Made', target_col, 'Hours_Awake', 'Fatigue_Level'])
    df_plot, display_col, display_label = _metric_frame(df_plot, target_col)
    df_plot = _prepare_ordered_categories(df_plot)
    # Plotly bubble requires size > 0
    df_plot = df_plot[df_plot['Hours_Awake'] > 0]
    fig = px.scatter(df_plot, x='Decisions_Made', y=display_col,
                     size='Hours_Awake',
                     **_color_kwargs(df_plot, 'Fatigue_Level', fatigue_colors, color_by),
                     opacity=0.6, render_mode='webgl',
                     category_orders=_category_orders('Fatigue_Level', color_by),
                     labels={'Decisions_Made': 'Total Decisions Made', display_col: display_label,
                             'Hours_Awake': 'Hours Awake'},
                     title=f'Decision Volume vs {display_label}')
    return _apply_theme(fig)

def create_task_error_faceted(df, color_by=None, target_col='Error_Rate'):
    target_col = target_col if target_col in df else 'Error_Rate'
    df_plot = df.dropna(subset=['Task_Switches', target_col, 'Experience_Group', 'Fatigue_Level'])
    df_plot, display_col, display_label = _metric_frame(df_plot, target_col)
    df_plot = _prepare_ordered_categories(df_plot)
    fig = px.scatter(df_plot, x='Task_Switches', y=display_col,
                     facet_col='Experience_Group',
                     **_color_kwargs(df_plot, 'Fatigue_Level', fatigue_colors, color_by),
                     opacity=0.7, render_mode='webgl',
                     category_orders=_category_orders('Experience_Group', 'Fatigue_Level', color_by),
                     labels={'Task_Switches': 'Task Switches', display_col: display_label},
                     title=f'Task Switching vs {display_label} by Experience')
    # Fix overlapping facet labels: shorten annotation text and reduce font size
    fig.for_each_annotation(lambda a: a.update(text=a.text.split('=')[-1], font_size=11))
    fig.update_xaxes(tickangle=0)
    return _apply_theme(fig)

def create_density_fatigue_scatter(df, color_by=None, target_col='Decision_Fatigue_Score'):
    target_col = target_col if target_col in df else 'Decision_Fatigue_Score'
    df_plot = df.dropna(subset=['Time_of_Day', target_col, 'Experience_Group'])
    df_plot, display_col, display_label = _metric_frame(df_plot, target_col)
    df_plot = _prepare_ordered_categories(df_plot)
    fig = px.box(df_plot, x='Time_of_Day', y=display_col,
                 **_color_kwargs(df_plot, 'Experience_Group', None, color_by),
                 category_orders=_category_orders('Time_of_Day', 'Experience_Group', color_by),
                 labels={'Time_of_Day': 'Time of Day', display_col: display_label},
                 title=f'{display_label} Across Shifts')
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
    df_plot, display_col, display_label = _metric_frame(df_plot, target_col)
    df_plot = _prepare_ordered_categories(df_plot)
    fig = px.scatter(
        df_plot, x='Decision_Density', y=display_col,
        **_color_kwargs(df_plot, 'Fatigue_Level', fatigue_colors, color_by),
        opacity=0.6, render_mode='webgl',
        category_orders=_category_orders('Fatigue_Level', color_by),
        labels={'Decision_Density': 'Decisions per Hour Awake', display_col: display_label},
        title=f'Decision Density vs {display_label}'
    )
    return _apply_theme(fig)


# ΓöÇΓöÇ TAB 4: RECOVERY ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ

def create_caffeine_hydration_heatmap(df, target_col='Avg_Decision_Time_sec'):
    target_col = target_col if target_col in df else 'Avg_Decision_Time_sec'
    df_plot = df.dropna(subset=['Caffeine_Group', 'Hydration_Ratio', target_col])
    df_plot, display_col, display_label = _metric_frame(df_plot, target_col)
    df_plot = _prepare_ordered_categories(df_plot)
    fig = px.density_heatmap(df_plot, x='Caffeine_Group', y='Hydration_Ratio',
                             z=display_col, histfunc='avg',
                             color_continuous_scale='Viridis',
                             category_orders=_category_orders('Caffeine_Group'),
                             labels={'Caffeine_Group': 'Caffeine Intake',
                                     'Hydration_Ratio': 'Hydration Ratio',
                                     display_col: display_label},
                             title=f'Caffeine & Hydration vs {display_label}')
    return _set_average_colorbar(_apply_theme(fig), display_label)

def create_gym_sleep_load_heatmap(df, target_col='Cognitive_Load_Score'):
    target_col = target_col if target_col in df else 'Cognitive_Load_Score'
    df_plot = df.dropna(subset=['Gym_Group', 'Sleep_Group', target_col])
    df_plot, display_col, display_label = _metric_frame(df_plot, target_col)
    df_plot = _prepare_ordered_categories(df_plot)
    agg = df_plot.groupby(['Sleep_Group', 'Gym_Group'], observed=False)[display_col].mean().reset_index()
    pivot = (
        agg.pivot(index='Sleep_Group', columns='Gym_Group', values=display_col)
        .reindex(index=CATEGORY_ORDERS['Sleep_Group'], columns=CATEGORY_ORDERS['Gym_Group'])
    )
    finite_values = pivot.to_numpy(dtype=float)
    finite_values = finite_values[~np.isnan(finite_values)]
    zmin, zmax = None, None
    if len(finite_values):
        zmin = float(np.percentile(finite_values, 5))
        zmax = float(np.percentile(finite_values, 95))
        if zmin == zmax:
            zmin, zmax = float(finite_values.min()), float(finite_values.max())

    fig = go.Figure(data=go.Heatmap(
        x=list(pivot.columns),
        y=list(pivot.index),
        z=pivot.to_numpy(),
        zmin=zmin,
        zmax=zmax,
        colorscale=[
            [0.0, "#F7FBFF"],
            [0.18, "#C7D2FE"],
            [0.38, "#60A5FA"],
            [0.62, "#2563EB"],
            [0.82, "#7C3AED"],
            [1.0, "#3B0764"],
        ],
        colorbar=dict(title=f"Average {display_label}"),
        hovertemplate="Gym Activity: %{x}<br>Sleep Group: %{y}<br>Average " + display_label + ": %{z:.2f}<extra></extra>",
    ))
    fig.update_layout(title=f'Gym Activity and Sleep vs {display_label}')
    fig = _apply_theme(fig)
    fig.update_xaxes(title_text='Gym Activity', categoryorder='array', categoryarray=CATEGORY_ORDERS['Gym_Group'])
    fig.update_yaxes(title_text='Sleep Group', categoryorder='array', categoryarray=CATEGORY_ORDERS['Sleep_Group'])
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
    return _set_average_colorbar(_apply_theme(fig), display_label)

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


# ΓöÇΓöÇ TAB 5: INTERVENTION ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ

def create_perfect_storm_heatmap(df, target_col='Error_Rate'):
    target_col = target_col if target_col in df else 'Error_Rate'
    df_plot = df.dropna(subset=['Caffeine_Group', 'Hydration_Group', target_col])
    df_plot, display_col, display_label = _metric_frame(df_plot, target_col)
    df_plot = _prepare_ordered_categories(df_plot)
    fig = px.density_heatmap(df_plot, x='Caffeine_Group', y='Hydration_Group',
                             z=display_col, histfunc='avg',
                             color_continuous_scale=red_cream_scale,
                             category_orders=_category_orders('Caffeine_Group', 'Hydration_Group'),
                             labels={'Caffeine_Group': 'Caffeine Intake',
                                     'Hydration_Group': 'Hydration Balance',
                                     display_col: display_label},
                             title=f'Caffeine and Hydration vs {display_label}')
    fig = _apply_theme(fig)
    _set_average_colorbar(fig, display_label)
    fig.update_xaxes(categoryorder='array', categoryarray=CATEGORY_ORDERS['Caffeine_Group'])
    fig.update_yaxes(categoryorder='array', categoryarray=CATEGORY_ORDERS['Hydration_Group'])
    return fig

def create_risk_index_scatter(df, color_by=None, target_col='Error_Rate'):
    target_col = target_col if target_col in df else 'Error_Rate'
    df_plot = df.dropna(subset=['Break_Group', target_col, 'System_Recommendation'])
    df_plot, display_col, display_label = _metric_frame(df_plot, target_col)
    df_plot = _prepare_ordered_categories(df_plot)
    fig = px.box(df_plot, x='Break_Group', y=display_col, color='System_Recommendation',
                 color_discrete_map=sys_rec_colors,
                 category_orders=_category_orders('Break_Group', 'System_Recommendation'),
                 labels={'Break_Group': 'Break Frequency',
                         'System_Recommendation': 'System Recommendation',
                         display_col: display_label},
                 title=f'Break Recovery by Recommendation vs {display_label}')
    return _apply_theme(fig)

def create_avg_risk_profile_bar(df, target_col='Error_Rate'):
    target_col = target_col if target_col in df else 'Error_Rate'
    df_plot = df.dropna(subset=['Caffeine_Group', 'Sugar_Group', target_col])
    df_plot, display_col, display_label = _metric_frame(df_plot, target_col)
    df_plot = _prepare_ordered_categories(df_plot)
    fig = px.density_heatmap(df_plot, x='Caffeine_Group', y='Sugar_Group',
                 z=display_col, histfunc='avg',
                 color_continuous_scale=red_cream_scale,
                 category_orders=_category_orders('Caffeine_Group', 'Sugar_Group'),
                 labels={'Caffeine_Group': 'Caffeine Intake',
                         'Sugar_Group': 'Snack Reliance',
                         display_col: display_label},
                 title=f'Caffeine and Snacks vs {display_label}')
    fig = _apply_theme(fig)
    _set_average_colorbar(fig, display_label)
    fig.update_xaxes(categoryorder='array', categoryarray=CATEGORY_ORDERS['Caffeine_Group'])
    fig.update_yaxes(categoryorder='array', categoryarray=CATEGORY_ORDERS['Sugar_Group'])
    return fig

def create_intervention_streamgraph(df, color_by=None, target_col='Error_Rate'):
    target_col = target_col if target_col in df else 'Error_Rate'
    df_plot = df.dropna(subset=['Gym_Group', 'Sleep_Group', target_col])
    df_plot, display_col, display_label = _metric_frame(df_plot, target_col)
    df_plot = _prepare_ordered_categories(df_plot)
    agg = df_plot.groupby(['Gym_Group', 'Sleep_Group'], observed=False)[display_col].mean().reset_index()
    fig = px.line(
        agg, x='Gym_Group', y=display_col, color='Sleep_Group',
        markers=True,
        custom_data=['Sleep_Group'],
        color_discrete_map=sleep_group_colors,
        category_orders=_category_orders('Gym_Group', 'Sleep_Group'),
        labels={'Gym_Group': 'Gym Activity',
                'Sleep_Group': 'Sleep Group',
                display_col: display_label},
        title=f'Physical Recovery and Sleep vs {display_label}'
    )
    fig.update_xaxes(categoryorder='array', categoryarray=CATEGORY_ORDERS['Gym_Group'])
    return _apply_theme(fig)


# ΓöÇΓöÇ TAB 6: ARCHETYPES ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ

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
    # Logical flow: Stress ΓåÆ Cog Load ΓåÆ Fatigue ΓåÆ Error (cause ΓåÆ effect sequence)
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
                                  title='Archetype Risk Profiles (Stress to Load to Fatigue to Error)')
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
    # Logical flow: Sleep ΓåÆ Mood ΓåÆ Social Engagement ΓåÆ Breaks (recovery ΓåÆ output sequence)
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
                                  title='Archetype Lifestyle (Sleep to Mood to Collaboration to Breaks)')
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


# -- WORKLOAD + CONFOUNDING -- Memo brushing island --

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


def create_brushable_pcp(df, selection=None, sample_size=2500):
    """Brushable PCP. Persists constraintranges from the selection store."""
    try:
        from .theme import apply_theme, FATIGUE_COLORS as fatigue_colors
    except ImportError:
        from theme import apply_theme, FATIGUE_COLORS as fatigue_colors
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
    try:
        from .theme import get_color_map, get_category_order, apply_theme, OKABE_ITO
        from .selection import compute_mask, has_selection
    except ImportError:
        from theme import get_color_map, get_category_order, apply_theme, OKABE_ITO
        from selection import compute_mask, has_selection

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
    try:
        from .theme import SELECTION_COLORS, NEUTRAL, apply_theme
        from .selection import compute_mask, has_selection
    except ImportError:
        from theme import SELECTION_COLORS, NEUTRAL, apply_theme
        from selection import compute_mask, has_selection

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
