import streamlit as st
from utils.data import get_pitcher_id, get_arsenal_data
from utils.plots import plot_movement, plot_usage, plot_velo, plot_spin

st.set_page_config(page_title="Pitch Arsenal Visualizer", layout="wide")

st.title("Pitch Arsenal Visualizer")
st.markdown("Search any MLB pitcher to explore their pitch mix, movement, velocity, and spin.")

with st.sidebar:
    st.header("Search")
    first_name = st.text_input("First Name", placeholder="e.g. Paul")
    last_name  = st.text_input("Last Name",  placeholder="e.g. Skenes")
    season     = st.selectbox("Season", options=list(range(2026, 2014, -1)))
    search     = st.button("Load Arsenal", use_container_width=True)

if "data" not in st.session_state:
    st.session_state.data = None
if "pitcher_name" not in st.session_state:
    st.session_state.pitcher_name = ""

if search:
    if not first_name or not last_name:
        st.sidebar.error("Please enter both a first and last name.")
    else:
        with st.spinner(f"Loading {first_name} {last_name}'s {season} arsenal..."):
            pitcher_id = get_pitcher_id(last_name, first_name)
            if pitcher_id is None:
                st.sidebar.error("Pitcher not found. Check spelling and try again.")
            else:
                df = get_arsenal_data(pitcher_id, season)
                st.session_state.data = df
                st.session_state.pitcher_name = f"{first_name} {last_name}"

if st.session_state.data is not None:
    df = st.session_state.data
    all_pitches = sorted(df["pitch_label"].unique())

    with st.sidebar:
        st.markdown("---")
        st.subheader("Filter Pitches")
        selected = st.multiselect(
            "Show pitches",
            options=all_pitches,
            default=all_pitches
        )

    df_filtered = df[df["pitch_label"].isin(selected)]

    st.subheader(f"{st.session_state.pitcher_name} — {season}")

    col1, col2 = st.columns([3, 2])
    with col1:
        st.plotly_chart(plot_movement(df_filtered), use_container_width=True)
    with col2:
        st.plotly_chart(plot_usage(df_filtered), use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.plotly_chart(plot_velo(df_filtered), use_container_width=True)
    with col4:
        st.plotly_chart(plot_spin(df_filtered), use_container_width=True)

else:
    st.info("Search for a pitcher in the sidebar to get started.")