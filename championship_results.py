import streamlit as st
import pandas as pd
import sqlite3
from championship_utils import save_final_results, get_final_results

def get_championship_bets():
    """Retorna DataFrame com todas as apostas do campeonato"""
    try:
        conn = sqlite3.connect("championship.db")
        df = pd.read_sql_query("SELECT * FROM championship_bets", conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Erro ao buscar apostas do campeonato: {str(e)}")
        return pd.DataFrame(columns=["usuario_id", "campeao", "vice", "equipe", "data_aposta"])

def main():
    if st.session_state.get("user_role", "").strip().lower() != "master":
        st.error("Acesso restrito ao Master.")
        return

    st.title("🏆 Atualizar Resultado Final do Campeonato")

    pilotos = [
        "Pierre Gasly", "Jack Doohan", "Fernando Alonso", "Lance Stroll",
        "Charles Leclerc", "Lewis Hamilton", "Esteban Ocon", "Oliver Bearman",
        "Lando Norris", "Oscar Piastri", "Kimi Antonelli", "George Russell",
        "Liam Lawson", "Isack Hadjar", "Max Verstappen", "Yuki Tsunoda",
        "Nico Hulkenberg", "Gabriel Bortoleto", "Alex Albon", "Carlos Sainz"
    ]
    equipes = [
        "Red Bull", "Mercedes", "Ferrari", "McLaren", "Alpine",
        "Aston Martin", "Haas", "Racing Bulls", "Sauber", "Williams"
    ]

    with st.form("final_results_form"):
        campeao = st.selectbox("Piloto Campeão", pilotos)
        vices_possiveis = [p for p in pilotos if p != campeao]
        vice = st.selectbox("Piloto Vice", vices_possiveis)
        equipe = st.selectbox("Equipe Campeã", equipes)
        submitted = st.form_submit_button("Salvar Resultado")
        if submitted:
            save_final_results(campeao, vice, equipe)
            st.success("Resultado oficial atualizado!")

    resultado = get_final_results()
    st.subheader("Resultado Atual Armazenado")
    if resultado:
        st.markdown(f"""
        **Campeão:** {resultado['champion']}  
        **Vice:** {resultado['vice']}  
        **Equipe Campeã:** {resultado['team']}
        """)
    else:
        st.info("Nenhum resultado registrado ainda.")

    st.title("📊 Todas as Apostas dos Participantes (Campeonato)")
    bets_df = get_championship_bets()
    if bets_df.empty:
        st.info("Nenhuma aposta de campeonato registrada ainda.")
    else:
        # Renomeia as colunas para exibição amigável
        bets_df = bets_df.rename(columns={
            "usuario_id": "Usuário",
            "campeao": "Campeão",
            "vice": "Vice",
            "equipe": "Equipe",
            "data_aposta": "Data da Aposta"
        })
        st.dataframe(bets_df, use_container_width=True)
