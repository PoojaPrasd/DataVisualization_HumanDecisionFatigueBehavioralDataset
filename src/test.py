import os
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import seaborn as sns
import plotly.express as px
import pandas as pd
import numpy as np

# Configure premium light theme defaults
plt.style.use('default')
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.facecolor'] = 'white'

# Load the built-in Gapminder dataset from Plotly Express
df = px.data.gapminder()

# Dynamically extract the most recent year available in the dataset
most_recent_year = df["year"].max()
print(f"Dynamically identified most recent year in dataset: {most_recent_year}")

# Filter for the most recent year to keep the visual clean and current
df_recent = df[df["year"] == most_recent_year].copy()
df_recent["pop_millions"] = df_recent["pop"] / 1e6

# Sort by population descending so smaller bubbles are plotted ON TOP of larger ones in the good plot,
# preventing large country bubbles (like China and India) from obscuring smaller data points!
df_recent = df_recent.sort_values(by="pop", ascending=False).copy()

export_folder = "exports/good_bad"
os.makedirs(export_folder, exist_ok=True)

# =========================================================================
# CHART 1: THE BAD VISUALIZATION (Separate Window)
# =========================================================================
fig_bad, ax_bad = plt.subplots(figsize=(10, 8), facecolor='white')

# Violation: Using bubble size to represent Life Expectancy (unintuitive bounded scale).
# Violation: Using a sequential gradient colormap (YlOrRd) to represent Continent (nominal categories).
continents = df_recent['continent'].unique()
colors = plt.cm.YlOrRd(np.linspace(0.3, 0.9, len(continents)))
color_map_bad = dict(zip(continents, colors))

for continent, group in df_recent.groupby('continent'):
    ax_bad.scatter(
        group['gdpPercap'], 
        group['lifeExp'], 
        s=(group['lifeExp'] - 38) ** 2 * 0.4, # Deceptive mapping of area
        color=color_map_bad[continent],
        label=continent,
        alpha=1.0, 
        edgecolors='black',
        linewidths=1.2
    )

# Chartjunk: Distracting, high-contrast grey gridlines on a lavender-grey canvas
ax_bad.set_facecolor('#eaeaf2')
ax_bad.grid(True, color='#888888', linestyle='--', linewidth=1.0)
ax_bad.tick_params(colors='#333333', labelsize=10)

ax_bad.set_title(f"Global Life Expectancy vs. GDP per Capita ({most_recent_year})\nBubble Size: Life Expectancy | Bubble Color: Continent (Sequential Scale)", 
                 fontsize=11, fontweight='bold', color='#333333', pad=15)
ax_bad.set_xlabel("GDP per Capita", fontsize=10, color='#cc0000')
ax_bad.set_ylabel("Life Expectancy", fontsize=10, color='#cc0000')

# Legend for bad plot (Unintuitive combined sequential list)
ax_bad.legend(title="Continent", loc="lower right", facecolor='#eaeaf2')

plt.tight_layout()
bad_export_path = os.path.join(export_folder, "bad_intuitive.png")
plt.savefig(bad_export_path, bbox_inches='tight', dpi=150, facecolor='white')
print(f"SUCCESS: Exported Bad Chart to {bad_export_path}")


# =========================================================================
# CHART 2: THE GOOD VISUALIZATION (Separate Window with Separate Legends)
# =========================================================================
# Explicit mapping of premium Set2 palette colors to continents. 
# This ensures 100% identical color alignment between the scatter points 
# and the decoupled legends under any sorting order.
continent_colors = {
    'Africa': '#FC8D62',   # Orange
    'Americas': '#8DA0CB', # Muted Blue
    'Asia': '#66C2A5',     # Teal/Green (China & India will be green)
    'Europe': '#E78AC3',   # Muted Pink
    'Oceania': '#A6D854'   # Light Lime Green
}

fig_good, ax_good = plt.subplots(figsize=(11, 8), facecolor='#F4F6FA')

# Solution: Intuitive Size Mapping (Population) & Intuitive Color Mapping (Continent Categorical).
# Solution: Logarithmic X-axis to spread out skewed economic data cleanly.
# Solution: Transparency (alpha=0.7) to manage overlapping bubbles.
# Note: We omit standard legend inside scatterplot so we can draw custom decoupled legends!
scatter = sns.scatterplot(
    data=df_recent,
    x="gdpPercap",
    y="lifeExp",
    hue="continent",
    size="pop_millions",
    sizes=(30, 900), # Controlled size boundaries for high readability
    palette=continent_colors, # Pass the explicit color dictionary!
    alpha=0.75,       # Muted opacity for premium color blending
    edgecolor='white', # Crisp white outlines to separate overlapping bubbles beautifully
    linewidth=0.7,
    ax=ax_good,
    legend=False      # Disable Seaborn's default combined legend
)

# Premium layout details: Cool Slate-Blue background color scheme (Highly Professional)
ax_good.set_facecolor('#F4F6FA')

# Maximize Data-Ink Ratio: Strip out all 4 boundary spines completely (Tufte's Spine-Free layout)!
# The data is framed cleanly and purely by gridlines and tick labels alone.
for spine in ['top', 'right', 'left', 'bottom']:
    ax_good.spines[spine].set_visible(False)

# Extremely faint gridlines (Major lines are soft, minor are ultra-light dotted)
ax_good.grid(True, which="major", color='#E1E6EB', linestyle='-', linewidth=0.6, zorder=0)
ax_good.grid(True, which="minor", color='#ECF0F4', linestyle=':', linewidth=0.4, zorder=0)
ax_good.set_axisbelow(True) # Keep gridlines behind scatter bubbles

# Set clean logarithmic scale for GDP
ax_good.set_xscale('log')

# Maximize Data-Ink: Hide physical tick marks (strokes) while keeping readable text labels
ax_good.tick_params(colors='#4f5b66', labelsize=9.5, bottom=False, left=False, which='both')

# Format X-axis tick labels as beautiful currency values (e.g. $1,000, $10,000)
import matplotlib.ticker as ticker
ax_good.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f"${int(x):,}"))

# Enable minor tick markers on X-axis log scale to drive the faint log gridlines
ax_good.xaxis.set_minor_locator(ticker.LogLocator(base=10.0, subs='auto'))

# (No country name text annotations on graph)
ax_good.set_title(f"Global Life Expectancy vs. GDP per Capita ({most_recent_year})", 
                 fontsize=11, fontweight='bold', color='#333333', pad=15)
ax_good.set_xlabel("GDP per Capita (Log Scale)", fontsize=10, color='#2e7d32')
ax_good.set_ylabel("Life Expectancy (years)", fontsize=10, color='#2e7d32')


# -------------------------------------------------------------------------
# DECOUPLED LEGEND SYSTEM (Separate Color and Size Meaning)
# -------------------------------------------------------------------------
# (Using pre-defined continent_colors dictionary to guarantee color alignment)

# 1. Legend Box 1: Color Meanings (Continent Categories)
color_handles = [
    Line2D([0], [0], marker='o', color='w', markerfacecolor=color, markersize=10, label=continent)
    for continent, color in continent_colors.items()
]
legend_color = ax_good.legend(
    handles=color_handles,
    title="Continent",
    loc="upper left",
    bbox_to_anchor=(1.02, 1.0), # Stacks at top-right outside subplot
    facecolor='#F4F6FA',
    edgecolor='none', # Maximize Data-Ink: Remove legend outline border entirely
    fontsize=9.5,
    title_fontsize=10.5
)
ax_good.add_artist(legend_color) # Locks Legend 1 as a separate visual layer

# 2. Legend Box 2: Size Meanings (Population Indicators)
# We map population values in millions (10M, 100M, 500M, 1000M) to visual diameter sizes
size_values = [10, 100, 500, 1000]
size_handles = [
    Line2D([0], [0], marker='o', color='w', markerfacecolor='#888888', markeredgecolor='none',
           markersize=np.sqrt(val) * 0.9, alpha=0.7, label=f"{val}M People")
    for val in size_values
]
legend_size = ax_good.legend(
    handles=size_handles,
    title="Population",
    loc="upper left",
    bbox_to_anchor=(1.02, 0.55), # Stacks below Legend 1 outside subplot
    facecolor='#F4F6FA',
    edgecolor='none', # Maximize Data-Ink: Remove legend outline border entirely
    fontsize=9.5,
    title_fontsize=10.5
)


# (No explanation text boxes on graph)

plt.tight_layout()
good_export_path = os.path.join(export_folder, "good_intuitive.png")
plt.savefig(good_export_path, bbox_inches='tight', dpi=150, facecolor='#F4F6FA')
print(f"SUCCESS: Exported Good Chart to {good_export_path}")
plt.show()

# =========================================================================
# THE SCIENCE OF VISUALIZATION: GOOD VS. BAD
# =========================================================================
"""
EXPLANATION: What makes the Good visualization good, and the Bad visualization bad?

1. THE BAD VISUALIZATION:
   - Deceptive Size Mapping: It uses raw values or arbitrary math `(lifeExp - 38)**2` to scale the bubbles. 
     This violates the "Principle of Proportional Ink", making differences look much larger than they actually are.
   - Inappropriate Color Scales: It uses a Sequential Colormap (YlOrRd - Yellow to Red) for Continents. 
     Sequential colors imply a hierarchy or magnitude (e.g., Red is "more" or "worse" than Yellow), but 
     Continents are Nominal/Categorical data. They have no mathematical order.
   - Low Data-Ink Ratio & Chartjunk: The chart features heavy, dark, high-contrast dashed gridlines and 
     a grey background. The gridlines fight with the data for the viewer's attention.
   - Overlap Obscuration: Because the data isn't sorted by size, massive bubbles are drawn last, completely 
     swallowing and hiding smaller bubbles underneath them.
   - Bad Axes: GDP per capita is highly skewed. Plotting it on a linear scale clumps 90% of the countries 
     against the left axis, making the relationship invisible.

2. THE GOOD VISUALIZATION:
   - Proper Semantic Scaling: Bubble size maps accurately to Population. It provides an immediate, intuitive 
     grasp of demographic weight.
   - Proper Color Mapping: Uses a Qualitative/Categorical palette (Muted Blue, Pink, Orange, Green). Each 
     color is distinct, implying separate categories without enforcing an arbitrary mathematical order.
   - Z-Order Sorting: The dataframe is sorted by population (Descending) before plotting. This guarantees 
     that the smallest bubbles are drawn last, placing them ON TOP of the massive bubbles. No data is hidden.
   - High Data-Ink Ratio: Tufte's principles are applied by stripping away the black border spines, turning 
     the gridlines into ultra-faint, soft background guides, and removing physical tick marks.
   - Logarithmic Axis: The X-axis uses a log scale, perfectly spreading out the highly skewed GDP data so 
     a clear linear/curved relationship emerges across the entire canvas.
   - Decoupled Legends: Instead of one massive confusing legend, color (Continent) and size (Population) 
     are split into two distinct, highly readable floating legends with no harsh borders.
"""

print("\nSUCCESS: Both visual scripts generated independently and exported with separate legends.")