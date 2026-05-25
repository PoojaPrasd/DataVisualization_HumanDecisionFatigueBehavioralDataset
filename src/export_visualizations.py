import os
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

# Configure premium, Tufte-maximizing Cool Slate-Blue light theme globally
# This removes heavy dark backdrops and redundant visual noise, achieving a high Data-Ink Ratio.
pio.templates["premium_tufte"] = go.layout.Template(
    layout=go.Layout(
        paper_bgcolor='#F4F6FA',  # Warm off-white / Cool slate-blue canvas
        plot_bgcolor='#F4F6FA',
        font=dict(color='#2B3A42', family="Inter, Roboto, Helvetica, Arial, sans-serif"),
        title=dict(font=dict(size=16, color='#2B3A42', weight='bold')),
        legend=dict(
            bgcolor='rgba(0,0,0,0)',      # Floating transparent background
            bordercolor='rgba(0,0,0,0)',  # Strip borders to maximize data-ink
            borderwidth=0
        ),
        xaxis=dict(
            showline=False,               # Remove spine borders
            gridcolor='#E1E6EB',          # Desaturated soft gridlines
            zeroline=False,
            tickfont=dict(color='#4F5B66')
        ),
        yaxis=dict(
            showline=False,               # Remove spine borders
            gridcolor='#E1E6EB',          # Desaturated soft gridlines
            zeroline=False,
            tickfont=dict(color='#4F5B66')
        ),
        scene=dict(
            xaxis=dict(backgroundcolor='#F4F6FA', gridcolor='#E1E6EB', showbackground=True),
            yaxis=dict(backgroundcolor='#F4F6FA', gridcolor='#E1E6EB', showbackground=True),
            zaxis=dict(backgroundcolor='#F4F6FA', gridcolor='#E1E6EB', showbackground=True)
        )
    )
)
pio.templates.default = "plotly_white+premium_tufte"

# Define output directories
OUTPUT_DIR = "exports"
HTML_DIR = os.path.join(OUTPUT_DIR, "html")
PNG_DIR = os.path.join(OUTPUT_DIR, "png")

# Define premium color mappings
PALETTE_RECOMMENDATION = {"Continue": "#2ec4b6", "Slow Down": "#ff9f1c", "Take Break": "#e71d36"}

def ensure_directories():
    os.makedirs(HTML_DIR, exist_ok=True)
    os.makedirs(PNG_DIR, exist_ok=True)
    print("Export directories verified:")
    print(f"  - Interactive HTML: {os.path.abspath(HTML_DIR)}")
    print(f"  - Static PNG Images: {os.path.abspath(PNG_DIR)}")

def load_and_preprocess_data():
    csv_path = os.path.join("data", "human_decision_fatigue_dataset.csv")
    if not os.path.exists(csv_path):
        csv_path = os.path.join("..", "data", "human_decision_fatigue_dataset.csv")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset not found at either data/ or ../data/ path. Please verify the path.")
    
    df = pd.read_csv(csv_path)
    print(f"Dataset loaded successfully. Dimensions: {df.shape[0]} rows, {df.shape[1]} columns.")
    
    # Configure logical category sorting
    df['Time_of_Day'] = pd.Categorical(df['Time_of_Day'], categories=['Morning', 'Afternoon', 'Evening', 'Night'], ordered=True)
    df['Fatigue_Level'] = pd.Categorical(df['Fatigue_Level'], categories=['Low', 'Moderate', 'High'], ordered=True)
    df['System_Recommendation'] = pd.Categorical(df['System_Recommendation'], categories=['Continue', 'Slow Down', 'Take Break'], ordered=True)
    
    # Create sleep duration bins
    def sleep_bin(h):
        if h < 6: return 'Short Sleep (<6h)'
        elif h <= 8: return 'Standard Sleep (6-8h)'
        else: return 'Optimal Sleep (>8h)'

    df['Sleep_Group'] = df['Sleep_Hours_Last_Night'].apply(sleep_bin)
    df['Sleep_Group'] = pd.Categorical(df['Sleep_Group'], categories=['Short Sleep (<6h)', 'Standard Sleep (6-8h)', 'Optimal Sleep (>8h)'], ordered=True)

    return df

def export_plot(fig, filename_base):
    # 1. Export as interactive standalone HTML page
    html_path = os.path.join(HTML_DIR, f"{filename_base}.html")
    fig.write_html(html_path, include_plotlyjs="cdn")
    print(f"  [HTML Saved] {os.path.basename(html_path)}")
    
    # 2. Export as static high-res PNG image
    png_path = os.path.join(PNG_DIR, f"{filename_base}.png")
    try:
        # Save as high-res PNG
        fig.write_image(png_path, width=1200, height=800, scale=2)
        print(f"  [PNG Saved]  {os.path.basename(png_path)}")
    except Exception as e:
        print(f"  [PNG Skip]   Could not export static PNG image (kaleido engine details: {e})")

def main():
    ensure_directories()
    df = load_and_preprocess_data()
    
    # Pre-draw samples for performance-critical high-dimensional rendering
    sample_df = df.sample(1500, random_state=42)
    sample_sat = df.sample(2000, random_state=42)
    
    print("\nBeginning visualization renders and exports...")

    # =========================================================================
    # Plot A: Bivariate Workload Heatmap
    # =========================================================================
    print("\n[1/12] Rendering: Plot A (workload_threshold_heatmap)...")
    pivot_workload = df.groupby([
        pd.cut(df['Decisions_Made'], bins=15),
        pd.cut(df['Task_Switches'], bins=15)
    ], observed=False)['Cognitive_Load_Score'].mean().unstack().fillna(0)
    pivot_workload.index = [f"{int(i.left)}-{int(i.right)}" for i in pivot_workload.index]
    pivot_workload.columns = [f"{int(c.left)}-{int(c.right)}" for c in pivot_workload.columns]
    
    fig_a = px.imshow(
        pivot_workload,
        labels=dict(x="Number of Task Switches", y="Decisions Made", color="Avg Cognitive Load"),
        title="<b>Plot A: Bivariate Workload Grid vs. Average Cognitive Load</b>",
        color_continuous_scale="Viridis"
    )
    fig_a.update_layout(title_font_size=18, margin=dict(l=40, r=40, t=60, b=40))
    export_plot(fig_a, "plot_a_workload_threshold_heatmap")

    # =========================================================================
    # Plot B: Sleep vs. Stress Box Plots
    # =========================================================================
    print("\n[2/12] Rendering: Plot B (sleep_vs_stress_box)...")
    fig_b = px.box(
        df,
        x='Sleep_Group',
        y='Stress_Level_1_10',
        color='Sleep_Group',
        color_discrete_sequence=['#e71d36', '#ff9f1c', '#2ec4b6'],
        labels={
            'Sleep_Group': 'Sleep Duration Class',
            'Stress_Level_1_10': 'Stress Level (1-10)'
        },
        title="<b>Plot B: Stress Level Distribution by Sleep Quality Group</b>"
    )
    fig_b.update_layout(title_font_size=18, margin=dict(l=40, r=40, t=60, b=40))
    export_plot(fig_b, "plot_b_sleep_vs_stress_box")

    # =========================================================================
    # Plot C: The Fatigue-Performance Curve (Dual Y-Axis)
    # =========================================================================
    print("\n[3/12] Rendering: Plot C (fatigue_performance_curve)...")
    grouped_awake = df.groupby('Hours_Awake')[['Error_Rate', 'Decision_Fatigue_Score']].mean().reset_index()
    fig_c = go.Figure()
    fig_c.add_trace(go.Scatter(
        x=grouped_awake['Hours_Awake'],
        y=grouped_awake['Decision_Fatigue_Score'],
        name='Decision Fatigue Score (Left)',
        line=dict(color='#ff9f1c', width=4),
        mode='lines+markers'
    ))
    fig_c.add_trace(go.Scatter(
        x=grouped_awake['Hours_Awake'],
        y=grouped_awake['Error_Rate'] * 100,
        name='Error Rate % (Right)',
        line=dict(color='#e71d36', width=4, dash='dash'),
        mode='lines+markers',
        yaxis='y2'
    ))
    fig_c.update_layout(
        title='<b>Plot C: The Cognitive Wall: Hours Awake vs. Fatigue & Error Rate</b>',
        title_font_size=18,
        xaxis=dict(title='Hours Awake', dtick=1),
        yaxis=dict(title='Decision Fatigue Score (0-100)', title_font=dict(color='#ff9f1c'), tickfont=dict(color='#ff9f1c')),
        yaxis2=dict(title='Error Rate (%)', title_font=dict(color='#e71d36'), tickfont=dict(color='#e71d36'), overlaying='y', side='right'),
        legend=dict(x=0.05, y=0.95),
        margin=dict(l=40, r=40, t=60, b=40),
        shapes=[
            dict(type="rect", xref="x", yref="paper", x0=7, x1=10, y0=0, y1=1, fillcolor="rgba(46, 196, 182, 0.15)", layer="below", line_width=0),
            dict(type="rect", xref="x", yref="paper", x0=10, x1=13, y0=0, y1=1, fillcolor="rgba(255, 159, 28, 0.15)", layer="below", line_width=0),
            dict(type="rect", xref="x", yref="paper", x0=13, x1=17, y0=0, y1=1, fillcolor="rgba(231, 29, 54, 0.25)", layer="below", line_width=0)
        ]
    )
    fig_c.add_annotation(x=8.5, y=50, text="<b>SAFETY ZONE</b>", showarrow=False, font=dict(color="#2ec4b6", size=10))
    fig_c.add_annotation(x=11.5, y=65, text="<b>WARNING ZONE</b>", showarrow=False, font=dict(color="#ff9f1c", size=10))
    fig_c.add_annotation(x=15, y=85, text="<b>DANGER ZONE</b>", showarrow=False, font=dict(color="#e71d36", size=10))
    export_plot(fig_c, "plot_c_fatigue_performance_curve")

    # =========================================================================
    # Plot D: Caffeine vs. Awake Heatmap
    # =========================================================================
    print("\n[4/12] Rendering: Plot D (caffeine_vs_awake_heatmap)...")
    pivot_caffeine = df.groupby(['Hours_Awake', 'Caffeine_Intake_Cups'], observed=False)['Decision_Fatigue_Score'].mean().unstack().fillna(0)
    fig_d = px.imshow(
        pivot_caffeine,
        labels=dict(x="Caffeine Intake (Cups)", y="Hours Awake", color="Avg Fatigue Score"),
        title="<b>Plot D: Caffeine Intake & Hours Awake vs. Perceived Decision Fatigue</b>",
        color_continuous_scale="Portland"
    )
    fig_d.update_layout(title_font_size=18, margin=dict(l=40, r=40, t=60, b=40))
    export_plot(fig_d, "plot_d_caffeine_vs_awake_heatmap")

    # =========================================================================
    # Plot E: Recommendation Boundary (2D Bubble Chart)
    # =========================================================================
    print("\n[5/12] Rendering: Plot E (recommendation_boundaries)...")
    fig_e = px.scatter(
        sample_df,
        x='Cognitive_Load_Score',
        y='Decision_Fatigue_Score',
        color='System_Recommendation',
        size='Error_Rate',
        color_discrete_map=PALETTE_RECOMMENDATION,
        size_max=12,
        labels={
            'Cognitive_Load_Score': 'Cognitive Load Score',
            'Decision_Fatigue_Score': 'Decision Fatigue Score',
            'Error_Rate': 'Error Rate',
            'System_Recommendation': 'System Action'
        },
        title='<b>Plot E: Recommendation Decision Space & Action Boundaries (2D Bubble Chart)</b>',
        opacity=0.65
    )
    fig_e.update_layout(title_font_size=18, margin=dict(l=40, r=40, t=60, b=40))
    export_plot(fig_e, "plot_e_recommendation_boundaries")

    # =========================================================================
    # Plot F: The Perfect Storm Catastrophe Zone (Faceted 2D Scatter)
    # =========================================================================
    print("\n[6/12] Rendering: Plot F (perfect_storm_catastrophe)...")
    fig_f = px.scatter(
        sample_df,
        x='Hours_Awake',
        y='Error_Rate',
        facet_col='Sleep_Group',
        color='Stress_Level_1_10',
        size='Cognitive_Load_Score',
        color_continuous_scale='Hot',
        size_max=12,
        labels={
            'Hours_Awake': 'Hours Awake',
            'Error_Rate': 'Error Rate',
            'Sleep_Group': 'Sleep Duration Class',
            'Stress_Level_1_10': 'Stress level (1-10)',
            'Cognitive_Load_Score': 'Cognitive Load'
        },
        title='<b>Plot F: The "Perfect Storm" Catastrophe Zone: Sleep Buffering Stress & Fatigue</b>',
        opacity=0.75
    )
    fig_f.update_layout(title_font_size=18, yaxis=dict(tickformat='.0%'), margin=dict(l=40, r=40, t=60, b=40))
    export_plot(fig_f, "plot_f_perfect_storm_catastrophe")

    # =========================================================================
    # Plot G: Multitasking Efficiency Decay (2D Bubble Decay)
    # =========================================================================
    print("\n[7/12] Rendering: Plot G (multitasking_efficiency_decay)...")
    fig_g = px.scatter(
        sample_df,
        x='Task_Switches',
        y='Avg_Decision_Time_sec',
        color='Cognitive_Load_Score',
        size='Decisions_Made',
        color_continuous_scale='Bluered',
        size_max=12,
        labels={
            'Decisions_Made': 'Decisions Made',
            'Avg_Decision_Time_sec': 'Average Decision Time (s)',
            'Task_Switches': 'Task Switches',
            'Cognitive_Load_Score': 'Cognitive Load'
        },
        title='<b>Plot G: Multitasking Efficiency Decay: Speed sluggishness vs. Switching Friction</b>',
        opacity=0.7
    )
    fig_g.update_layout(title_font_size=18, margin=dict(l=40, r=40, t=60, b=40))
    export_plot(fig_g, "plot_g_multitasking_efficiency_decay")

    # =========================================================================
    # Plot H: Speed-Accuracy Trade-off Collapse (Faceted)
    # =========================================================================
    print("\n[8/12] Rendering: Plot H (sat_tradeoff_collapse)...")
    fig_h = px.scatter(
        sample_sat,
        x='Avg_Decision_Time_sec',
        y='Error_Rate',
        facet_col='Fatigue_Level',
        color='Stress_Level_1_10',
        color_continuous_scale='Viridis',
        labels={
            'Avg_Decision_Time_sec': 'Avg Decision Time (s)',
            'Error_Rate': 'Error Rate',
            'Fatigue_Level': 'Fatigue Level',
            'Stress_Level_1_10': 'Stress Level'
        },
        title='<b>Plot H: Speed-Accuracy Trade-off Collapse: Active Compensation vs. Total Collapse</b>',
        opacity=0.7
    )
    fig_h.update_layout(yaxis=dict(tickformat='.0%'), margin=dict(l=40, r=40, t=60, b=40))
    export_plot(fig_h, "plot_h_sat_tradeoff_collapse")

    # =========================================================================
    # Plot I: Context-Switching Cap (OLS Trend)
    # =========================================================================
    print("\n[9/12] Rendering: Plot I (context_switching_cap)...")
    fig_i = px.scatter(
        sample_df,
        x='Task_Switches',
        y='Cognitive_Load_Score',
        color='Avg_Decision_Time_sec',
        color_continuous_scale='Turbo',
        trendline='ols',
        trendline_color_override='#e71d36', # Premium Red high-contrast trendline for light canvas
        labels={
            'Task_Switches': 'Task Switches',
            'Cognitive_Load_Score': 'Cognitive Load Score',
            'Avg_Decision_Time_sec': 'Avg Decision Time (s)'
        },
        title='<b>Plot I: The Context-Switching Cap Policy: Multitasking vs. Mental Load & Speed</b>'
    )
    fig_i.update_layout(title_font_size=18, margin=dict(l=40, r=40, t=60, b=40))
    export_plot(fig_i, "plot_i_context_switching_cap")

    # =========================================================================
    # Plot J: Sleep-Aware Stress Mitigation (Stress Slopes)
    # =========================================================================
    print("\n[10/12] Rendering: Plot J (sleep_aware_stress_slopes)...")
    df_policy = df.copy()
    df_policy['Workload_Bin'] = pd.cut(df_policy['Decisions_Made'], bins=6)
    df_policy['Workload_Range'] = df_policy['Workload_Bin'].apply(lambda x: f"{int(x.left)}-{int(x.right)}")
    grouped_policy = df_policy.groupby(['Sleep_Group', 'Workload_Range'], observed=False)['Stress_Level_1_10'].mean().reset_index()
    grouped_policy['Workload_Range'] = pd.Categorical(
        grouped_policy['Workload_Range'],
        categories=sorted(grouped_policy['Workload_Range'].unique(), key=lambda x: int(x.split('-')[0])),
        ordered=True
    )
    
    fig_j = px.line(
        grouped_policy.sort_values('Workload_Range'),
        x='Workload_Range',
        y='Stress_Level_1_10',
        color='Sleep_Group',
        color_discrete_sequence=['#e71d36', '#ff9f1c', '#2ec4b6'],
        markers=True,
        labels={
            'Workload_Range': 'Decision Workload (Decisions Made)',
            'Stress_Level_1_10': 'Avg Stress Level (1-10)',
            'Sleep_Group': 'Sleep Class'
        },
        title='<b>Plot J: The Sleep-Aware Mitigation Policy: Decision Stress Slopes by Sleep Class</b>'
    )
    fig_j.update_layout(title_font_size=18, margin=dict(l=40, r=40, t=60, b=40))
    export_plot(fig_j, "plot_j_sleep_aware_stress_slopes")

    # =========================================================================
    # Plot K: Overtime Fatigue Wall Cap (Bar with line)
    # =========================================================================
    print("\n[11/12] Rendering: Plot K (overtime_fatigue_wall_cap)...")
    hourly_errors = df.groupby('Hours_Awake')['Error_Rate'].mean().reset_index()
    fig_k = px.bar(
        hourly_errors,
        x='Hours_Awake',
        y='Error_Rate',
        color='Error_Rate',
        color_continuous_scale='OrRd',
        labels={
            'Hours_Awake': 'Continuous Hours Awake',
            'Error_Rate': 'Average Error Rate'
        },
        title='<b>Plot K: The Overtime Fatigue Wall Cap: Hourly Error Rate vs. Corporate 2% Quality Tolerance Limit</b>'
    )
    fig_k.add_shape(
        type="line", x0=6.5, x1=17.5, y0=0.02, y1=0.02,
        line=dict(color="#e71d36", width=3, dash="dash")
    )
    fig_k.add_annotation(
        x=10, y=0.025, text="⚠️ <b>Corporate Quality Tolerance Limit (2% Max Errors)</b>",
        showarrow=False, font=dict(color="#e71d36", size=11)
    )
    fig_k.update_layout(title_font_size=18, yaxis=dict(tickformat='.1%'), margin=dict(l=40, r=40, t=60, b=40))
    export_plot(fig_k, "plot_k_overtime_fatigue_wall_cap")

    # =========================================================================
    # Plot L: False Alert Jitter Phenotype (Dual Axis)
    # =========================================================================
    print("\n[12/12] Rendering: Plot L (false_alert_jitter_phenotype)...")
    sleep_deprived = df[df['Sleep_Hours_Last_Night'] < 6].copy()
    caffeine_stats = sleep_deprived.groupby('Caffeine_Intake_Cups')[['Avg_Decision_Time_sec', 'Error_Rate']].mean().reset_index()
    
    fig_l = go.Figure()
    fig_l.add_trace(go.Scatter(
        x=caffeine_stats['Caffeine_Intake_Cups'],
        y=caffeine_stats['Avg_Decision_Time_sec'],
        name='Avg Decision Time (Seconds) - Productivity',
        line=dict(color='#2ec4b6', width=4),
        mode='lines+markers'
    ))
    fig_l.add_trace(go.Scatter(
        x=caffeine_stats['Caffeine_Intake_Cups'],
        y=caffeine_stats['Error_Rate'] * 100,
        name='Error Rate (%) - Mistakes',
        line=dict(color='#e71d36', width=4, dash='dash'),
        mode='lines+markers',
        yaxis='y2'
    ))
    fig_l.update_layout(
        title='<b>Plot L: The False Alert Stimulant Jitter: Decision Speed Boost vs. Mistake Surge</b>',
        title_font_size=18,
        xaxis=dict(title='Caffeine Consumed (Cups during Shift)', dtick=1),
        yaxis=dict(title='Avg Decision Time (s) - Lower is Faster', title_font=dict(color='#2ec4b6'), tickfont=dict(color='#2ec4b6')),
        yaxis2=dict(title='Error Rate (%) - Lower is Better', title_font=dict(color='#e71d36'), tickfont=dict(color='#e71d36'), overlaying='y', side='right'),
        legend=dict(x=0.05, y=0.95),
        margin=dict(l=40, r=40, t=60, b=40)
    )
    export_plot(fig_l, "plot_l_false_alert_jitter_phenotype")

    print("\nAll 12 visualizations rendered and saved successfully inside 'exports/'!")

if __name__ == '__main__':
    main()
