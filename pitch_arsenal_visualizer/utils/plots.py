import plotly.express as px
import plotly.graph_objects as go
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

# Chart 1: Movement Profile
def plot_movement(df):
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

    fig = px.scatter(
        summary,
        x="pfx_x_in",
        y="pfx_z_in",
        color="pitch_label",
        size="count",
        text="pitch_label",
        color_discrete_map=PITCH_COLORS,
        labels={
            "pfx_x_in": "Horizontal Break (in.)",
            "pfx_z_in": "Induced Vertical Break (in.)",
            "pitch_label": "Pitch",
            "count": "# Thrown"
        },
        title="Pitch Movement Profile"
    )
    fig.add_hline(y=0, line_dash="dash", line_color="grey")
    fig.add_vline(x=0, line_dash="dash", line_color="grey")
    fig.update_traces(textposition="top center")
    fig.update_layout(template="plotly_dark")
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
        template="plotly_dark",
        showlegend=False
    )
    return fig