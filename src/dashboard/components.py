import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Global Aesthetics
global_template = "plotly_white"
font_family = "Inter, sans-serif"

# Perceptually uniform and colorblind-aware palettes
fatigue_colors = {'Low': '#2ECC71', 'Medium': '#F1C40F', 'High': '#E74C3C'}
sys_rec_colors = {'Continue': '#BDC3C7', 'Slow Down': '#F39C12', 'Take Break': '#E74C3C'}
sleep_group_colors = {'Poor Sleep': '#E74C3C', 'Adequate Sleep': '#F1C40F', 'Good Sleep': '#2ECC71'}
okabe_ito = ['#E69F00', '#56B4E9', '#009E73', '#F0E442', '#0072B2', '#D55E00', '#CC79A7', '#000000']
time_of_day_colors = {'Morning': okabe_ito[0], 'Afternoon': okabe_ito[1], 'Evening': okabe_ito[2], 'Night': okabe_ito[4]}

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

# --- TAB 1 ---
def create_fatigue_distribution_bar(df):
    agg = df.groupby(['Time_of_Day', 'Fatigue_Level'], observed=False).size().reset_index(name='Count')
    # Use 100% stacked bar chart (normalized proportions)
    agg['Percentage'] = agg.groupby('Time_of_Day')['Count'].transform(lambda x: x / x.sum() * 100)
    fig = px.bar(agg, x='Time_of_Day', y='Percentage', color='Fatigue_Level',
                 category_orders={'Time_of_Day': ['Morning', 'Afternoon', 'Evening', 'Night'], 'Fatigue_Level': ['Low', 'Medium', 'High']},
                 color_discrete_map=fatigue_colors,
                 labels={'Time_of_Day': 'Time of Day', 'Percentage': 'Percentage (%)'},
                 title='Fatigue Level Composition by Time of Day')
    return _apply_theme(fig)

def create_stress_fatigue_boxplot(df):
    fig = px.box(df, x='Fatigue_Level', y='Stress_Level_1_10', color='Fatigue_Level',
                 color_discrete_map=fatigue_colors,
                 category_orders={'Fatigue_Level': ['Low', 'Medium', 'High']},
                 labels={'Stress_Level_1_10': 'Stress Level (1-10)', 'Fatigue_Level': 'Fatigue Level'},
                 title='Stress Distribution Across Fatigue Levels')
    return _apply_theme(fig)

def create_sleep_fatigue_boxplot(df):
    fig = px.box(df, x='Fatigue_Level', y='Sleep_Hours_Last_Night', color='Fatigue_Level',
                 color_discrete_map=fatigue_colors,
                 category_orders={'Fatigue_Level': ['Low', 'Medium', 'High']},
                 labels={'Sleep_Hours_Last_Night': 'Sleep Hours Last Night', 'Fatigue_Level': 'Fatigue Level'},
                 title='Sleep Hours vs Fatigue Levels')
    return _apply_theme(fig)

def create_system_rec_distribution(df):
    agg = df['System_Recommendation'].value_counts().reset_index()
    agg.columns = ['System_Recommendation', 'Count']
    fig = px.pie(agg, names='System_Recommendation', values='Count',
                 hole=0.4, title='System Recommendation Distribution',
                 color_discrete_map=sys_rec_colors)
    return _apply_theme(fig)

def create_hierarchical_sunburst(df):
    fig = px.sunburst(df, path=['System_Recommendation', 'Fatigue_Level', 'Time_of_Day'],
                      color='Fatigue_Level', color_discrete_map=fatigue_colors,
                      title="Hierarchical Breakdown of Recommendations")
    return _apply_theme(fig)

def create_mood_shift_violin(df):
    # Safely handle missing mood
    df_plot = df.dropna(subset=['Time_of_Day', 'Mid_Shift_Mood_Score'])
    fig = px.violin(df_plot, x='Time_of_Day', y='Mid_Shift_Mood_Score', color='Time_of_Day',
                    box=True, title='Mood Score Distribution by Time of Day',
                    color_discrete_map=time_of_day_colors,
                    labels={'Time_of_Day': 'Time of Day', 'Mid_Shift_Mood_Score': 'Mid-Shift Mood Score'})
    fig.update_traces(opacity=0.8)
    return _apply_theme(fig)

# --- TAB 2 ---
def create_load_error_scatter(df):
    fig = px.scatter(df, x='Cognitive_Load_Score', y='Error_Rate', color='Fatigue_Level',
                     color_discrete_map=fatigue_colors,
                     labels={'Cognitive_Load_Score': 'Cognitive Load Score', 'Error_Rate': 'Error Rate'},
                     title='Cognitive Load vs Error Rate')
    return _apply_theme(fig)

def create_stress_fatigue_quadrant(df):
    # Replaced Scatter with Density Contour Map
    fig = px.density_contour(df, x='Stress_Level_1_10', y='Decision_Fatigue_Score',
                             color_discrete_sequence=['#2C3E50'],
                             labels={'Stress_Level_1_10': 'Stress Level (1-10)', 'Decision_Fatigue_Score': 'Decision Fatigue Score'},
                             title='Density Map: Stress vs Decision Fatigue')
    fig.update_traces(contours_coloring="fill", contours_showlabels=False)
    return _apply_theme(fig)

def create_sleep_fatigue_trend(df):
    agg = df.groupby('Sleep_Group', observed=False)['Decision_Fatigue_Score'].mean().reset_index()
    fig = px.bar(agg, x='Sleep_Group', y='Decision_Fatigue_Score', color='Sleep_Group',
                 color_discrete_map=sleep_group_colors,
                 labels={'Sleep_Group': 'Sleep Duration Group', 'Decision_Fatigue_Score': 'Avg Decision Fatigue'},
                 title='Average Decision Fatigue by Sleep Group')
    return _apply_theme(fig)

def create_sleep_error_trend(df):
    # Replaced average error trend with a clear Count Plot of Sleep Groups
    agg = df['Sleep_Group'].value_counts().reset_index()
    agg.columns = ['Sleep_Group', 'Count']
    fig = px.bar(agg, x='Sleep_Group', y='Count', color='Sleep_Group',
                 color_discrete_map=sleep_group_colors,
                 labels={'Sleep_Group': 'Sleep Quality Category', 'Count': 'Number of Employees'},
                 title='Total Population by Sleep Category')
    return _apply_theme(fig)

# --- TAB 3 ---
def create_decision_error_bubble(df):
    fig = px.scatter(df, x='Decisions_Made', y='Error_Rate', size='Hours_Awake', color='Fatigue_Level',
                     color_discrete_map=fatigue_colors, opacity=0.6,
                     labels={'Decisions_Made': 'Total Decisions Made', 'Error_Rate': 'Error Rate'},
                     title='Decision Volume vs Error Rate (Bubble Size = Hours Awake)')
    return _apply_theme(fig)

def create_task_error_faceted(df):
    fig = px.scatter(df, x='Task_Switches', y='Error_Rate', facet_col='Experience_Group', color='Fatigue_Level',
                     color_discrete_map=fatigue_colors,
                     labels={'Task_Switches': 'Number of Task Switches', 'Error_Rate': 'Error Rate'},
                     title='Task Switching Impact on Errors by Experience')
    return _apply_theme(fig)

def create_density_fatigue_scatter(df):
    # Replaced Scatter with a Boxplot of Fatigue by Shift Time and Experience
    df_plot = df.dropna(subset=['Time_of_Day', 'Decision_Fatigue_Score', 'Experience_Group'])
    fig = px.box(df_plot, x='Time_of_Day', y='Decision_Fatigue_Score', color='Experience_Group',
                 color_discrete_sequence=okabe_ito,
                 labels={'Time_of_Day': 'Time of Day', 'Decision_Fatigue_Score': 'Decision Fatigue Score'},
                 title='Decision Fatigue Across Shifts by Experience Level')
    return _apply_theme(fig)

def create_workload_parallel_coords(df):
    cols = ['Hours_Awake', 'Decisions_Made', 'Task_Switches', 'Cognitive_Load_Score', 'Error_Rate']
    df_plot = df.dropna(subset=cols)
    fig = px.parallel_coordinates(df_plot, color='Error_Rate', dimensions=cols,
                                  color_continuous_scale=px.colors.sequential.Reds,
                                  title='Workload Dynamics (Parallel Coordinates)')
    fig = _apply_theme(fig)
    fig.update_layout(margin=dict(t=80, b=40, l=60, r=60)) # Prevent overlapping labels
    return fig

# --- TAB 4 ---
def create_caffeine_hydration_heatmap(df):
    agg = df.groupby(['Caffeine_Group', 'Hydration_Ratio'], observed=False)['Avg_Decision_Time_sec'].mean().reset_index()
    fig = px.density_heatmap(df, x='Caffeine_Group', y='Hydration_Ratio', z='Avg_Decision_Time_sec', histfunc='avg',
                             color_continuous_scale='Viridis',
                             labels={'Caffeine_Group': 'Caffeine Intake', 'Hydration_Ratio': 'Hydration Ratio', 'Avg_Decision_Time_sec': 'Avg Decision Time (s)'},
                             title='Caffeine & Hydration effect on Decision Time')
    return _apply_theme(fig)

def create_gym_sleep_load_heatmap(df):
    fig = px.density_heatmap(df, x='Gym_Group', y='Sleep_Group', z='Cognitive_Load_Score', histfunc='avg',
                             color_continuous_scale='Blues',
                             labels={'Gym_Group': 'Gym Activity', 'Sleep_Group': 'Sleep Group', 'Cognitive_Load_Score': 'Avg Cognitive Load'},
                             title='Gym Activity and Sleep vs Cognitive Load')
    return _apply_theme(fig)

def create_sleep_quality_boxplot(df):
    df_plot = df.dropna(subset=['Sleep_Group', 'Mid_Shift_Mood_Score'])
    fig = px.box(df_plot, x='Sleep_Group', y='Mid_Shift_Mood_Score', color='Sleep_Group',
                 color_discrete_map=sleep_group_colors,
                 labels={'Sleep_Group': 'Sleep Group', 'Mid_Shift_Mood_Score': 'Mid-Shift Mood Score'},
                 title='Sleep Duration effect on Mood')
    return _apply_theme(fig)

def create_mood_fatigue_quadrant(df):
    df_plot = df.dropna(subset=['Mid_Shift_Mood_Score', 'Decision_Fatigue_Score', 'Fatigue_Level'])
    fig = px.scatter(df_plot, x='Mid_Shift_Mood_Score', y='Decision_Fatigue_Score', color='Fatigue_Level',
                     color_discrete_map=fatigue_colors, opacity=0.7,
                     labels={'Mid_Shift_Mood_Score': 'Mid-Shift Mood Score', 'Decision_Fatigue_Score': 'Decision Fatigue Score'},
                     title='Mood vs Fatigue Quadrant')
    if not df_plot.empty:
        fig.add_hline(y=df_plot['Decision_Fatigue_Score'].median(), line_dash="dot", line_color="gray")
        fig.add_vline(x=df_plot['Mid_Shift_Mood_Score'].median(), line_dash="dot", line_color="gray")
    return _apply_theme(fig)

# --- TAB 5 ---
def create_perfect_storm_heatmap(df):
    fig = px.density_heatmap(df, x='Stress_Group', y='Sleep_Group', z='Error_Rate', histfunc='avg',
                             color_continuous_scale='Reds',
                             labels={'Stress_Group': 'Stress Level', 'Sleep_Group': 'Sleep Group', 'Error_Rate': 'Avg Error Rate'},
                             title='The "Perfect Storm" of Errors (Stress vs Sleep)')
    return _apply_theme(fig)

def create_risk_index_scatter(df):
    fig = px.scatter(df, x='Fatigue_Risk_Index', y='Error_Rate', color='System_Recommendation',
                     color_discrete_map=sys_rec_colors,
                     labels={'Fatigue_Risk_Index': 'Calculated Fatigue Risk Index', 'Error_Rate': 'Error Rate'},
                     title='Composite Risk Index vs Actual Error Rate')
    return _apply_theme(fig)

def create_avg_risk_profile_bar(df):
    agg = df.groupby('System_Recommendation', observed=False)['Fatigue_Risk_Index'].mean().reset_index()
    fig = px.bar(agg, x='System_Recommendation', y='Fatigue_Risk_Index', color='System_Recommendation',
                 color_discrete_map=sys_rec_colors,
                 labels={'System_Recommendation': 'System Recommendation', 'Fatigue_Risk_Index': 'Avg Risk Index'},
                 title='Average Risk Index by Intervention Type')
    return _apply_theme(fig)

def create_intervention_streamgraph(df):
    agg = df.groupby(['Time_of_Day', 'Fatigue_Level'], observed=False)['Error_Rate'].mean().reset_index()
    fig = px.area(
        agg, x='Time_of_Day', y='Error_Rate', color='Fatigue_Level',
        line_group='Fatigue_Level', groupnorm='percent', # Normalize to 100% proportion
        category_orders={'Time_of_Day': ['Morning', 'Afternoon', 'Evening', 'Night']},
        color_discrete_map=fatigue_colors,
        labels={'Time_of_Day': 'Time of Day', 'Error_Rate': 'Proportion of Total Avg Error Rate (%)'},
        title='Proportional Intervention Graph (Error Mix by Time)'
    )
    fig.update_traces(mode='lines', stackgroup='one', opacity=0.8)
    return _apply_theme(fig)

# --- TAB 6 ---
def create_pca_scatter(df):
    df_plot = df.dropna(subset=['PCA_1', 'PCA_2', 'Behavioural_Archetype'])
    fig = px.scatter(df_plot, x='PCA_1', y='PCA_2', color='Behavioural_Archetype',
                     opacity=0.7, title='Behavioural Archetypes (PCA Projection)',
                     color_discrete_sequence=okabe_ito,
                     labels={'PCA_1': 'Principal Component 1', 'PCA_2': 'Principal Component 2', 'Behavioural_Archetype': 'Archetype'})
    return _apply_theme(fig)

def create_pca_loadings_bar(df):
    if 'pca_loadings' in df.attrs:
        loadings = df.attrs['pca_loadings']
        fig = px.bar(loadings, x=loadings.index, y=['PC1', 'PC2'], barmode='group',
                     title='PCA Feature Loadings (What drives the variance?)',
                     labels={'index': 'Feature', 'value': 'Loading Weight', 'variable': 'Principal Component'})
        fig.update_layout(xaxis_tickangle=-45)
        return _apply_theme(fig)
    return go.Figure()

def create_cluster_profile_heatmap(df):
    cols = ['Stress_Level_1_10', 'Cognitive_Load_Score', 'Peer_Collaboration_Pings', 
            'Break_Room_Entry_Count', 'Vending_Machine_Sugar_Purchases', 'Error_Rate']
    df_plot = df.dropna(subset=['Behavioural_Archetype'] + cols)
    agg = df_plot.groupby('Behavioural_Archetype')[cols].mean()
    # Normalize for better heatmap visualization
    agg_norm = (agg - agg.min()) / (agg.max() - agg.min() + 1e-9)
    fig = px.imshow(agg_norm, text_auto=".2f", aspect="auto", color_continuous_scale='Magma',
                    title='Archetype Trait Heatmap (Normalized Means)',
                    labels={'x': 'Feature', 'y': 'Archetype'})
    return _apply_theme(fig)

def create_archetype_parallel_coords_risk(df):
    cols = ['Stress_Level_1_10', 'Cognitive_Load_Score', 'Decision_Fatigue_Score', 'Error_Rate', 'Cluster_ID']
    df_plot = df.dropna(subset=cols)
    fig = px.parallel_coordinates(df_plot, color='Cluster_ID', dimensions=cols,
                                  color_continuous_scale=px.colors.sequential.Viridis,
                                  title='Archetype Risk Profiles (Parallel Coordinates)')
    fig = _apply_theme(fig)
    fig.update_layout(margin=dict(t=80, b=40, l=60, r=60)) # Increase margins for labels
    return fig

def create_archetype_parallel_coords_behaviour(df):
    cols = ['Sleep_Hours_Last_Night', 'Peer_Collaboration_Pings', 'Mid_Shift_Mood_Score', 'Break_Room_Entry_Count', 'Cluster_ID']
    df_plot = df.dropna(subset=cols)
    fig = px.parallel_coordinates(df_plot, color='Cluster_ID', dimensions=cols,
                                  color_continuous_scale=px.colors.sequential.Plasma,
                                  title='Archetype Lifestyle Profiles (Parallel Coordinates)')
    fig = _apply_theme(fig)
    fig.update_layout(margin=dict(t=80, b=40, l=60, r=60)) # Increase margins for labels
    return fig
