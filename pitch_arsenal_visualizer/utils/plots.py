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
        template="plotly_dark",
        barmode="stack",
        yaxis_tickformat=".0%",
        legend_title="Pitch"
    )
    fig.update_traces(textposition="inside", textfont_size=10)
    return fig