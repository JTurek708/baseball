import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

PITCH_COLORS = {
    "4-Seam FB":     "#D22D49",
    "Sinker":        "#FE9D00",
    "Cutter":        "#933F2C",
    "Slider":        "#EEE716",
    "Sweeper":       "#DBE81C",
    "Curveball":     "#00D1ED",
    "Knuckle-Curve": "#3BACAC",
    "Changeup":      "#1DBE3A",
    "Splitter":      "#3CB371",
    "Knuckleball":   "#777777",
}

# Editorial Layout
EDITORIAL_LAYOUT = dict(
    paper_bgcolor="#F5F1E8",
    plot_bgcolor="#F5F1E8",
    font=dict(family="Lora, Georgia, serif", color="#2B2B2B", size=13),
    title=dict(
        font=dict(family="Playfair Display, Georgia, serif", size=20, color="#2B2B2B"),
        x=0,
        xanchor="left"
    ),
    xaxis=dict(
        gridcolor="#D9D2BC",
        linecolor="#2B2B2B",
        zerolinecolor="#2B2B2B"
    ),
    yaxis=dict(
        gridcolor="#D9D2BC",
        linecolor="#2B2B2B",
        zerolinecolor="#2B2B2B"
    ),
    legend=dict(
        font=dict(family="Lora, Georgia, serif", size=12),
        bgcolor="rgba(0,0,0,0)"
    ),
    margin=dict(l=40, r=20, t=60, b=40)
)
# Pitcher Compare Colors
PITCHER_COMPARE_COLORS = ["#8B2C2C", "#1F3A5F"]

PITCH_SYMBOLS = {
    "4-Seam FB":     "circle",
    "Sinker":        "square",
    "Cutter":        "diamond",
    "Slider":        "triangle-up",
    "Sweeper":       "triangle-down",
    "Curveball":     "star",
    "Knuckle-Curve": "star-triangle-up",
    "Changeup":      "cross",
    "Splitter":      "x",
    "Knuckleball":   "hexagon",
}

# Chart 1: Movement Profile
def plot_movement(df):
    from utils.data import get_whiff_rate

    summary = (
        df.groupby("pitch_label")
        .agg(
            pfx_x=("pfx_x", "mean"),
            pfx_z=("pfx_z", "mean"),
            count=("pitch_type", "count")
        )
        .reset_index()
    )
    summary["pfx_x_in"] = summary["pfx_x"] * 12
    summary["pfx_z_in"] = summary["pfx_z"] * 12

    whiff_df = get_whiff_rate(df)
    summary = summary.merge(whiff_df[["pitch_label", "whiff_rate"]], on="pitch_label", how="left")
    summary["whiff_pct"] = (summary["whiff_rate"] * 100).round(1)
    summary["label"] = summary.apply(
        lambda r: f"{r['pitch_label']}<br>Whiff: {r['whiff_pct']}%", axis=1
    )

    fig = px.scatter(
        summary,
        x="pfx_x_in",
        y="pfx_z_in",
        color="pitch_label",
        size="count",
        text="pitch_label",
        color_discrete_map=PITCH_COLORS,
        custom_data=["whiff_pct", "count"],
        labels={
            "pfx_x_in": "Horizontal Break (in.)",
            "pfx_z_in": "Induced Vertical Break (in.)",
            "pitch_label": "Pitch",
        },
        title="Pitch Movement Profile"
    )
    fig.add_hline(y=0, line_dash="dash", line_color="grey")
    fig.add_vline(x=0, line_dash="dash", line_color="grey")
    fig.update_traces(
        textposition="top center",
        hovertemplate=(
            "<b>%{text}</b><br>"
            "H. Break: %{x:.1f} in.<br>"
            "V. Break: %{y:.1f} in.<br>"
            "Whiff Rate: %{customdata[0]}%<br>"
            "# Thrown: %{customdata[1]}<br>"
            "<extra></extra>"
        )
    )
    fig.update_layout(**EDITORIAL_LAYOUT)
    return fig

# Chart 2: Pitch Mix
def plot_usage(df):
    usage = (
        df["pitch_label"]
        .value_counts(normalize=True)
        .reset_index()
    )
    usage.columns = ["pitch_label", "pct"]
    usage = usage.sort_values("pct")

    fig = px.bar(
        usage,
        x="pct",
        y="pitch_label",
        orientation="h",
        color="pitch_label",
        color_discrete_map=PITCH_COLORS,
        text=usage["pct"].map("{:.1%}".format),
        labels={"pct": "Usage %", "pitch_label": ""},
        title="Pitch Mix"
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        template="plotly_dark",
        showlegend=False,
        xaxis_tickformat=".0%"
    )
    return fig

# Chart 3: Velocity Distribution
def plot_velo(df):
    df_clean = df.dropna(subset=["release_speed"])

    fig = go.Figure()
    for pitch in df_clean["pitch_label"].unique():
        subset = df_clean[df_clean["pitch_label"] == pitch]
        fig.add_trace(go.Violin(
            x=subset["release_speed"],
            name=pitch,
            fillcolor=PITCH_COLORS.get(pitch, "#888888"),
            line_color=PITCH_COLORS.get(pitch, "#888888"),
            opacity=0.7,
            meanline_visible=True
        ))
    fig.update_layout(
        template="plotly_dark",
        title="Velocity Distribution by Pitch Type",
        xaxis_title="Velocity (mph)",
        showlegend=True
    )
    return fig

# Chart 4: Spin Rate
def plot_spin(df):
    df_clean = df.dropna(subset=["release_spin_rate"])

    fig = px.box(
        df_clean,
        x="pitch_label",
        y="release_spin_rate",
        color="pitch_label",
        color_discrete_map=PITCH_COLORS,
        labels={
            "release_spin_rate": "Spin Rate (RPM)",
            "pitch_label": ""
        },
        title="Spin Rate by Pitch Type"
    )
    fig.update_layout(
        **EDITORIAL_LAYOUT,
        showlegend=False
    )
    return fig

# Count-Leverage Breakdown
def plot_count_usage(df):
    count_cols = ["balls", "strikes"]
    df_counts = df.dropna(subset=count_cols).copy()
    df_counts["count"] = df_counts["balls"].astype(int).astype(str) + "-" + df_counts["strikes"].astype(int).astype(str)

    COUNT_ORDER = ["0-0", "1-0", "2-0", "3-0", "0-1", "1-1", "2-1", "3-1", "0-2", "1-2", "2-2", "3-2"]
    df_counts = df_counts[df_counts["count"].isin(COUNT_ORDER)]

    usage = (
        df_counts.groupby(["count", "pitch_label"])
        .size()
        .reset_index(name="n")
    )
    usage["pct"] = usage.groupby("count")["n"].transform(lambda x: x / x.sum())
    usage["count"] = pd.Categorical(usage["count"], categories=COUNT_ORDER, ordered=True)
    usage = usage.sort_values("count")
    usage["pct_label"] = (usage["pct"] * 100).round(1).astype(str) + "%"

    fig = px.bar(
        usage,
        x="count",
        y="pct",
        color="pitch_label",
        color_discrete_map=PITCH_COLORS,
        labels={
            "count": "Count",
            "pct": "Usage %",
            "pitch_label": "Pitch"
        },
        title="Pitch Usage by Count",
        text="pct_label"
    )
    fig.update_layout(
        **EDITORIAL_LAYOUT,
        barmode="stack",
        yaxis_tickformat=".0%",
        legend_title="Pitch"
    )
    fig.update_traces(textposition="inside", textfont_size=10)
    return fig

def plot_movement_comparison(df):
    summary = (
        df.groupby(["pitcher_name", "pitch_label"])
        .agg(
            pfx_x=("pfx_x", "mean"),
            pfx_z=("pfx_z", "mean"),
            count=("pitch_type", "count")
        )
        .reset_index()
    )
    summary["pfx_x_in"] = summary["pfx_x"] * 12
    summary["pfx_z_in"] = summary["pfx_z"] * 12

    fig = px.scatter(
        summary,
        x="pfx_x_in",
        y="pfx_z_in",
        color="pitcher_name",
        symbol="pitch_label",
        size="count",
        text="pitch_label",
        color_discrete_sequence=PITCHER_COMPARE_COLORS,
        symbol_map=PITCH_SYMBOLS,
        labels={
            "pfx_x_in": "Horizontal Break (in.)",
            "pfx_z_in": "Induced Vertical Break (in.)",
            "pitcher_name": "Pitcher",
            "pitch_label": "Pitch"
        },
        title="Movement Profile Comparison"
    )
    fig.add_hline(y=0, line_dash="dash", line_color="grey")
    fig.add_vline(x=0, line_dash="dash", line_color="grey")
    fig.update_traces(textposition="top center")
    fig.update_layout(**EDITORIAL_LAYOUT)
    return fig

def plot_usage_comparison(df):
    usage = (
        df.groupby(["pitcher_name", "pitch_label"])
        .size()
        .reset_index(name="n")
    )
    usage["pct"] = usage.groupby("pitcher_name")["n"].transform(lambda x: x / x.sum())

    fig = px.bar(
        usage,
        x="pitch_label",
        y="pct",
        color="pitcher_name",
        barmode="group",
        color_discrete_sequence=PITCHER_COMPARE_COLORS,
        text=usage["pct"].map("{:.1%}".format),
        labels={
            "pitch_label": "",
            "pct": "Usage %",
            "pitcher_name": "Pitcher"
        },
        title="Pitch Mix Comparison"
    )
    fig.update_layout(
        **EDITORIAL_LAYOUT,
        yaxis_tickformat=".0%",
        legend_title="Pitcher"
    )
    fig.update_traces(textposition="outside", textfont_size=10)
    return fig

def plot_velo_comparison(df):
    df_clean = df.dropna(subset=["release_speed"])

    fig = px.box(
        df_clean,
        x="pitch_label",
        y="release_speed",
        color="pitcher_name",
        color_discrete_sequence=PITCHER_COMPARE_COLORS,
        labels={
            "pitch_label": "",
            "release_speed": "Velocity (mph)",
            "pitcher_name": "Pitcher"
        },
        title="Velocity Distribution Comparison",
        boxmode="group"
    )
    fig.update_layout(
        **EDITORIAL_LAYOUT,
        legend_title="Pitcher"
    )
    return fig


def plot_spin_comparison(df):
    df_clean = df.dropna(subset=["release_spin_rate"])

    fig = px.box(
        df_clean,
        x="pitch_label",
        y="release_spin_rate",
        color="pitcher_name",
        color_discrete_sequence=PITCHER_COMPARE_COLORS,
        labels={
            "pitch_label": "",
            "release_spin_rate": "Spin Rate (RPM)",
            "pitcher_name": "Pitcher"
        },
        title="Spin Rate Comparison",
        boxmode="group"
    )
    fig.update_layout(
        **EDITORIAL_LAYOUT,
        legend_title="Pitcher"
    )
    return fig

def plot_usage_by_hand(df):
    usage = (
        df.groupby(["batter_hand", "pitch_label"])
        .size()
        .reset_index(name="n")
    )
    usage["pct"] = usage.groupby("batter_hand")["n"].transform(lambda x: x / x.sum())

    fig = px.bar(
        usage,
        x="pitch_label",
        y="pct",
        color="batter_hand",
        barmode="group",
        color_discrete_sequence=["#8B2C2C", "#1F3A5F"],
        text=usage["pct"].map("{:.1%}".format),
        labels={
            "pitch_label": "",
            "pct": "Usage %",
            "batter_hand": ""
        },
        title="Pitch Usage by Batter Handedness"
    )
    fig.update_layout(
        **EDITORIAL_LAYOUT,
        yaxis_tickformat=".0%",
        legend_title=""
    )
    fig.update_traces(textposition="outside", textfont_size=10)
    return fig


def plot_whiff_by_hand(df):
    df = df.copy()
    df["is_whiff"] = df["description"].isin([
        "swinging_strike", "swinging_strike_blocked", "foul_tip"
    ])
    df["is_swing"] = df["description"].isin([
        "swinging_strike", "swinging_strike_blocked", "foul_tip",
        "foul", "hit_into_play"
    ])

    summary = (
        df.groupby(["batter_hand", "pitch_label"])
        .agg(whiffs=("is_whiff", "sum"), swings=("is_swing", "sum"))
        .reset_index()
    )
    summary["whiff_pct"] = summary["whiffs"] / summary["swings"].replace(0, 1)

    fig = px.bar(
        summary,
        x="pitch_label",
        y="whiff_pct",
        color="batter_hand",
        barmode="group",
        color_discrete_sequence=["#8B2C2C", "#1F3A5F"],
        text=summary["whiff_pct"].map("{:.1%}".format),
        labels={
            "pitch_label": "",
            "whiff_pct": "Whiff %",
            "batter_hand": ""
        },
        title="Whiff Rate by Batter Handedness"
    )
    fig.update_layout(
        **EDITORIAL_LAYOUT,
        yaxis_tickformat=".0%",
        legend_title=""
    )
    fig.update_traces(textposition="outside", textfont_size=10)
    return fig

def plot_location_heatmap(df, count_filter="All"):
    df = df.copy()
    df = df.dropna(subset=["plate_x", "plate_z"])

    if count_filter != "All":
        df = df[df["count_str"] == count_filter]

    if df.empty:
        return None

    pitches = sorted(df["pitch_label"].unique())
    n = len(pitches)
    cols = min(n, 4)
    rows = (n + cols - 1) // cols

    fig = make_subplots(
        rows=rows, cols=cols,
        subplot_titles=pitches,
        horizontal_spacing=0.06,
        vertical_spacing=0.10
    )

    SZ_LEFT, SZ_RIGHT = -0.83, 0.83
    SZ_BOT, SZ_TOP    = 1.5, 3.5

    for i, pitch in enumerate(pitches):
        r = i // cols + 1
        c = i % cols + 1
        sub = df[df["pitch_label"] == pitch]

        fig.add_trace(
            go.Histogram2dContour(
                x=sub["plate_x"],
                y=sub["plate_z"],
                colorscale=[
                    [0.0,  "#F5F1E8"],
                    [0.15, "#F0D8B8"],
                    [0.35, "#E8A87C"],
                    [0.55, "#D9534F"],
                    [0.75, "#A52828"],
                    [1.0,  "#6B1414"]
                ],
                showscale=False,
                ncontours=15,
                contours=dict(coloring="fill", showlines=False),
                line=dict(width=0)
            ),
            row=r, col=c
        )

        fig.add_shape(
            type="rect",
            x0=SZ_LEFT, x1=SZ_RIGHT,
            y0=SZ_BOT, y1=SZ_TOP,
            line=dict(color="#2B2B2B", width=2),
            fillcolor="rgba(0,0,0,0)",
            row=r, col=c
        )

        fig.update_xaxes(
            range=[-2, 2], showgrid=False, zeroline=False,
            showticklabels=False, row=r, col=c
        )
        fig.update_yaxes(
            range=[0.5, 4.5], showgrid=False, zeroline=False,
            showticklabels=False, scaleanchor=f"x{i+1 if i > 0 else ''}",
            scaleratio=1, row=r, col=c
        )

    fig.update_layout(
        **EDITORIAL_LAYOUT,
        height=300 * rows,
        showlegend=False
    )
    fig.update_layout(
        title=dict(
            text=f"Pitch Locations — Catcher's View ({count_filter})",
            font=dict(family="Playfair Display, Georgia, serif", size=20, color="#2B2B2B"),
            x=0,
            xanchor="left"
        )
    )
    return fig