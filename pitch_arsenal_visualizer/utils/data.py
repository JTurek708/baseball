import pybaseball
import pandas as pd

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


