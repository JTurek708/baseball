import streamlit as st
import pandas as pd
from utils.data import (
    get_pitcher_id, get_arsenal_data, label_pitcher_data,
    get_arsenal_summary, get_comparison_summary
)
from utils.plots import (
    plot_movement, plot_usage, plot_velo, plot_spin,
    plot_count_usage, plot_movement_comparison, plot_usage_comparison
)

st.set_page_config(page_title="Pitch Arsenal Visualizer", layout="wide")
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Lora:wght@400;500;600&family=IBM+Plex+Mono&display=swap');

    html, body, [class*="css"] {
        font-family: 'Lora', Georgia, serif;
        color: #2B2B2B;
    }

    h1 {
        font-family: 'Playfair Display', Georgia, serif !important;
        font-weight: 900 !important;
        font-size: 3rem !important;
        letter-spacing: -0.5px;
        border-bottom: 3px double #2B2B2B;
        padding-bottom: 0.5rem;
        margin-bottom: 0.5rem !important;
    }

    h2, h3 {
        font-family: 'Playfair Display', Georgia, serif !important;
        font-weight: 700 !important;
        color: #2B2B2B;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        border-bottom: 1px solid #C4B998;
    }

    .stTabs [data-baseweb="tab"] {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: #6B6B6B;
    }

    .stTabs [aria-selected="true"] {
        color: #8B2C2C !important;
        font-weight: 600;
    }

    .stButton > button {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        background-color: #8B2C2C;
        color: #F5F1E8;
        border: none;
        border-radius: 0;
        padding: 0.6rem 1rem;
    }

    .stButton > button:hover {
        background-color: #6B1F1F;
        color: #F5F1E8;
    }

    .block-container {
        padding-top: 2rem;
        max-width: 1300px;
    }

    section[data-testid="stSidebar"] {
        border-right: 1px solid #C4B998;
    }

    .stAlert {
        border-radius: 0;
        border-left: 4px solid #8B2C2C;
    }
</style>
""", unsafe_allow_html=True)

st.title("Pitch Arsenal Visualizer")
st.markdown("Search any MLB pitcher to explore their pitch mix, movement, velocity, and spin.")

if "data" not in st.session_state:
    st.session_state.data = None
if "pitcher_name" not in st.session_state:
    st.session_state.pitcher_name = ""
if "compare_data" not in st.session_state:
    st.session_state.compare_data = None

tab1, tab2 = st.tabs(["Single Pitcher", "Compare Pitchers"])

with tab1:
    with st.sidebar:
        st.header("Single Pitcher")
        first_name = st.text_input("First Name", placeholder="e.g. Paul", key="s_first")
        last_name  = st.text_input("Last Name",  placeholder="e.g. Skenes", key="s_last")
        season     = st.selectbox("Season", options=list(range(2026, 2014, -1)), key="s_season")
        search     = st.button("Load Arsenal", use_container_width=True, key="s_search")

    if search:
        if not first_name or not last_name:
            st.sidebar.error("Please enter both a first and last name.")
        else:
            with st.spinner(f"Loading {first_name} {last_name}'s {season} arsenal..."):
                pitcher_id = get_pitcher_id(last_name.strip(), first_name.strip())
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
                default=all_pitches,
                key="s_filter"
            )

        df_filtered = df[df["pitch_label"].isin(selected)]
        st.markdown(
            f"<h2 style='font-family:Playfair Display, Georgia, serif; font-style:italic; "
            f"color:#6B6B6B; font-weight:500; margin-top:1.5rem;'>"
            f"{st.session_state.pitcher_name} · {season}</h2>",
            unsafe_allow_html=True
        )

        summary = get_arsenal_summary(df_filtered)

        st.markdown(
            "<h3 style='font-family:Playfair Display, Georgia, serif; "
            "font-style:italic; color:#6B6B6B; font-weight:500; "
            "margin-top:1.5rem; margin-bottom:0.5rem;'>"
            "The Arsenal at a Glance</h3>",
            unsafe_allow_html=True
        )

        st.dataframe(
            summary.style.format({
                "Usage": "{:.1%}",
                "Avg Velo": "{:.1f}",
                "Max Velo": "{:.1f}",
                "Avg Spin": "{:,.0f}",
                "H. Break": "{:.1f}",
                "V. Break": "{:.1f}",
                "Whiff%": "{:.1%}"
            }),
            use_container_width=True,
            hide_index=True
        )

        col1, col2 = st.columns([3, 2])
        with col1:
            st.plotly_chart(plot_movement(df_filtered), use_container_width=True, key="s_movement")
        with col2:
            st.plotly_chart(plot_usage(df_filtered), use_container_width=True, key="s_usage")

        col3, col4 = st.columns(2)
        with col3:
            st.plotly_chart(plot_velo(df_filtered), use_container_width=True, key="s_velo")
        with col4:
            st.plotly_chart(plot_spin(df_filtered), use_container_width=True, key="s_spin")

        st.markdown("---")
        st.plotly_chart(plot_count_usage(df_filtered), use_container_width=True, key="s_count")

    else:
        st.info("Search for a pitcher in the sidebar to get started.")

with tab2:
    st.subheader("Compare Two Pitchers")

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("**Pitcher A**")
        a_first  = st.text_input("First Name", placeholder="e.g. Gerrit",  key="a_first")
        a_last   = st.text_input("Last Name",  placeholder="e.g. Cole",    key="a_last")
        a_season = st.selectbox("Season", options=list(range(2026, 2014, -1)), key="a_season")

    with col_b:
        st.markdown("**Pitcher B**")
        b_first  = st.text_input("First Name", placeholder="e.g. Paul",   key="b_first")
        b_last   = st.text_input("Last Name",  placeholder="e.g. Skenes", key="b_last")
        b_season = st.selectbox("Season", options=list(range(2026, 2014, -1)), key="b_season")

    compare = st.button("Compare", use_container_width=True, key="compare_btn")

    if compare:
        if not all([a_first, a_last, b_first, b_last]):
            st.error("Please fill in all four name fields.")
        else:
            with st.spinner("Loading both pitchers..."):
                id_a = get_pitcher_id(a_last.strip(), a_first.strip())
                id_b = get_pitcher_id(b_last.strip(), b_first.strip())

                if id_a is None:
                    st.error(f"Could not find {a_first} {a_last}. Check spelling.")
                elif id_b is None:
                    st.error(f"Could not find {b_first} {b_last}. Check spelling.")
                else:
                    df_a = label_pitcher_data(
                        get_arsenal_data(id_a, a_season),
                        f"{a_first} {a_last} ({a_season})"
                    )
                    df_b = label_pitcher_data(
                        get_arsenal_data(id_b, b_season),
                        f"{b_first} {b_last} ({b_season})"
                    )
                    st.session_state.compare_data = pd.concat([df_a, df_b], ignore_index=True)

    if st.session_state.compare_data is not None:
        df_compare = st.session_state.compare_data

        st.markdown(
            "<h3 style='font-family:Playfair Display, Georgia, serif; "
            "font-style:italic; color:#6B6B6B; font-weight:500; "
            "margin-top:1.5rem; margin-bottom:0.5rem;'>"
            "Side by Side</h3>",
            unsafe_allow_html=True
        )

        comparison_summary = get_comparison_summary(df_compare)

        st.dataframe(
            comparison_summary.style.format({
                "Usage": "{:.1%}",
                "Avg Velo": "{:.1f}",
                "Avg Spin": "{:,.0f}",
                "H. Break": "{:.1f}",
                "V. Break": "{:.1f}",
                "Whiff%": "{:.1%}"
            }),
            use_container_width=True,
            hide_index=True
        )

        col1, col2 = st.columns([3, 2])
        with col1:
            st.plotly_chart(plot_movement_comparison(df_compare), use_container_width=True, key="c_movement")
        with col2:
            st.plotly_chart(plot_usage_comparison(df_compare), use_container_width=True, key="c_usage")

    else:
        st.info("Enter two pitchers above and click Compare.")