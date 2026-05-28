"""
theme.py — shared visual constants for the Neuropulse dashboard.
All chart components MUST import their colors and category orders from here.
"""
# ── 1. ORDERED CATEGORIES (Must be defined first!) ───────────────────────────
FATIGUE_ORDER = ["Low", "Medium", "High"]  
TIME_ORDER = ["Morning", "Afternoon", "Evening", "Night"]
SYS_REC_ORDER = ["Continue", "Slow Down", "Take Break"]
SLEEP_GROUP_ORDER = ["Poor Sleep", "Adequate Sleep", "Good Sleep"]
STRESS_GROUP_ORDER = ["Low", "Medium", "High"]
EXPERIENCE_ORDER = ["New (0-3)", "Mid-level (3-7)", "Senior (7-15)", "Veteran (15+)"]
SLEEP_QUALITY_ORDER = ["Poor", "Fair", "Good", "Excellent"]

# ── 2. COLOR MAPS ─────────────────────────────────────────────────────────────
FATIGUE_COLORS = {
    "Low": "#FFE0B2",     
    "Medium": "#FF9800",  
    "Moderate": "#FF9800",  # Temporary alias safety-net
    "High": "#E65100"     
}

SYS_REC_COLORS = {
    "Continue": "#2E7D32",   
    "Slow Down": "#FBC02D",  
    "Take Break": "#C62828"  
}

TIME_COLORS = {
    "Morning": "#FFF9C4",    
    "Afternoon": "#29B6F6",  
    "Evening": "#5C6BC0",    
    "Night": "#1A237E"       
}

SLEEP_GROUP_COLORS = {
    "Poor Sleep": "#E8F5E9",     
    "Adequate Sleep": "#81C784", 
    "Good Sleep": "#2E7D32"      
}

STRESS_COLORS = {
    "Low": "#F3E5F5",     
    "Medium": "#BA68C8",  
    "High": "#6A1B9A"     
}

EXPERIENCE_COLORS = {
    "New (0-3)": "#ECEFF1",
    "Mid-level (3-7)": "#90A4AE",
    "Senior (7-15)": "#546E7A",
    "Veteran (15+)": "#263238"
}

SLEEP_QUALITY_COLORS = {
    "Poor": "#E0F2F1",
    "Fair": "#4DB6AC",
    "Good": "#00897B",
    "Excellent": "#004D40"
}

SELECTION_COLORS = {"Selected": "#E91E63", "Not selected": "#CFD8DC"}
NEUTRAL = "#607D8B"
NEUTRAL_LIGHT = "#CFD8DC"
OKABE_ITO = ["#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2", "#D55E00", "#CC79A7", "#000000"]
# ── CONTINUOUS COLORSCALES ────────────────────────────────────────────────────
# Use these in `color_continuous_scale=`. Prefer perceptually uniform scales.

CONTINUOUS_SEQUENTIAL = "Viridis"   # general purpose
CONTINUOUS_DIVERGING = "RdBu_r"     # for symmetric data around a center
CONTINUOUS_RISK = "Reds"            # one-sided: higher = worse

# ── LOOKUP FUNCTIONS ──────────────────────────────────────────────────────────
# Helpers so chart code can ask "what's the right color map for this variable?"

_VARIABLE_TO_COLOR_MAP = {
    "Fatigue_Level": FATIGUE_COLORS,
    "System_Recommendation": SYS_REC_COLORS,
    "Time_of_Day": TIME_COLORS,
    "Sleep_Group": SLEEP_GROUP_COLORS,
}

_VARIABLE_TO_ORDER = {
    "Fatigue_Level": FATIGUE_ORDER,
    "System_Recommendation": SYS_REC_ORDER,
    "Time_of_Day": TIME_ORDER,
    "Sleep_Group": SLEEP_GROUP_ORDER,
    "Stress_Group": STRESS_GROUP_ORDER,
    "Experience_Group": EXPERIENCE_ORDER,
    "Self_Reported_Sleep_Quality": SLEEP_QUALITY_ORDER,
}

def get_color_map(variable_name):
    """Return the canonical color map for a categorical variable, or None."""
    return _VARIABLE_TO_COLOR_MAP.get(variable_name)

def get_category_order(variable_name):
    """Return the canonical category order for a variable, or None."""
    return _VARIABLE_TO_ORDER.get(variable_name)

# ── THEME APPLICATION ─────────────────────────────────────────────────────────
# Centralized layout theming. Replaces the existing `_apply_theme` in components.py.

FONT_FAMILY = "Inter, sans-serif"

def apply_theme(fig, *, height=None, show_legend=True):
    fig.update_layout(
        template="plotly_white",
        font_family=FONT_FAMILY,
        margin=dict(l=40, r=40, t=50, b=40),
        title_font=dict(size=15, family=FONT_FAMILY, color="#2C3E50"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=show_legend,
        hoverlabel=dict(bgcolor="white", font_size=12, font_family=FONT_FAMILY),
    )
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor="#dee2e6")
    fig.update_yaxes(showgrid=True, gridcolor="rgba(200,200,200,0.3)",
                     zeroline=False, linecolor="#dee2e6")
    if height is not None:
        fig.update_layout(height=height)
    return fig
