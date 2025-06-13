def main():
    import streamlit as st
    from data_utils import (
        get_current_season,
        get_current_driver_standings,
        get_current_constructor_standings,
        get_driver_points_by_race,
        get_qualifying_vs_race_delta,
        get_fastest_lap_times,
        get_pit_stop_data,
        get_distribuicao_fichas_participante,
        get_distribuicao_fichas_consolidada,
        get_apostas_11_colocado
        )
    # Page Title with current season
    season = get_current_season()
    st.title(f"🏎️ Formula 1 {season} Dashboard")
            
    # Section: Driver Standings
    st.subheader("🧑‍✈️ Campeonato de Pilotos")
    st.dataframe(get_current_driver_standings(), use_container_width=True)
            
    # Section: Constructor Standings
    st.subheader("🏭 Campeonato de Construtores")
    st.dataframe(get_current_constructor_standings(), use_container_width=True)
            
    # Section: Driver Points Over Races
    st.subheader("📈 Progressão de pontos dos pilotos ao longo das corridas")
    points_df = get_driver_points_by_race()
    st.dataframe(points_df, use_container_width=True)
    st.line_chart(points_df.drop(columns=["Race"]).set_index("Round"))
            
    # Section: Qualifying vs Race Position Delta
    st.subheader("🔄 Classificação vs Corrida (Última Prova)")
    st.dataframe(get_qualifying_vs_race_delta(), use_container_width=True)
            
    # Section: Fastest Laps
    st.subheader("⚡ Volta mais rápida (Última Prova)")
    st.dataframe(get_fastest_lap_times(), use_container_width=True)
            
    # Section: Pit Stop Summary
    st.subheader("🛑 Resumo dos Pit Stops (Última Prova)")
    st.dataframe(get_pit_stop_data(), use_container_width=True)
        
    # Nova Seção: Distribuição de Fichas do Participante
    st.subheader("🎯 Sua Distribuição de Fichas")
    distrib_participante = get_distribuicao_fichas_participante(st.session_state.get("user_id"))
    if not distrib_participante.empty:
        st.dataframe(
            distrib_participante.style.format({"Fichas": "{:.0f}"}),
            use_container_width=True
        )
    else:
        st.info("Nenhuma distribuição de fichas registrada.")
        
    # Nova Seção: Distribuição Consolidada de Fichas
    st.subheader("📊 Distribuição Consolidada de Fichas")
    dist_consolidada = get_distribuicao_fichas_consolidada()
    if not dist_consolidada.empty:
        st.dataframe(
            dist_consolidada.style.format({"Total Fichas": "{:.0f}", "% do Total": "{:.1%}"}),
            use_container_width=True
        )
        st.bar_chart(dist_consolidada.set_index("Piloto")["Total Fichas"])
    else:
        st.info("Nenhum dado disponível para exibir.")
        
    # Nova Seção: Apostas no 11º Colocado
    st.subheader("🔮 Apostas no 11º Colocado")
    apostas_11 = get_apostas_11_colocado()
    if not apostas_11.empty:
        st.dataframe(
            apostas_11.style.format({"Total Apostas": "{:.0f}", "% das Apostas": "{:.1%}"}),
            use_container_width=True
        )
        st.bar_chart(apostas_11.set_index("Piloto")["Total Apostas"])
    else:
        st.info("Nenhuma aposta no 11º colocado registrada.")
