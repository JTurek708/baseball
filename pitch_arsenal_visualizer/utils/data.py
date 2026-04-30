import pybaseball
import pandas as pd

import streamlit as st

@st.cache_data
def get_arsenal_data(mlbam_id, season):
    data = pybaseball.statcast_pitcher(
        start_dt=f"{season}-03-01",
        end_dt=f"{season}-11-01",
        player_id=mlbam_id
    )
    data = data[data["pitch_type"].notna()]
    data = data[~data["pitch_type"].isin(["IN", ""])]
    data["pitch_label"] = data["pitch_type"].map(PITCH_LABELS).fillna(data["pitch_type"])
    return data

pybaseball.cache.enable()

# Pitch labels
PITCH_LABELS = {
    "FF": "4-Seam FB",
    "SI": "Sinker",
    "FC": "Cutter",
    "SL": "Slider",
    "ST": "Sweeper",
    "CU": "Curveball",
    "KC": "Knuckle-Curve",
    "CH": "Changeup",
    "FS": "Splitter",
    "KN": "Knuckleball",
}

# Get pitcher id and name
def get_pitcher_id(last_name, first_name):
    lookup = pybaseball.playerid_lookup(last_name, first_name)
    lookup = lookup[lookup["key_mlbam"] > 0]
    if lookup.empty:
        return None
    return int(lookup.iloc[0]["key_mlbam"])

# get pitcher arsenal
def get_arsenal_data(mlbam_id, season):
    data = pybaseball.statcast_pitcher(
        start_dt=f"{season}-03-01",
        end_dt=f"{season}-11-01",
        player_id=mlbam_id
    )
    data = data[data["pitch_type"].notna()]
    data = data[~data["pitch_type"].isin(["IN", ""])]

    data["pitch_label"] = data["pitch_type"].map(PITCH_LABELS).fillna(data["pitch_type"])

    return data

# Whiff Rate
def get_whiff_rate(df):
    df = df.copy()
    df["is_whiff"] = df["description"].isin([
        "swinging_strike",
        "swinging_strike_blocked",
        "foul_tip"
    ])
    return (
        df.groupby("pitch_label")
        .agg(
            whiffs=("is_whiff", "sum"),
            swings=("is_whiff", "count")
        )
        .reset_index()
        .assign(whiff_rate=lambda x: x["whiffs"] / x["swings"])
    )

def label_pitcher_data(df, name):
    df = df.copy()
    df["pitcher_name"] = name
    return df

def get_arsenal_summary(df):
    df = df.copy()
    df["is_whiff"] = df["description"].isin([
        "swinging_strike",
        "swinging_strike_blocked",
        "foul_tip"
    ])
    df["is_swing"] = df["description"].isin([
        "swinging_strike",
        "swinging_strike_blocked",
        "foul_tip",
        "foul",
        "hit_into_play"
    ])

    summary = (
        df.groupby("pitch_label")
        .agg(
            count=("pitch_type", "count"),
            avg_velo=("release_speed", "mean"),
            max_velo=("release_speed", "max"),
            avg_spin=("release_spin_rate", "mean"),
            avg_hb=("pfx_x", "mean"),
            avg_ivb=("pfx_z", "mean"),
            swings=("is_swing", "sum"),
            whiffs=("is_whiff", "sum"),
        )
        .reset_index()
    )

    summary["usage_pct"] = summary["count"] / summary["count"].sum()
    summary["whiff_pct"] = summary["whiffs"] / summary["swings"].replace(0, 1)
    summary["avg_hb"] = summary["avg_hb"] * 12
    summary["avg_ivb"] = summary["avg_ivb"] * 12

    summary = summary[[
        "pitch_label", "count", "usage_pct",
        "avg_velo", "max_velo", "avg_spin",
        "avg_hb", "avg_ivb", "whiff_pct"
    ]].rename(columns={
        "pitch_label": "Pitch",
        "count": "Thrown",
        "usage_pct": "Usage",
        "avg_velo": "Avg Velo",
        "max_velo": "Max Velo",
        "avg_spin": "Avg Spin",
        "avg_hb": "H. Break",
        "avg_ivb": "V. Break",
        "whiff_pct": "Whiff%"
    })

    return summary.sort_values("Usage", ascending=False).reset_index(drop=True)

def get_comparison_summary(df):
    df = df.copy()
    df["is_whiff"] = df["description"].isin([
        "swinging_strike",
        "swinging_strike_blocked",
        "foul_tip"
    ])
    df["is_swing"] = df["description"].isin([
        "swinging_strike",
        "swinging_strike_blocked",
        "foul_tip",
        "foul",
        "hit_into_play"
    ])

    summary = (
        df.groupby(["pitcher_name", "pitch_label"])
        .agg(
            count=("pitch_type", "count"),
            avg_velo=("release_speed", "mean"),
            avg_spin=("release_spin_rate", "mean"),
            avg_hb=("pfx_x", "mean"),
            avg_ivb=("pfx_z", "mean"),
            swings=("is_swing", "sum"),
            whiffs=("is_whiff", "sum"),
        )
        .reset_index()
    )

    summary["usage_pct"] = summary.groupby("pitcher_name")["count"].transform(lambda x: x / x.sum())
    summary["whiff_pct"] = summary["whiffs"] / summary["swings"].replace(0, 1)
    summary["avg_hb"] = summary["avg_hb"] * 12
    summary["avg_ivb"] = summary["avg_ivb"] * 12

    summary = summary[[
        "pitcher_name", "pitch_label", "count", "usage_pct",
        "avg_velo", "avg_spin", "avg_hb", "avg_ivb", "whiff_pct"
    ]].rename(columns={
        "pitcher_name": "Pitcher",
        "pitch_label": "Pitch",
        "count": "Thrown",
        "usage_pct": "Usage",
        "avg_velo": "Avg Velo",
        "avg_spin": "Avg Spin",
        "avg_hb": "H. Break",
        "avg_ivb": "V. Break",
        "whiff_pct": "Whiff%"
    })

    return summary.sort_values(["Pitch", "Pitcher"]).reset_index(drop=True)


