import streamlit as st
import pandas as pd
from services.championship_service import (
    save_final_results,
    get_final_results,
    get_championship_bets_df,
    calcular_pontuacao_campeonato
)
from db.db_utils import get_usuarios_df

def main():
    st.title("🏆 Resultado Oficial do Campeonato")

    # Apenas admin ou master pode alterar o resultado oficial
    perfil = st.session_state.get("user_role", "participante")
    is_admin = perfil in ("admin", "master")

    # Busca resultado atual, se houver
    temporada = 2025  # Ajuste para parametrização futura, se necessário
    resultado_atual = get_final_results(temporada)

    st.header("📢 Resultado Oficial (Pilotos e Equipes)")
    if resultado_atual:
        st.success(
            f"**Campeão:** {resultado_atual['champion']}  \n"
            f"**Vice:** {resultado_atual['vice']}  \n"
            f"**Equipe Campeã:** {resultado_atual['team']}"
        )
    else:
        st.info("Nenhum resultado oficial cadastrado ainda.")

    # Se admin, exibe formulário para registrar ou atualizar o resultado
    if is_admin:
        st.markdown("### Cadastrar/Atualizar Resultado Oficial")
        apostas_df = get_championship_bets_df()
        pilotos = sorted(set(apostas_df["champion"].tolist() + apostas_df["vice"].tolist()))
        equipes = sorted(apostas_df["team"].unique())

        with st.form("form_resultado_campeonato"):
            champion = st.selectbox("Piloto Campeão", pilotos, index=pilotos.index(resultado_atual['champion']) if resultado_atual else 0)
            vice = st.selectbox("Piloto Vice", pilotos, index=pilotos.index(resultado_atual['vice']) if resultado_atual else 0)
            team = st.selectbox("Equipe Campeã", equipes, index=equipes.index(resultado_atual['team']) if resultado_atual else 0)
            submitted = st.form_submit_button("Salvar resultado oficial")

            if submitted:
                if champion == vice:
                    st.error("Campeão e Vice devem ser pilotos diferentes.")
                else:
                    salvo = save_final_results(champion, vice, team, temporada)
                    if salvo:
                        st.success("Resultado oficial do campeonato salvo!")
                    else:
                        st.error("Erro ao salvar resultado.")

    st.markdown("---")

    st.header("📑 Resumo das apostas dos participantes")
    apostas_df = get_championship_bets_df()
    usuarios_df = get_usuarios_df()
    if not apostas_df.empty:
        apostas_df = apostas_df.copy()
        apostas_df["user_nome"] = apostas_df["user_id"].apply(
            lambda uid: usuarios_df[usuarios_df["id"] == uid]["nome"].values[0]
            if uid in usuarios_df["id"].values else "Desconhecido"
        )
        apostas_df["Pontos Bônus"] = apostas_df["user_id"].apply(lambda uid: calcular_pontuacao_campeonato(uid, temporada))
        apostas_df = apostas_df[["user_nome", "champion", "vice", "team", "bet_time", "Pontos Bônus"]]
        apostas_df.columns = ["Participante", "Campeão", "Vice", "Equipe", "Data/Hora Aposta", "Pontos Bônus"]
        st.dataframe(apostas_df, use_container_width=True)
    else:
        st.info("Nenhuma aposta registrada pelos participantes.")

if __name__ == "__main__":
    main()
