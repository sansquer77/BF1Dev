import streamlit as st
from data_utils import (
    get_current_season,
    get_current_driver_standings,
    get_current_constructor_standings,
    get_driver_points_by_race,
    get_qualifying_vs_race_delta,
    get_fastest_lap_times,
    get_pit_stop_data
)
def main():
    st.title("Dash F1")
    
    # Page Title with current season
    season = get_current_season()
    st.title(f"🏎️ Formula 1 {season} Live Insights Dashboard")
    
    # Section: Driver Standings
    st.subheader("🧑‍✈️ Driver Standings")
    st.dataframe(get_current_driver_standings(), use_container_width=True)
    
    # Section: Constructor Standings
    st.subheader("🏭 Constructor Standings")
    st.dataframe(get_current_constructor_standings(), use_container_width=True)
    
    # Section: Driver Points Over Races
    st.subheader("📈 Driver Points Progression Over Races")
    points_df = get_driver_points_by_race()
    st.dataframe(points_df, use_container_width=True)
    st.line_chart(points_df.drop(columns=["Race"]).set_index("Round"))
    
    # Section: Qualifying vs Race Position Delta
    st.subheader("🔄 Qualifying vs Race Position (Last Race)")
    st.dataframe(get_qualifying_vs_race_delta(), use_container_width=True)
    
    # Section: Fastest Laps
    st.subheader("⚡ Fastest Lap Times (Last Race)")
    st.dataframe(get_fastest_lap_times(), use_container_width=True)
    
    # Section: Pit Stop Summary
    st.subheader("🛑 Pit Stop Summary (Last Race)")
    st.dataframe(get_pit_stop_data(), use_container_width=True)
