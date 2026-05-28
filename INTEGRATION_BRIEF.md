# Integration Brief — Port Memo's Workload + Confounding Tab into the Team App

**For**: Claude Code in VSCode
**Goal**: Integrate Memo's brushing-based Workload + Confounding tab into the team's
"Neuropulse" app (which has login + global sidebar filters + zoom-based tab rebuilding).
**Approach**: Memo's tab becomes a self-contained brushing island (Option 1). It reuses
two existing global sidebar dropdowns and adds one new one. It is isolated from the
team's tab-rebuild callback so the two interaction paradigms don't collide.

Read this fully, propose an execution plan, then execute step by step, stopping after
each numbered step to confirm the app still boots. Show diffs before applying.

---

## 0. Context: two incompatible interaction paradigms

The team app (target) and Memo's tab (source) use different models:

- **Team app**: global sidebar filters (`color-by-filter`, `target-variable-filter`,
  `dynamic-filter-column`, `dynamic-filter-values`) plus per-chart zoom (`relayoutData`).
  The `update_dashboard` callback rebuilds ALL FOUR tabs' contents
  (`tab-1-content` … `tab-4-content`) whenever a global filter or zoom changes.
  There is no persistent selection state.
- **Memo's tab**: a persistent `dcc.Store(id="selection-store")` that callbacks read/write,
  updating individual figures in place via brushing (PCP + scatter), with PreventUpdate
  guards to prevent feedback loops.

These conflict: if Memo's charts live inside `tab-3-content` and `update_dashboard` keeps
outputting `tab-3-content.children`, then every global-filter change DESTROYS and RECREATES
Memo's charts, breaking the selection-store wiring. The integration's central job is to
ISOLATE tab-3 from `update_dashboard` while still letting Memo's charts READ two global
filters.

---

## 1. The dropdown plan (decided with the team)

Memo's tab needs three controls. Instead of adding all three, REUSE the team's existing
global sidebar dropdowns where possible:

| Memo's control | Source | Maps to |
|---|---|---|
| `conf-color` (scatter color/group) | **REUSE** team's `color-by-filter` | scatter color grouping + per-group regression |
| `conf-y` + `conf-target` (scatter Y axis + box compare-on) | **REUSE** team's `target-variable-filter` | both driven by one numeric selector |
| `conf-x` (scatter X axis) | **NEW** dropdown in sidebar | scatter X axis only |

So:
- Memo's `render_three_charts` callback reads `color-by-filter`, `target-variable-filter`,
  and the new `conf-x` as Inputs.
- The scatter's Y axis = `target-variable-filter` value; the box's compare-on = same value.
- The scatter's color/group = `color-by-filter` value.
- Only ONE new dropdown (`conf-x`) is added to the sidebar.

Also: ADD `Anomaly_Cohort` to the global `COLOR_COLUMNS` list (one tuple) so it becomes a
color-grouping option. This is the "answer key" to the engineered confounds in the data —
coloring the scatter by Anomaly_Cohort makes the planted divergent slopes visible.

---

## 2. Files and what happens to each

| File | Action |
|---|---|
| `theme.py` | NEW — copy from Memo's version into team's `src/dashboard/` |
| `selection.py` | NEW — copy from Memo's version into team's `src/dashboard/` |
| `components.py` | ADD Memo's chart functions (renamed to avoid collision); keep all team functions |
| `layout.py` | Replace `workload_memo_tab` content; add `conf-x` to sidebar; add `Anomaly_Cohort` to COLOR_COLUMNS; mount `selection-store` |
| `app.py` | Add Memo's 5 callbacks; REMOVE tab-3 from `update_dashboard` outputs |
| `data_loader.py` | UNCHANGED — use the team's richer version (with anomalies) |

The team's `data_loader.py` produces `Fatigue_Level` values of "Low"/"Medium"/"High" —
Memo's `theme.py` already aligns to "Medium", so no reconciliation is needed.

---

## 3. Execution steps

### Step 1 — Copy the two helper modules
Copy `theme.py` and `selection.py` from Memo's version verbatim into the team's
`src/dashboard/`. These are new files; no conflict.
Source paths (Memo's zip):
`src/dashboard/theme.py`, `src/dashboard/selection.py`.
**Validate**: `python -c "from src.dashboard import theme, selection; print('ok')"`.

### Step 2 — Port chart functions into components.py
From Memo's `components.py`, copy these into the team's `components.py`:
- `PCP_DIMENSIONS` (the list)
- `create_workload_parallel_coords` → **RENAME to `create_brushable_pcp`** (the team
  already has a `create_workload_parallel_coords`; do not overwrite it).
- `_fit_line`
- `create_confounding_scatter`
- `create_comparative_box`

These functions import from `.theme` and `.selection` inside their bodies — keep those
local imports. Add `import numpy as np` and `import plotly.graph_objects as go` at the top
of the team's components.py if not already present.

**Do not** modify or delete any of the team's existing functions.
**Validate**: `python -c "from src.dashboard.components import create_brushable_pcp, create_confounding_scatter, create_comparative_box; print('ok')"`.

### Step 3 — Add Anomaly_Cohort to COLOR_COLUMNS
In `layout.py`, add `("Anomaly_Cohort", "Anomaly cohort")` to the `COLOR_COLUMNS` list.
This makes it appear in the global `color-by-filter` dropdown.
**Validate**: app still boots; the color dropdown shows "Anomaly cohort" as an option.

### Step 4 — Add the conf-x dropdown to the sidebar
In `create_filter_sidebar`, add ONE new dropdown after the existing controls, in a
visually labeled group so it's clear it belongs to the confounding tab:

```python
html.Hr(),
html.Label("Confounding scatter — X axis", className="small fw-semibold mb-1"),
dcc.Dropdown(
    id="conf-x",
    options=[{"label": label, "value": value} for value, label in [
        ("Hours_Awake", "Hours awake"),
        ("Decisions_Made", "Decisions made"),
        ("Task_Switches", "Task switches"),
        ("Sleep_Hours_Last_Night", "Sleep hours"),
        ("Avg_Decision_Time_sec", "Decision time"),
        ("Cognitive_Load_Score", "Cognitive load"),
        ("Decision_Fatigue_Score", "Fatigue score"),
    ] if value in df.columns],
    value="Hours_Awake",
    clearable=False,
    className="mb-2",
),
```

**Validate**: sidebar shows the new dropdown; app boots.

### Step 5 — Mount selection-store
In `create_dashboard_page` (the function that builds the post-login page), add near the
top of its container children:
```python
dcc.Store(id="selection-store", data={"source": None, "filters": []}),
```
Also add a "Clear selection" button somewhere in the dashboard header row:
```python
dbc.Button("Clear selection", id="reset-selection-btn", color="light", size="sm",
           className="mt-2", style={"fontSize": "12px"}),
```
**Validate**: app boots; store and button exist (button does nothing yet).

### Step 6 — Replace the workload_memo_tab content
In `create_tab_contents`, replace the `workload_memo_tab = tab_wrap([...])` block with
Memo's layout: a wide PCP on top, then confounding scatter (md=8) + comparative box (md=4).

The charts must use stable graph ids that the callbacks expect:
`pcp-graph`, `conf-scatter`, `comp-box`.

These are NEW ids NOT in the team's GRAPH_IDS list (which is correct — they must NOT be in
GRAPH_IDS, because GRAPH_IDS charts get zoom-filtered by update_dashboard, and Memo's
charts use brushing instead).

The four figure-building lines for the old workload tab
(`fig_workload_1..4`) can stay defined (harmless) or be removed — but the workload tab body
must now render Memo's charts. Because Memo's charts are populated by callbacks (not static
figures), use `dcc.Graph(id=..., ...)` WITHOUT a `figure=` argument for the three Memo
charts. Note this differs from the team's `create_chart_card(fig, graph_id)` which expects
a prebuilt figure — so build the Memo cards with a small inline helper or a variant that
omits `figure=`.

Use this structure for the workload tab body:
```python
workload_memo_tab = tab_wrap([
    dbc.Row([
        dbc.Col(_memo_graph_card("pcp-graph", "240px"), md=12),
    ], className="g-2 mb-2"),
    dbc.Row([
        dbc.Col(_memo_graph_card("conf-scatter", "300px"), md=8),
        dbc.Col(_memo_graph_card("comp-box", "300px"), md=4),
    ], className="g-2"),
], "workload_memo")
```
where `_memo_graph_card` is a new helper (add it near `create_chart_card`):
```python
def _memo_graph_card(graph_id, height):
    return dbc.Card(dbc.CardBody([
        dcc.Graph(id=graph_id,
                  config={"displayModeBar": True,
                          "modeBarButtonsToAdd": ["lasso2d", "select2d"],
                          "modeBarButtonsToRemove": ["autoScale2d"],
                          "displaylogo": False},
                  style={"height": height})
    ], className="p-1"),
    className="shadow-sm rounded-2 border-0 h-100",
    style={"backgroundColor": "#ffffff", "overflow": "hidden"})
```
**Validate**: navigate to the Workload tab; three empty chart boxes render in the
PCP-on-top, scatter+box-below layout. They are empty because callbacks aren't added yet.

### Step 7 — Isolate tab-3 from update_dashboard (CRITICAL)
In `app.py`, the `update_dashboard` callback currently outputs four tab contents. Remove
the tab-3 output so Memo's charts are never destroyed by global-filter rebuilds:

- Remove `Output("tab-3-content", "children")` from the decorator.
- The function returns four values; it must now return three, and `create_tab_contents`
  returns four tabs — so capture the workload tab but don't return it. Simplest: keep
  calling `create_tab_contents` but unpack and return only tabs 1, 2, 4:
  ```python
  wb, risk, workload, interv = create_tab_contents(filtered, color_by=..., target_col=...)
  return wb, risk, interv   # tab-3 (workload) intentionally excluded
  ```
  And the decorator outputs become:
  ```python
  Output("tab-1-content", "children"),
  Output("tab-2-content", "children"),
  Output("tab-4-content", "children"),
  ```

This means tab-3 is rendered ONCE at initial page build (via `create_tabs_content`) and
never rebuilt. Memo's callbacks own it from then on.

**Validate**: app boots; changing a global filter updates tabs 1/2/4 but does NOT wipe
tab-3's charts (they stay, though still empty until step 8).

### Step 8 — Add Memo's five callbacks to app.py
Add these callbacks (adapted so the render callback reads the sidebar dropdowns). Import
`PreventUpdate` and the selection helpers.

```python
from dash.exceptions import PreventUpdate
try:
    from .selection import EMPTY_SELECTION, selection_from_pcp_figure, selection_from_scatter_brush
except ImportError:
    from selection import EMPTY_SELECTION, selection_from_pcp_figure, selection_from_scatter_brush

@app.callback(
    Output("selection-store", "data", allow_duplicate=True),
    Input("reset-selection-btn", "n_clicks"),
    prevent_initial_call=True,
)
def reset_selection(_):
    return EMPTY_SELECTION

@app.callback(
    Output("selection-store", "data", allow_duplicate=True),
    Input("pcp-graph", "restyleData"),
    State("pcp-graph", "figure"),
    prevent_initial_call=True,
)
def pcp_writes_selection(_, figure):
    return selection_from_pcp_figure(figure)

@app.callback(
    Output("pcp-graph", "figure"),
    Input("selection-store", "data"),
)
def render_pcp(selection):
    if selection and selection.get("source") == "pcp":
        raise PreventUpdate
    from .components import create_brushable_pcp
    return create_brushable_pcp(df, selection=selection)

@app.callback(
    Output("conf-scatter", "figure"),
    Output("comp-box", "figure"),
    Input("selection-store", "data"),
    Input("conf-x", "value"),
    Input("target-variable-filter", "value"),   # REUSED as scatter Y + box compare-on
    Input("color-by-filter", "value"),           # REUSED as scatter color/group
)
def render_three_charts(selection, conf_x, target_var, color_var):
    from .components import create_confounding_scatter, create_comparative_box
    y_var = target_var or "Error_Rate"
    color = color_var or "System_Recommendation"
    fig_scatter = create_confounding_scatter(df, conf_x, y_var, color, selection=selection)
    fig_box = create_comparative_box(df, y_var, selection=selection)
    return fig_scatter, fig_box

@app.callback(
    Output("selection-store", "data", allow_duplicate=True),
    Input("conf-scatter", "selectedData"),
    State("conf-x", "value"),
    State("target-variable-filter", "value"),
    prevent_initial_call=True,
)
def scatter_writes_selection(selected, x_col, y_col):
    result = selection_from_scatter_brush(selected, x_col, y_col or "Error_Rate")
    if not result.get("filters"):
        raise PreventUpdate
    return result
```

Note: `app = Dash(...)` already has `suppress_callback_exceptions=True`, which is needed
because tab-3's components are defined in layout that's only built after login — good, leave it.

All callbacks use `@app.callback` (the team app already uses this form; the global
`@callback` does not register in this Dash version).

**Validate**: full interactive test (see Acceptance below).

---

## 4. Collision checklist (verify none are violated)

- `pcp-graph`, `conf-scatter`, `comp-box` are NOT in GRAPH_IDS. ✓ required
- Memo's `create_brushable_pcp` does not overwrite team's `create_workload_parallel_coords`. ✓ required
- No duplicate component ids: `conf-x`, `selection-store`, `reset-selection-btn` are new and unique. ✓ verify
- `color-by-filter` and `target-variable-filter` are read by BOTH `update_dashboard` (for tabs 1/2/4) AND Memo's `render_three_charts` (for tab-3). Multiple callbacks reading the same Input is allowed in Dash. ✓ fine
- `update_dashboard` no longer outputs `tab-3-content`. ✓ required

---

## 5. Acceptance criteria

After integration:
- App boots, login works (gph/gph), dashboard loads.
- Tab 3 (Workload + Confounding) shows: wide PCP on top, confounding scatter + comparative box below.
- Brushing a PCP axis updates the scatter (adds dashed local regression) and the box (splits selected/not).
- Box-selecting on the scatter updates the PCP (constraint bands) without resetting.
- Changing the global `color-by-filter` recolors the scatter's groups (and updates tabs 1/2/4).
- Changing the global `target-variable-filter` changes the scatter Y axis and box variable (and tabs 1/2/4).
- Changing `conf-x` changes the scatter X axis (tab 3 only).
- Selecting "Anomaly cohort" in color-by makes the engineered confound slopes visible in the scatter.
- "Clear selection" resets tab-3's brushing.
- Tabs 1, 2, 4 retain their original zoom-filter behavior, unaffected.
- Changing a global filter does NOT wipe/blank tab-3's charts.

---

## 6. Execution order summary
1. Copy theme.py + selection.py
2. Port chart functions (rename PCP → create_brushable_pcp)
3. Add Anomaly_Cohort to COLOR_COLUMNS
4. Add conf-x dropdown to sidebar
5. Mount selection-store + reset button
6. Replace workload_memo_tab content (empty charts OK)
7. Remove tab-3 from update_dashboard (isolation — critical)
8. Add the five callbacks; full interactive test

Stop after each step. Show diffs before applying. Keep no debug prints in the final code.
